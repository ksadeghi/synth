"""Test DDL parsing and generation with the cashflow schema."""
import json, sys
sys.path.insert(0, ".")
from lambda_function import lambda_handler

DDL = """CREATE TABLE daferllc_mateenik.cashflow (property string,comments string,date_requested string,unit_number string,description string,date_paid string,expense float,workorder_id string,income float)LOCATION 's3://daferllc-mateenik-workorders/iceberg_data'TBLPROPERTIES ('table_type'='iceberg','write_compression'='SNAPPY','format'='PARQUET');"""

# ── Test /parse-schema ────────────────────────────────────────────────────────
event_parse = {
    "requestContext": {"http": {"method": "POST"}},
    "rawPath": "/parse-schema",
    "isBase64Encoded": False,
    "body": DDL,
}
resp = lambda_handler(event_parse, {})
assert resp["statusCode"] == 200, f"Parse failed: {resp['body']}"
schema = json.loads(resp["body"])
print("✓ /parse-schema →", len(schema["columns"]), "columns")
for c in schema["columns"]:
    print(f"   {c['name']:20s} {c['type']}")

# ── Test /generate with parsed schema ─────────────────────────────────────────
event_gen = {
    "requestContext": {"http": {"method": "POST"}},
    "rawPath": "/generate",
    "isBase64Encoded": False,
    "body": json.dumps({"schema": schema, "num_records": 3}),
}
resp = lambda_handler(event_gen, {})
assert resp["statusCode"] == 200, f"Generate failed: {resp['body']}"
data = json.loads(resp["body"])
print(f"\n✓ /generate → {len(data['rows'])} rows × {len(data['columns'])} columns")
print("  Columns:", data["columns"])
for row in data["rows"]:
    print("  Row:", row)

print("\nAll DDL tests passed ✓")
