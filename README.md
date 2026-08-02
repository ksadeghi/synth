# Synthetic Data Generator — AWS Lambda

A single Lambda function that serves both the UI and the API for generating synthetic data from a database schema.

## How it works

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the HTML single-page UI |
| `POST` | `/generate` | Accepts schema + record count → returns JSON rows |
| `POST` | `/export` | Accepts columns + rows → returns CSV file |

Routing is driven by the Lambda **Function URL** (no API Gateway needed).

---

## Project structure

```
lambda_function.py   — Lambda handler + synthetic data generators
html_content.py      — Inline HTML/CSS/JS frontend (imported by handler)
example_schema.json  — Sample schema to test with
test_local.py        — Local smoke tests (no AWS required)
```

---

## Schema format

Upload a JSON file with this structure:

```json
{
  "columns": [
    { "name": "id",        "type": "serial" },
    { "name": "email",     "type": "varchar", "length": 150 },
    { "name": "age",       "type": "integer", "min": 18, "max": 80 },
    { "name": "salary",    "type": "decimal", "min": 30000, "max": 150000 },
    { "name": "is_active", "type": "boolean" },
    { "name": "created_at","type": "timestamp" }
  ]
}
```

### Supported types

| Type | Notes |
|------|-------|
| `integer`, `int`, `bigint`, `smallint`, `serial` | Supports `min`/`max` |
| `float`, `double`, `decimal`, `numeric`, `real` | Supports `min`/`max` |
| `boolean`, `bool` | `true`/`false` |
| `date` | `YYYY-MM-DD` |
| `datetime`, `timestamp` | `YYYY-MM-DD HH:MM:SS` |
| `varchar`, `char` | Supports `length` |
| `text`, `string` | Random string |
| `email` | Or any column whose name contains "email" |
| `name`, `fullname` | Or any column whose name contains "name" |
| `phone` | Or any column whose name contains "phone"/"mobile"/"tel" |
| `address` | Or any column whose name contains "address"/"street"/"city" |
| `uuid` | Standard UUID v4 format |

Column **name hints** take priority over the declared type (e.g. a `varchar` column named `email` will get a realistic email value).

---

## Deployment

### 1. Package the Lambda

```bash
zip lambda.zip lambda_function.py html_content.py
```

### 2. Create the Lambda

- Runtime: **Python 3.12**
- Handler: `lambda_function.lambda_handler`
- Memory: 128 MB is sufficient
- Timeout: 30 seconds

```bash
aws lambda create-function \
  --function-name synthetic-data-generator \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda.zip \
  --timeout 30
```

### 3. Enable Function URL

```bash
aws lambda create-function-url-config \
  --function-name synthetic-data-generator \
  --auth-type NONE \
  --cors '{
    "AllowOrigins": ["*"],
    "AllowMethods": ["GET","POST"],
    "AllowHeaders": ["content-type"]
  }'
```

> **Note:** `auth-type NONE` makes the URL public. For internal tools, use `AWS_IAM` and sign requests, or place a CloudFront distribution in front.

### 4. Open the URL

The function URL looks like:
```
https://<id>.lambda-url.<region>.on.aws/
```

Open it in a browser — the UI loads directly.

---

## Local testing

```bash
python test_local.py
```

No AWS credentials or network access needed.


To deploy perform these actions:
================================
aws lambda create-function --function-name synthetic-data-generator --runtime python3.12 --role arn:aws:iam::417012743123:role/adt-lambda-multi-service-role --handler lambda_function.lambda_handler --zip-file fileb://lambda.zip --timeout 30

aws lambda create-function-url-config --function-name synthetic-data-generator --auth-type NONE --cors '{"AllowOrigins":["*"],"AllowMethods":["GET","POST"],"AllowHeaders":["content-type"]}'

aws lambda add-permission --function-name synthetic-data-generator --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal * --function-url-auth-type NONE

To redeploy updated function:
aws lambda update-function-code --function-name synthetic-data-generator --zip-file fileb://lambda.zip

