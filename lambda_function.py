import json
import csv
import io
import base64
import random
import string
import re
from datetime import datetime, timedelta
from html_content import HTML_CONTENT


def lambda_handler(event, context):
    """Main Lambda handler - routes GET to UI, POST to processing."""
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("rawPath", "/")

    if method == "GET":
        return serve_html()
    elif method == "POST" and path == "/parse-schema":
        return handle_parse_schema(event)
    elif method == "POST" and path == "/generate":
        return handle_generate(event)
    elif method == "POST" and path == "/export":
        return handle_export(event)
    else:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Not found"}),
        }


def serve_html():
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": HTML_CONTENT,
    }


def parse_body(event):
    body = event.get("body", "{}")
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body)


def handle_generate(event):
    try:
        data = parse_body(event)
        schema = data.get("schema", {})
        num_records = int(data.get("num_records", 10))
        num_records = max(1, min(num_records, 1000))

        if not schema or "columns" not in schema:
            return error_response(400, "Invalid schema: expected {'columns': [...]}")

        columns = schema["columns"]
        rows = [generate_row(columns) for _ in range(num_records)]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"columns": [c["name"] for c in columns], "rows": rows}),
        }
    except Exception as e:
        return error_response(500, str(e))


def handle_export(event):
    try:
        data = parse_body(event)
        columns = data.get("columns", [])
        rows = data.get("rows", [])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)

        csv_content = output.getvalue()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/csv",
                "Content-Disposition": 'attachment; filename="synthetic_data.csv"',
            },
            "body": csv_content,
        }
    except Exception as e:
        return error_response(500, str(e))


def error_response(status, message):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }


# ── Schema parsers ───────────────────────────────────────────────────────────

def handle_parse_schema(event):
    """Accept raw DDL text or JSON text, return normalised schema JSON."""
    try:
        body = event.get("body", "")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        # Try JSON first, then DDL
        try:
            schema = json.loads(body)
            if "columns" not in schema:
                raise ValueError("Not a schema JSON")
        except (json.JSONDecodeError, ValueError):
            schema = parse_ddl(body)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(schema),
        }
    except Exception as e:
        return error_response(400, f"Could not parse schema: {e}")


def parse_ddl(ddl: str) -> dict:
    """
    Parse a CREATE TABLE DDL statement into {"columns": [{"name": ..., "type": ...}]}.

    Handles:
      - Standard SQL:  col_name data_type [(size)] [constraints]
      - Hive/Athena:   col_name data_type  (no parens around column list, no commas required)
      - Qualifed names: schema.table or db.schema.table
    """
    # Collapse whitespace and newlines
    ddl_clean = re.sub(r"\s+", " ", ddl.strip())

    # Extract column block between the first '(' and the matching ')'
    # For Hive-style DDL the columns are space-separated without a wrapping paren —
    # detect that case by checking if '(' appears before LOCATION/TBLPROPERTIES.
    hive_no_paren = re.search(
        r"CREATE\s+(?:EXTERNAL\s+)?TABLE\s+\S+\s+([a-zA-Z_].*?)(?:\s+(?:LOCATION|TBLPROPERTIES|STORED|ROW|FIELDS|PARTITIONED|CLUSTERED|COMMENT)\b)",
        ddl_clean, re.IGNORECASE
    )

    paren_match = re.search(
        r"CREATE\s+(?:EXTERNAL\s+)?TABLE\s+\S+\s*\((.+?)\)\s*(?:LOCATION|TBLPROPERTIES|STORED|ROW|$)",
        ddl_clean, re.IGNORECASE | re.DOTALL
    )

    if paren_match:
        col_block = paren_match.group(1)
        columns = parse_paren_columns(col_block)
    elif hive_no_paren:
        col_block = hive_no_paren.group(1)
        columns = parse_hive_columns(col_block)
    else:
        raise ValueError("Could not locate column definitions in DDL")

    if not columns:
        raise ValueError("No columns found in DDL")

    return {"columns": columns}


def parse_paren_columns(col_block: str) -> list:
    """Parse comma-separated 'name type [constraints]' inside parentheses."""
    columns = []
    # Split on commas that are NOT inside nested parens
    depth = 0
    current = []
    for ch in col_block:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            col_def = "".join(current).strip()
            if col_def:
                col = parse_single_column(col_def)
                if col:
                    columns.append(col)
            current = []
        else:
            current.append(ch)

    # Last column (no trailing comma)
    col_def = "".join(current).strip()
    if col_def:
        col = parse_single_column(col_def)
        if col:
            columns.append(col)

    return columns


def parse_hive_columns(col_block: str) -> list:
    """
    Parse Hive-style 'name type name type ...' where pairs are space-separated
    and there are no commas or wrapping parentheses.
    e.g.: property string comments string date_requested string expense float
    """
    tokens = col_block.strip().split()
    columns = []
    i = 0
    while i + 1 < len(tokens):
        name = tokens[i]
        dtype = tokens[i + 1]
        # Skip if looks like a keyword, not a real column
        if name.upper() in ("PRIMARY", "UNIQUE", "KEY", "INDEX", "CONSTRAINT",
                             "CHECK", "FOREIGN", "REFERENCES"):
            i += 1
            continue
        columns.append(normalise_column(name, dtype))
        i += 2
    return columns


