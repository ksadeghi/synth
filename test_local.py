"""Quick local smoke test — no AWS needed."""
import json
import sys
sys.path.insert(0, ".")

from lambda_function import lambda_handler

# ── Test 1: GET → HTML ───────────────────────────────────────────────────────
event_get = {"requestContext": {"http": {"method": "GET"}}, "rawPath": "/"}
resp = lambda_handler(event_get, {})
assert resp["statusCode"] == 200
assert "<title>" in resp["body"]
print("✓ GET /  →  HTML served")

# ── Test 2: POST /generate ───────────────────────────────────────────────────
with open("example_schema.json") as f:
    schema = json.load(f)

event_gen = {
    "requestContext": {"http": {"method": "POST"}},
    "rawPath": "/generate",
    "isBase64Encoded": False,
    "body": json.dumps({"schema": schema, "num_records": 5}),
}
resp = lambda_handler(event_gen, {})
assert resp["statusCode"] == 200, resp["body"]
data = json.loads(resp["body"])
assert len(data["rows"]) == 5
assert len(data["columns"]) == len(schema["columns"])
print(f"✓ POST /generate  →  {len(data['rows'])} rows, {len(data['columns'])} columns")
print("  Sample row:", data["rows"][0])

# ── Test 3: POST /export ─────────────────────────────────────────────────────
event_exp = {
    "requestContext": {"http": {"method": "POST"}},
    "rawPath": "/export",
    "isBase64Encoded": False,
    "body": json.dumps(data),
}
resp = lambda_handler(event_exp, {})
assert resp["statusCode"] == 200
assert resp["headers"]["Content-Type"] == "text/csv"
lines = resp["body"].strip().splitlines()
assert len(lines) == 6  # header + 5 rows
print(f"✓ POST /export    →  CSV with {len(lines)-1} data row(s)")
print("  Header:", lines[0])

print("\nAll tests passed ✓")
