# Synthetic Data Generator — AWS Lambda

A single Lambda function that serves both the UI and the API for generating synthetic data from a database schema.

## How it works

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the HTML single-page UI |
| `POST` | `/parse-schema` | Parses uploaded DDL or JSON → returns normalised schema |
| `POST` | `/generate` | Accepts schema + record count → returns JSON rows |
| `POST` | `/export` | Accepts generated data → returns ZIP of CSV files (one per table) |
| `POST` | `/export-sql` | Accepts schema + data → returns an executable SQL script |

Routing is driven by the Lambda **Function URL** (no API Gateway needed).

---

## Project structure

```
lambda_function.py        — Lambda handler + schema parsers + synthetic data generators
html_content.py           — Inline HTML/CSS/JS frontend (imported by handler)
example_schema.json       — Sample multi-table schema (e-commerce domain)
financial_schema.json     — Sample multi-table schema (financial domain)
synthetic_financial_data.sql — Pre-generated SQL script from financial_schema.json
```

---

## Schema format

### Multi-table JSON (recommended)

```json
{
  "tables": [
    {
      "name": "customers",
      "columns": [
        { "name": "customer_id", "type": "serial" },
        { "name": "email",       "type": "varchar", "length": 150 },
        { "name": "country",     "type": "varchar", "length": 3,
          "samples": ["US", "GB", "CA", "AU"] }
      ],
      "foreign_keys": []
    },
    {
      "name": "orders",
      "columns": [
        { "name": "order_id",    "type": "serial" },
        { "name": "customer_id", "type": "integer" },
        { "name": "total",       "type": "decimal", "min": 10, "max": 5000 }
      ],
      "foreign_keys": [
        { "column": "customer_id", "ref_table": "customers", "ref_column": "customer_id" }
      ]
    }
  ]
}
```

FK columns are resolved automatically — `orders.customer_id` values are always drawn from the generated `customers.customer_id` values, so referential integrity is guaranteed.

### Legacy single-table JSON

```json
{
  "columns": [
    { "name": "id",        "type": "serial" },
    { "name": "email",     "type": "varchar", "length": 150 },
    { "name": "age",       "type": "integer", "min": 18, "max": 80 },
    { "name": "is_active", "type": "boolean" }
  ]
}
```

### DDL upload

Upload a `.sql` or `.ddl` file with one or more `CREATE TABLE` statements. `FOREIGN KEY ... REFERENCES` constraints are parsed automatically. Both standard SQL and Hive/Athena DDL styles are supported.

### Supported column types

| Type | Notes |
|------|-------|
| `integer`, `int`, `bigint`, `smallint`, `serial` | Supports `min` / `max` |
| `float`, `double`, `decimal`, `numeric`, `real` | Supports `min` / `max` |
| `boolean`, `bool` | `true` / `false` |
| `date` | `YYYY-MM-DD` |
| `datetime`, `timestamp` | `YYYY-MM-DD HH:MM:SS` |
| `varchar`, `char` | Supports `length` |
| `text`, `string` | Random string |
| `email` | Also inferred when column name contains "email" |
| `name`, `fullname` | Also inferred from column name |
| `phone` | Also inferred from "phone" / "mobile" / "tel" |
| `address` | Also inferred from "address" / "street" / "city" |
| `uuid` | UUID v4 format |

### Sample value seeds

Any column can be seeded with comma-separated literals or regex patterns:

| Seed input | What gets generated |
|---|---|
| `Alice, Bob, Carol` | Randomly picks one literal per row |
| `[A-Z]{2}[0-9]{4}` | e.g. `XK8821`, `BT0042` |
| `TXN-[A-Z]{2}[0-9]{8}` | e.g. `TXN-KP00341829` |
| `VERIFIED, PENDING, REJECTED` | Picks one literal per row |
| `Alice, TXN-[0-9]{6}` | Mix of literals and patterns |

FK columns are disabled in the seed UI — they are always filled from the parent table.

---

## Export options

### ZIP of CSVs

One CSV file per table, suitable for bulk import into most databases and data tools.

### SQL Script

A single `.sql` file containing:
- `DROP TABLE IF EXISTS` statements in child-first order
- `CREATE TABLE` statements with inferred SQL types, `PRIMARY KEY` detection, and `FOREIGN KEY` constraints
- `INSERT INTO ... VALUES` for every generated row

This script runs directly against **PostgreSQL**, **MySQL**, **SQLite**, and most ANSI-SQL compatible databases.

> **Note:** The SQL script does **not** run against Amazon Athena. See the section below for Athena-specific instructions.

---

## Loading data into Amazon Athena

Athena is a serverless query engine that reads data from **S3**. It does not support `INSERT INTO` with literal values, `DROP TABLE`, `PRIMARY KEY`, or `FOREIGN KEY` constraints. The correct workflow is:

1. Export your generated data as a **ZIP of CSVs**
2. Upload each CSV to S3
3. Create an Athena external table pointing at the S3 location

### Step 1 — Export CSV and upload to S3

After generating data, click **Export ZIP (CSV per table)**. Extract the zip. You will have one CSV per table, e.g. `customers.csv`, `transactions.csv`.

Upload them to S3, keeping each table in its own prefix:

```bash
aws s3 cp customers.csv     s3://your-bucket/synthetic/customers/
aws s3 cp accounts.csv      s3://your-bucket/synthetic/accounts/
aws s3 cp transactions.csv  s3://your-bucket/synthetic/transactions/
# repeat for each table
```