def parse_single_column(col_def: str) -> dict | None:
    """Parse one column definition like 'col_name VARCHAR(255) NOT NULL DEFAULT x'."""
    # Skip table-level constraints
    if re.match(r"^\s*(PRIMARY|UNIQUE|KEY|INDEX|CONSTRAINT|CHECK|FOREIGN)\b", col_def, re.IGNORECASE):
        return None
    parts = col_def.split()
    if len(parts) < 2:
        return None
    name  = parts[0].strip("`\"[]")
    dtype = parts[1]
    return normalise_column(name, dtype)


def normalise_column(name: str, dtype: str) -> dict:
    """Strip size annotations and map to a clean column dict."""
    name  = name.strip("`\"[]")
    # Extract base type and optional length: VARCHAR(255) → varchar, 255
    m = re.match(r"([a-zA-Z_]+)\s*\(?(\d+)?\)?", dtype)
    base_type = m.group(1).lower() if m else dtype.lower()
    length    = int(m.group(2)) if m and m.group(2) else None

    col = {"name": name, "type": base_type}
    if length:
        col["length"] = length
    return col


# ── Synthetic data generators ────────────────────────────────────────────────

FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eva", "Frank", "Grace", "Henry",
               "Iris", "Jack", "Karen", "Leo", "Maria", "Nathan", "Olivia", "Paul"]
LAST_NAMES  = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
               "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson"]
DOMAINS     = ["example.com", "mail.com", "test.org", "sample.net", "demo.io"]
STREETS     = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm Blvd"]
CITIES      = ["Springfield", "Shelbyville", "Capital City", "Ogdenville", "Brockway"]
STATES      = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]


def rand_string(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def rand_int(col):
    lo = col.get("min", 1)
    hi = col.get("max", 10000)
    return random.randint(lo, hi)


def rand_float(col):
    lo = col.get("min", 0.0)
    hi = col.get("max", 1000.0)
    return round(random.uniform(lo, hi), 2)


def rand_date(col):
    start = datetime(2000, 1, 1)
    end   = datetime(2025, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")


def rand_datetime(col):
    start = datetime(2000, 1, 1)
    end   = datetime(2025, 12, 31)
    delta = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta))).strftime("%Y-%m-%d %H:%M:%S")


def rand_bool(_col):
    return random.choice([True, False])


def rand_email(col):
    first = random.choice(FIRST_NAMES).lower()
    last  = random.choice(LAST_NAMES).lower()
    return f"{first}.{last}@{random.choice(DOMAINS)}"


def rand_name(_col):
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def rand_phone(_col):
    return f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"


def rand_address(_col):
    return f"{random.randint(1,9999)} {random.choice(STREETS)}, {random.choice(CITIES)}, {random.choice(STATES)}"


def rand_uuid(_col):
    parts = [rand_hex(8), rand_hex(4), "4" + rand_hex(3),
             random.choice("89ab") + rand_hex(3), rand_hex(12)]
    return "-".join(parts)


def rand_hex(n):
    return "".join(random.choices("0123456789abcdef", k=n))


# Maps type keywords → generator function
TYPE_MAP = {
    "int":      rand_int,
    "integer":  rand_int,
    "bigint":   rand_int,
    "smallint": rand_int,
    "serial":   rand_int,
    "float":    rand_float,
    "double":   rand_float,
    "decimal":  rand_float,
    "numeric":  rand_float,
    "real":     rand_float,
    "bool":     rand_bool,
    "boolean":  rand_bool,
    "date":     rand_date,
    "datetime": rand_datetime,
    "timestamp":rand_datetime,
    "email":    rand_email,
    "name":     rand_name,
    "fullname": rand_name,
    "phone":    rand_phone,
    "address":  rand_address,
    "uuid":     rand_uuid,
    "text":     lambda col: rand_string(random.randint(5, 20)),
    "varchar":  lambda col: rand_string(random.randint(5, min(col.get("length", 20), 20))),
    "char":     lambda col: rand_string(col.get("length", 1)),
    "string":   lambda col: rand_string(random.randint(5, 20)),
}


def infer_generator(col):
    """Pick a generator based on column type and name hints."""
    col_name  = col.get("name", "").lower()
    col_type  = col.get("type", "string").lower().strip()

    # Strip size annotations like varchar(255) → varchar
    base_type = re.split(r"[\s(]", col_type)[0]

    # Name-based hints take priority
    if any(k in col_name for k in ("email", "e_mail")):
        return rand_email
    if any(k in col_name for k in ("phone", "mobile", "tel")):
        return rand_phone
    if any(k in col_name for k in ("address", "street", "city")):
        return rand_address
    if any(k in col_name for k in ("name", "fullname", "first_name", "last_name")):
        return rand_name
    if any(k in col_name for k in ("uuid", "guid")):
        return rand_uuid
    if any(k in col_name for k in ("date", "birthday", "dob", "created", "updated")):
        if "time" in col_name:
            return rand_datetime
        return rand_date

    return TYPE_MAP.get(base_type, lambda c: rand_string(10))


def generate_row(columns):
    row = []
    for col in columns:
        gen = infer_generator(col)
        row.append(gen(col))
    return row