### Step 2 — Create the Athena database

Run this once in the Athena query editor:

```sql
CREATE DATABASE IF NOT EXISTS synthetic_data;
```

### Step 3 — Create external tables

Run one `CREATE EXTERNAL TABLE` statement per table. The column types must match what the generator produced. Below is the complete DDL for the **financial schema** — adapt the S3 paths to your bucket.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.customers (
  customer_id   INT,
  full_name     STRING,
  email         STRING,
  phone         STRING,
  date_of_birth DATE,
  address       STRING,
  country_code  STRING,
  kyc_status    STRING,
  risk_rating   STRING,
  created_at    TIMESTAMP,
  is_active     BOOLEAN
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/customers/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.accounts (
  account_id      INT,
  customer_id     INT,
  account_number  STRING,
  account_type    STRING,
  currency        STRING,
  balance         DOUBLE,
  credit_limit    DOUBLE,
  interest_rate   DOUBLE,
  status          STRING,
  opened_at       TIMESTAMP
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/accounts/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.beneficiaries (
  beneficiary_id  INT,
  customer_id     INT,
  full_name       STRING,
  bank_name       STRING,
  account_number  STRING,
  routing_number  STRING,
  currency        STRING,
  country_code    STRING,
  is_verified     BOOLEAN,
  created_at      TIMESTAMP
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/beneficiaries/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.transactions (
  transaction_id    INT,
  account_id        INT,
  reference_number  STRING,
  transaction_type  STRING,
  amount            DOUBLE,
  currency          STRING,
  exchange_rate     DOUBLE,
  balance_after     DOUBLE,
  description       STRING,
  channel           STRING,
  status            STRING,
  created_at        TIMESTAMP
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/transactions/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.transfers (
  transfer_id      INT,
  from_account_id  INT,
  beneficiary_id   INT,
  reference_number STRING,
  amount           DOUBLE,
  currency         STRING,
  exchange_rate    DOUBLE,
  fee              DOUBLE,
  transfer_type    STRING,
  status           STRING,
  initiated_at     TIMESTAMP,
  completed_at     TIMESTAMP
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/transfers/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS synthetic_data.fraud_alerts (
  alert_id        INT,
  transaction_id  INT,
  account_id      INT,
  alert_type      STRING,
  severity        STRING,
  score           DOUBLE,
  status          STRING,
  reviewed_by     STRING,
  notes           STRING,
  created_at      TIMESTAMP,
  resolved_at     TIMESTAMP
)
ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://your-bucket/synthetic/fraud_alerts/'
TBLPROPERTIES ('skip.header.line.count'='1');
```

### Step 4 — Verify

```sql
SELECT * FROM synthetic_data.customers LIMIT 10;

-- Cross-table join example
SELECT
  c.full_name,
  c.kyc_status,
  t.reference_number,
  t.amount,
  t.status AS txn_status
FROM synthetic_data.transactions t
JOIN synthetic_data.accounts     a ON t.account_id  = a.account_id
JOIN synthetic_data.customers    c ON a.customer_id = c.customer_id
LIMIT 20;
```

### Alternative — use AWS Glue Crawler

Instead of writing `CREATE EXTERNAL TABLE` statements manually, you can point a **Glue Crawler** at `s3://your-bucket/synthetic/` and let it infer the schema automatically.

1. Go to **AWS Glue → Crawlers → Create crawler**
2. Set the data source to `s3://your-bucket/synthetic/`
3. Set the target database to `synthetic_data`
4. Run the crawler — it will create one table per CSV prefix
5. Query the tables immediately from Athena

> **Tip:** For production-scale queries, convert the CSVs to **Parquet** format first. Parquet gives significantly better query performance and lower cost in Athena. Use AWS Glue ETL or the Athena `CREATE TABLE AS SELECT` (CTAS) feature to do the conversion after the initial CSV load.

### TIMESTAMP / BOOLEAN caveats

Athena's CSV reader treats `TIMESTAMP` columns as strings unless you use the OpenCSVSerDe or convert the data. If you see parse errors on timestamp or boolean columns, use `STRING` for those columns in the external table definition and cast in your queries:

```sql
SELECT
  customer_id,
  CAST(created_at AS TIMESTAMP) AS created_at,
  CAST(is_active   AS BOOLEAN)  AS is_active
FROM synthetic_data.customers;
```

---

## Deploying the Lambda

1. Zip `lambda_function.py` and `html_content.py` into `lambda.zip`
2. Create a Lambda function (Python 3.11+, 256 MB memory, 30 s timeout)
3. Upload `lambda.zip`
4. Enable a **Function URL** (auth type: `NONE` for open access, or `AWS_IAM` for private)
5. Open the Function URL in your browser

To deploy perform these actions:

aws lambda create-function --function-name synthetic-data-generator --runtime python3.12 --role arn:aws:iam::417012743123:role/adt-lambda-multi-service-role --handler lambda_function.lambda_handler --zip-file fileb://lambda.zip --timeout 30

aws lambda create-function-url-config --function-name synthetic-data-generator --auth-type NONE --cors file://cors.json

aws lambda add-permission --function-name synthetic-data-generator --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal * --function-url-auth-type NONE

To redeploy updated function: 
aws lambda update-function-code --function-name synthetic-data-generator --zip-file fileb://lambda.zip