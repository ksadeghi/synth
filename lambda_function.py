import json
import csv
import io
import base64
import random
import string
import re
import zipfile
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
    elif method == "POST" and path == "/export-sql":
        return handle_export_sql(event)
    elif method == "POST" and path == "/table-counts":
        return handle_table_counts(event)
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


# ── Schema parsers ────────────────────────────────────────────────────────────

def handle_parse_schema(event):
    """Accept raw DDL text or JSON text, return normalised multi-table schema JSON."""
    try:
        body = event.get("body", "")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        # Try JSON first
        try:
            schema = json.loads(body)
            # Normalise: accept both legacy {"columns":[...]} and new {"tables":[...]}
            schema = normalise_schema(schema)
        except (json.JSONDecodeError, ValueError):
            schema = parse_ddl(body)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(schema),
        }
    except Exception as e:
        return error_response(400, f"Could not parse schema: {e}")


def normalise_schema(schema: dict) -> dict:
    """
    Accept either legacy single-table {"columns":[...]} or new {"tables":[...]}.
    Always returns {"tables": [{name, columns, foreign_keys}, ...]}.
    """
    if "tables" in schema:
        # Ensure every table has a foreign_keys list
        for tbl in schema["tables"]:
            tbl.setdefault("foreign_keys", [])
        return schema
    if "columns" in schema:
        return {"tables": [{"name": "table1", "columns": schema["columns"], "foreign_keys": []}]}
    raise ValueError("JSON must have 'tables' or 'columns' key")


def parse_ddl(ddl: str) -> dict:
    """
    Parse one or more CREATE TABLE statements into the multi-table schema format:
      {
        "tables": [
          {
            "name": "orders",
            "columns": [{"name": ..., "type": ...}, ...],
            "foreign_keys": [
              {"column": "customer_id", "ref_table": "customers", "ref_column": "id"}
            ]
          },
          ...
        ]
      }
    """
    # Find all CREATE TABLE blocks
    pattern = re.compile(
        r"CREATE\s+(?:EXTERNAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
        r"([`\"\[]?[\w.]+[`\"\]]?)\s*\((.+?)\)\s*"
        r"(?:PARTITIONED|LOCATION|TBLPROPERTIES|STORED|ROW|ENGINE|DEFAULT|;|$)",
        re.IGNORECASE | re.DOTALL,
    )

    tables = []
    for m in pattern.finditer(ddl):
        raw_name  = m.group(1).strip("`\"[]").split(".")[-1]  # strip schema prefix
        col_block = m.group(2)
        columns, foreign_keys = parse_paren_columns(col_block)
        tables.append({"name": raw_name, "columns": columns, "foreign_keys": foreign_keys})

    if not tables:
        raise ValueError("No CREATE TABLE statements found")

    return {"tables": tables}


def parse_paren_columns(col_block: str) -> tuple:
    """
    Parse a comma-separated column block.
    Returns (columns, foreign_keys).
    """
    columns      = []
    foreign_keys = []

    # Split on commas NOT inside nested parens
    depth   = 0
    current = []
    segments = []
    for ch in col_block:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            segments.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    last = "".join(current).strip()
    if last:
        segments.append(last)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        # FOREIGN KEY (col) REFERENCES table(col)
        fk_m = re.match(
            r"FOREIGN\s+KEY\s*\(\s*[`\"\[]?(\w+)[`\"\]]?\s*\)\s+"
            r"REFERENCES\s+[`\"\[]?(\w+)[`\"\]]?\s*\(\s*[`\"\[]?(\w+)[`\"\]]?\s*\)",
            seg, re.IGNORECASE
        )
        if fk_m:
            foreign_keys.append({
                "column":     fk_m.group(1),
                "ref_table":  fk_m.group(2),
                "ref_column": fk_m.group(3),
            })
            continue

        col = parse_single_column(seg)
        if col:
            columns.append(col)

    return columns, foreign_keys


def parse_single_column(col_def: str) -> dict | None:
    """Parse one column definition like 'col_name VARCHAR(255) NOT NULL DEFAULT x'."""
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
    name = name.strip("`\"[]")
    m    = re.match(r"([a-zA-Z_]+)\s*\(?(\d+)?\)?", dtype)
    base_type = m.group(1).lower() if m else dtype.lower()
    length    = int(m.group(2)) if m and m.group(2) else None
    col = {"name": name, "type": base_type}
    if length:
        col["length"] = length
    return col


# ── Generation ────────────────────────────────────────────────────────────────

def compute_table_counts(tables: list, base_n: int, fan_out: int) -> dict:
    """
    Return {table_name: row_count} for every table.

    Rules:
    - Root tables (no FK parents within the schema) get base_n rows.
    - A child table gets max(parent_counts) * fan_out rows, so every parent
      row is referenced at least fan_out times on average.
    - Capped at 10 000 rows per table.
    - Minimum 1 row per table regardless of fan_out.
    """
    name_set  = {t["name"] for t in tables}
    order     = topological_sort(tables)
    # Build parent-set per table (only parents that exist in this schema)
    parents: dict[str, set] = {}
    for tbl in tables:
        parents[tbl["name"]] = {
            fk["ref_table"]
            for fk in tbl.get("foreign_keys", [])
            if fk["ref_table"] in name_set
        }

    counts: dict[str, int] = {}
    for name in order:
        parent_set = parents[name]
        if not parent_set:
            counts[name] = base_n          # root table
        else:
            # Use the maximum parent count so every parent always has children
            max_parent = max(counts.get(p, base_n) for p in parent_set)
            counts[name] = min(max_parent * fan_out, 10_000)
        counts[name] = max(1, counts[name])

    return counts


def handle_table_counts(event):
    """Preview row counts without generating any data."""
    try:
        data    = parse_body(event)
        schema  = data.get("schema", {})
        base_n  = max(1, min(int(data.get("base_n",  10)), 1000))
        fan_out = max(1, min(int(data.get("fan_out",  3)),   20))

        if "columns" in schema and "tables" not in schema:
            schema = {"tables": [{"name": "table1", "columns": schema["columns"], "foreign_keys": []}]}

        tables = schema.get("tables", [])
        if not tables:
            return error_response(400, "No tables in schema")

        counts = compute_table_counts(tables, base_n, fan_out)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"counts": counts}),
        }
    except Exception as e:
        return error_response(400, str(e))


def handle_generate(event):
    try:
        data    = parse_body(event)
        schema  = data.get("schema", {})
        base_n  = max(1, min(int(data.get("num_records", 10)), 1000))
        fan_out = max(1, min(int(data.get("fan_out",     3)),   20))

        # Normalise to multi-table format
        if "columns" in schema and "tables" not in schema:
            schema = {"tables": [{"name": "table1", "columns": schema["columns"], "foreign_keys": []}]}

        tables = schema.get("tables", [])
        if not tables:
            return error_response(400, "Invalid schema: no tables found")

        counts = compute_table_counts(tables, base_n, fan_out)
        result = generate_all_tables(tables, counts)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }
    except Exception as e:
        return error_response(500, str(e))


def generate_all_tables(tables: list, counts: dict) -> dict:
    """
    Generate rows for all tables in topological order.
    counts: {table_name: row_count}
    Returns {"tables": [{"name": ..., "columns": [...], "rows": [...]}, ...]}.
    """
    order     = topological_sort(tables)
    generated: dict[str, list[dict]] = {}
    result_tables = []

    for tbl_name in order:
        tbl      = next(t for t in tables if t["name"] == tbl_name)
        columns  = tbl.get("columns", [])
        fk_list  = tbl.get("foreign_keys", [])
        fk_map   = {fk["column"]: (fk["ref_table"], fk["ref_column"]) for fk in fk_list}
        n        = counts.get(tbl_name, 10)

        # For child tables ensure every parent row appears at least once
        # by cycling through parent PKs before going random.
        parent_coverage = _build_parent_coverage(fk_map, generated, n)

        rows      = []
        row_dicts = []
        for i in range(n):
            row = generate_row(columns, fk_map, generated, parent_coverage, i)
            rows.append(row)
            row_dicts.append(dict(zip([c["name"] for c in columns], row)))

        generated[tbl_name] = row_dicts
        result_tables.append({
            "name":    tbl_name,
            "columns": [c["name"] for c in columns],
            "rows":    rows,
        })

    return {"tables": result_tables}


def _build_parent_coverage(fk_map: dict, generated: dict, child_n: int) -> dict:
    """
    For each FK column, build a list of parent PK values that must appear
    at least once in the child rows (round-robin coverage).
    Returns {col_name: [val, val, ...]} — only populated when parent rows exist
    and child_n >= parent row count.
    """
    coverage = {}
    for col_name, (ref_table, ref_col) in fk_map.items():
        parent_rows = generated.get(ref_table, [])
        if not parent_rows:
            continue
        # Shuffle parent PKs then tile to fill child_n slots
        pks = [r[ref_col] for r in parent_rows]
        random.shuffle(pks)
        # Repeat the list enough times to cover child_n rows
        tiled = []
        while len(tiled) < child_n:
            tiled.extend(pks)
        coverage[col_name] = tiled[:child_n]
    return coverage


def topological_sort(tables: list) -> list:
    """
    Return table names in an order where parent tables come before child tables.
    Falls back gracefully if a referenced table isn't in the schema.
    """
    name_set = {t["name"] for t in tables}
    deps: dict[str, set] = {}
    for tbl in tables:
        deps[tbl["name"]] = set()
        for fk in tbl.get("foreign_keys", []):
            ref = fk["ref_table"]
            if ref in name_set:
                deps[tbl["name"]].add(ref)

    ordered = []
    visited = set()

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        for dep in deps.get(name, []):
            visit(dep)
        ordered.append(name)

    for tbl in tables:
        visit(tbl["name"])

    return ordered


def generate_row(columns: list, fk_map: dict, generated: dict,
                 coverage: dict = None, row_idx: int = 0) -> list:
    """Generate one row, resolving FK columns from parent data.
    For the first len(parent_rows) child rows each parent PK is used exactly
    once (coverage); subsequent rows pick randomly.
    """
    row = []
    for col in columns:
        col_name = col["name"]

        # FK resolution
        if col_name in fk_map:
            ref_table, ref_col = fk_map[col_name]
            # Use pre-built coverage list if available
            if coverage and col_name in coverage:
                row.append(coverage[col_name][row_idx])
                continue
            parent_rows = generated.get(ref_table, [])
            if parent_rows:
                row.append(random.choice(parent_rows)[ref_col])
                continue
            # fall through to type generator if parent missing

        # Sample / pattern seeds
        samples = col.get("samples")
        if samples:
            entry = random.choice(samples)
            if _is_variable(entry):
                # Single token: {first_name}
                row.append(resolve_variable(entry))
            elif _is_template(entry):
                # Inline template: {first_name} {last_name}, {first_name}.{last_name}@co.com, etc.
                row.append(expand_template(entry))
            elif _is_pattern(entry):
                # Regex pattern: ORD-[A-Z]{2}[0-9]{4}
                row.append(rand_from_pattern(entry))
            else:
                # Plain literal: Alice
                row.append(coerce_sample(entry, col))
            continue

        # Default type-based generation
        gen = infer_generator(col)
        row.append(gen(col))

    return row


# ── Export ────────────────────────────────────────────────────────────────────

def handle_export(event):
    """
    Accepts {"tables": [{"name":..., "columns":[...], "rows":[...]}, ...]}.
    Returns a base64-encoded zip containing one CSV per table.
    """
    try:
        data   = parse_body(event)
        tables = data.get("tables", [])

        if not tables:
            return error_response(400, "No tables to export")

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for tbl in tables:
                csv_buf = io.StringIO()
                writer  = csv.writer(csv_buf)
                writer.writerow(tbl.get("columns", []))
                for row in tbl.get("rows", []):
                    writer.writerow(row)
                zf.writestr(f"{tbl['name']}.csv", csv_buf.getvalue())

        zip_bytes = buf.getvalue()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/zip",
                "Content-Disposition": 'attachment; filename="synthetic_data.zip"',
            },
            "body": base64.b64encode(zip_bytes).decode("utf-8"),
            "isBase64Encoded": True,
        }
    except Exception as e:
        return error_response(500, str(e))


def handle_export_sql(event):
    """
    Accepts {
      "schema": { "tables": [{name, columns:[{name,type,length?}], foreign_keys:[...]}] },
      "data":   { "tables": [{name, columns:[...], rows:[[...]]}] }
    }
    Returns a single .sql file with DROP TABLE, CREATE TABLE, and INSERT INTO statements.
    """
    try:
        body   = parse_body(event)
        schema = body.get("schema", {})
        data   = body.get("data",   {})

        schema_tables = {t["name"]: t for t in schema.get("tables", [])}
        data_tables   = data.get("tables", [])

        if not data_tables:
            return error_response(400, "No data to export")

        lines = []
        lines.append("-- Synthetic data export")
        lines.append(f"-- Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        lines.append("")

        # DROP TABLE in reverse order so children are dropped before parents
        lines.append("-- Drop existing tables (children first)")
        for tbl in reversed(data_tables):
            lines.append(f"DROP TABLE IF EXISTS {quote_ident(tbl['name'])};")
        lines.append("")

        # CREATE TABLE + INSERT per table
        for tbl_data in data_tables:
            tbl_name    = tbl_data["name"]
            col_names   = tbl_data.get("columns", [])
            rows        = tbl_data.get("rows", [])
            tbl_schema  = schema_tables.get(tbl_name, {})
            schema_cols = {c["name"]: c for c in tbl_schema.get("columns", [])}
            fk_list     = tbl_schema.get("foreign_keys", [])

            # CREATE TABLE
            lines.append(f"-- --------------------------------------------------------")
            lines.append(f"-- Table: {tbl_name}")
            lines.append(f"-- --------------------------------------------------------")
            lines.append(f"CREATE TABLE {quote_ident(tbl_name)} (")

            col_defs = []
            for col_name in col_names:
                sc       = schema_cols.get(col_name, {"name": col_name, "type": "varchar"})
                sql_type = to_sql_type(sc)
                is_pk    = col_name.lower() in (
                f"{tbl_name.lower()}_id",
                f"{tbl_name.lower().rstrip('s')}_id",
                "id",
            )
                pk_str   = " PRIMARY KEY" if is_pk else ""
                col_defs.append(f"    {quote_ident(col_name)} {sql_type}{pk_str}")

            for fk in fk_list:
                col_defs.append(
                    f"    FOREIGN KEY ({quote_ident(fk['column'])}) "
                    f"REFERENCES {quote_ident(fk['ref_table'])}({quote_ident(fk['ref_column'])})"
                )

            lines.append(",\n".join(col_defs))
            lines.append(");")
            lines.append("")

            # INSERT INTO
            if rows:
                col_list = ", ".join(quote_ident(c) for c in col_names)
                lines.append(f"INSERT INTO {quote_ident(tbl_name)} ({col_list}) VALUES")
                value_rows = []
                for row in rows:
                    vals = ", ".join(sql_literal(v) for v in row)
                    value_rows.append(f"    ({vals})")
                lines.append(",\n".join(value_rows) + ";")
                lines.append("")

        sql_text = "\n".join(lines)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Disposition": 'attachment; filename="synthetic_data.sql"',
            },
            "body": sql_text,
        }
    except Exception as e:
        return error_response(500, str(e))


def quote_ident(name: str) -> str:
    """Double-quote a SQL identifier."""
    return f'"{name}"'


def to_sql_type(col: dict) -> str:
    """Map a schema column dict to a standard SQL type string."""
    base   = col.get("type", "varchar").lower()
    length = col.get("length")
    mapping = {
        "serial":    "INTEGER",
        "int":       "INTEGER",      "integer":  "INTEGER",
        "bigint":    "BIGINT",       "smallint": "SMALLINT",
        "float":     "FLOAT",        "double":   "DOUBLE PRECISION",
        "real":      "REAL",
        "decimal":   "DECIMAL(18,2)","numeric":  "NUMERIC(18,2)",
        "bool":      "BOOLEAN",      "boolean":  "BOOLEAN",
        "date":      "DATE",
        "datetime":  "TIMESTAMP",    "timestamp":"TIMESTAMP",
        "text":      "TEXT",
        "uuid":      "VARCHAR(36)",
        "string":    "VARCHAR(255)",
        "email":     "VARCHAR(255)", "name":     "VARCHAR(255)",
        "fullname":  "VARCHAR(255)", "phone":    "VARCHAR(50)",
        "address":   "TEXT",
        "char":      f"CHAR({length})"    if length else "CHAR(1)",
        "varchar":   f"VARCHAR({length})" if length else "VARCHAR(255)",
    }
    return mapping.get(base, "VARCHAR(255)")


def sql_literal(value) -> str:
    """Render a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def error_response(status, message):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }


# ── Synthetic data generators ─────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# Real-world name data (sourced from US SSA top-200 baby names 2020-2025,
# and widely published global surname frequency lists — all public domain).
# ---------------------------------------------------------------------------
NAMES_DATA = {
    "first_male": [
        "Liam","Noah","Oliver","James","Elijah","William","Henry","Lucas","Theodore","Benjamin",
        "Mateo","Jack","Owen","Ethan","Aiden","Sebastian","Muhammad","Jackson","Mason","Asher",
        "Leo","Julian","Levi","Daniel","Michael","Logan","Alexander","Samuel","Ezra","Hudson",
        "Nathan","Gabriel","David","Ryan","Caleb","Anthony","Isaac","Christopher","Andrew","Joshua",
        "Lincoln","Cameron","Eli","Adrian","Nolan","Jaxon","Grayson","Santiago","Kai","Connor",
        "Dylan","Aaron","Charles","Dominic","Evan","Isaiah","Thomas","Jordan","Robert","Nicholas",
        "Wyatt","Hunter","Adam","Jason","Tyler","Jose","Kevin","Luke","Brian","Carter",
        "Austin","Landon","Gavin","Jonathan","Brayden","Colton","Carlos","Angel","Ayden","Cooper",
        "Lincoln","Miles","Josiah","Maxwell","Xavier","Jace","Ian","Bryson","Ryder","Harrison",
        "Parker","Vincent","Marcus","Cole","Easton","Nathaniel","Roman","Maverick","Sawyer","Damien",
    ],
    "first_female": [
        "Olivia","Emma","Charlotte","Amelia","Sophia","Mia","Isabella","Ava","Evelyn","Harper",
        "Luna","Camila","Sofia","Eleanor","Elizabeth","Violet","Scarlett","Emily","Hazel","Lily",
        "Gianna","Aurora","Penelope","Riley","Zoey","Nora","Lillian","Addison","Aubrey","Ellie",
        "Stella","Natalie","Zoe","Leah","Hannah","Layla","Brooklyn","Sofia","Anna","Victoria",
        "Isla","Grace","Maya","Chloe","Elena","Aria","Paisley","Savannah","Audrey","Claire",
        "Skylar","Lucy","Bella","Valentina","Nova","Genesis","Emilia","Willow","Samantha","Ruby",
        "Kinsley","Hailey","Eva","Madelyn","Delilah","Autumn","Alyssa","Naomi","Melanie","Serenity",
        "Abigail","Gabriella","Jade","Lydia","Aaliyah","Maria","Sophie","Reagan","Peyton","Alice",
        "Ariana","Eliana","Taylor","Isabelle","Caroline","Brooklyn","Quinn","Morgan","Kennedy","Vivian",
        "Mackenzie","Jasmine","Josephine","Faith","Alexandra","Ashley","Madison","Amber","Katherine","Diana",
    ],
    "last": [
        # English / American
        "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore",
        "Taylor","Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Young","Walker",
        "Hall","Allen","Wright","Scott","Torres","Nguyen","Hill","Flores","Green","Adams",
        "Nelson","Baker","Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell","Parker",
        "Evans","Edwards","Collins","Stewart","Sanchez","Morris","Rogers","Reed","Cook","Morgan",
        "Bell","Murphy","Bailey","Rivera","Cooper","Richardson","Cox","Howard","Ward","Peterson",
        "Gray","Ramirez","James","Watson","Brooks","Kelly","Sanders","Price","Bennett","Wood",
        "Barnes","Ross","Henderson","Coleman","Jenkins","Perry","Powell","Long","Patterson","Hughes",
        # European
        "Mueller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Schulz","Hoffmann",
        "Dupont","Leroy","Moreau","Laurent","Simon","Bernard","Martin","Robert","Richard","Petit",
        "Rossi","Ferrari","Esposito","Russo","Bianchi","Romano","Colombo","Ricci","Marino","Greco",
        "Garcia","Martinez","Lopez","Sanchez","Gonzalez","Rodriguez","Fernandez","Diaz","Torres","Ruiz",
        # Asian
        "Wang","Li","Zhang","Liu","Chen","Yang","Huang","Zhao","Wu","Zhou",
        "Kim","Lee","Park","Choi","Jeong","Kang","Cho","Yoon","Lim","Ha",
        "Tanaka","Sato","Suzuki","Watanabe","Ito","Yamamoto","Nakamura","Kobayashi","Kato","Abe",
        "Singh","Kumar","Sharma","Patel","Gupta","Verma","Shah","Mehta","Joshi","Nair",
        # Other
        "Silva","Santos","Oliveira","Souza","Pereira","Costa","Alves","Nascimento","Lima","Carvalho",
        "Ali","Hassan","Mohamed","Ahmed","Omar","Khan","Malik","Siddiqui","Chaudhry","Sheikh",
        "Okafor","Eze","Nwosu","Adeyemi","Abubakar","Musa","Ibrahim","Mohammed","Diallo","Traore",
    ],
    "email_domains": [
        "gmail.com","yahoo.com","outlook.com","hotmail.com","icloud.com",
        "mail.com","protonmail.com","aol.com","live.com","msn.com",
    ],
    "cities": [
        "New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia","San Antonio","San Diego",
        "Dallas","San Jose","Austin","Jacksonville","Fort Worth","Columbus","Charlotte","Indianapolis",
        "London","Manchester","Birmingham","Glasgow","Liverpool","Leeds","Edinburgh","Bristol",
        "Toronto","Montreal","Vancouver","Calgary","Ottawa","Edmonton",
        "Sydney","Melbourne","Brisbane","Perth","Adelaide",
        "Berlin","Hamburg","Munich","Frankfurt","Cologne","Stuttgart",
        "Paris","Marseille","Lyon","Toulouse","Nice","Nantes",
        "Tokyo","Osaka","Yokohama","Nagoya","Sapporo",
        "Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Kolkata",
        "Shanghai","Beijing","Shenzhen","Guangzhou","Chengdu",
        "Dubai","Abu Dhabi","Riyadh","Jeddah","Kuwait City",
        "Singapore","Kuala Lumpur","Bangkok","Jakarta","Manila",
        "São Paulo","Rio de Janeiro","Buenos Aires","Bogotá","Lima","Santiago",
        "Lagos","Nairobi","Johannesburg","Cairo","Casablanca","Accra",
    ],
    "countries": [
        "United States","United Kingdom","Canada","Australia","Germany","France","Italy","Spain",
        "Netherlands","Sweden","Norway","Denmark","Switzerland","Belgium","Austria","Portugal",
        "Japan","South Korea","China","India","Singapore","UAE","Saudi Arabia","Israel",
        "Brazil","Mexico","Argentina","Colombia","Chile","Peru",
        "South Africa","Nigeria","Kenya","Egypt","Morocco","Ghana",
        "New Zealand","Ireland","Finland","Poland","Czech Republic","Hungary","Romania",
    ],
    "companies": [
        "Acme Corp","Globex","Initech","Hooli","Pied Piper","Dunder Mifflin","Vandelay Industries",
        "Sterling Cooper","Bluth Company","Prestige Worldwide","Oceanic Airlines","Massive Dynamic",
        "Apex Technologies","Blue Horizon","Nexus Partners","Catalyst Group","Summit Solutions",
        "Vertex Systems","Pinnacle Ventures","Meridian Capital","Cobalt Digital","Argon Analytics",
        "Helix Biotech","Solaris Energy","Quantum Dynamics","Vortex Media","Stratos Finance",
        "Luminary Health","Atlas Consulting","Orion Logistics","Eclipse Software","Nova Retail",
        "Titan Manufacturing","Onyx Security","Ember Creative","Prism Data","Aegis Insurance",
        "Beacon Pharma","Cirrus Cloud","Denali Partners","Frontier Networks","Glacier Capital",
    ],
    "job_titles": [
        "Software Engineer","Senior Software Engineer","Staff Engineer","Principal Engineer",
        "Product Manager","Senior Product Manager","Director of Product","VP of Product",
        "Data Analyst","Data Scientist","Senior Data Scientist","ML Engineer",
        "DevOps Engineer","Site Reliability Engineer","Cloud Architect","Security Engineer",
        "UX Designer","UI Designer","Design Lead","Creative Director",
        "Marketing Manager","Growth Manager","Content Strategist","Brand Manager",
        "Sales Executive","Account Manager","Business Development Manager","Sales Director",
        "Financial Analyst","Senior Analyst","Finance Manager","CFO","Controller",
        "HR Manager","Talent Acquisition Specialist","People Operations Manager","CHRO",
        "Operations Manager","Project Manager","Program Manager","COO",
        "Customer Success Manager","Support Engineer","Technical Account Manager",
        "QA Engineer","Test Lead","Automation Engineer",
        "CEO","CTO","CIO","VP Engineering","VP Sales","VP Marketing",
    ],
    "streets": [
        "Main St","Oak Ave","Maple Dr","Cedar Ln","Pine Rd","Elm Blvd","Park Ave",
        "Washington Blvd","Lake Shore Dr","River Rd","Highland Ave","Sunset Blvd",
        "Willow Way","Birch Ct","Spruce St","Chestnut St","Walnut Ave","Magnolia Dr",
    ],
    "states": [
        "CA","TX","NY","FL","IL","PA","OH","GA","NC","MI",
        "WA","AZ","CO","TN","IN","MO","MD","WI","MN","SC",
    ],
}

# ── Variable substitution ──────────────────────────────────────────────────────
# Supported tokens: {first_name}, {last_name}, {full_name}, {male_name},
#   {female_name}, {email}, {username}, {city}, {country}, {company}, {job_title}

_VAR_RE      = re.compile(r'^\{([a-zA-Z]\w*)\}$')            # exactly one variable, nothing else
_TEMPLATE_RE = re.compile(r'\{([a-zA-Z]\w*)\}')              # {var} — must start with a letter (not a digit quantifier)


def _is_variable(s: str) -> bool:
    """True when the entire string is a single {variable} token."""
    return bool(_VAR_RE.match(s.strip()))


def _is_template(s: str) -> bool:
    """True when the string contains at least one {variable} placeholder."""
    return bool(_TEMPLATE_RE.search(s.strip()))


def expand_template(template: str) -> str:
    """
    Replace every {variable} placeholder in *template* with a resolved value.
    Unrecognised placeholders are left unchanged.
    Examples:
      '{first_name} {last_name}'  -> 'Olivia Garcia'
      '{first_name}.{last_name}@company.com' -> 'noah.patel@company.com'
      'EMP-{first_name}-[0-9]{4}' -> not a template call (contains regex too)
    """
    def _replace(m):
        token = '{' + m.group(1) + '}'
        return resolve_variable(token)
    return _TEMPLATE_RE.sub(_replace, template)


def resolve_variable(token: str) -> str:
    """Expand a {variable} token to a random real-world value."""
    key = _VAR_RE.match(token.strip()).group(1).lower()

    first_m  = lambda: random.choice(NAMES_DATA["first_male"])
    first_f  = lambda: random.choice(NAMES_DATA["first_female"])
    first_   = lambda: random.choice(NAMES_DATA["first_male"] + NAMES_DATA["first_female"])
    last_    = lambda: random.choice(NAMES_DATA["last"])

    if key in ("first_name", "firstname", "given_name"):
        return first_()
    if key in ("male_name", "male_first_name", "first_name_male"):
        return first_m()
    if key in ("female_name", "female_first_name", "first_name_female"):
        return first_f()
    if key in ("last_name", "lastname", "surname", "family_name"):
        return last_()
    if key in ("full_name", "fullname", "name"):
        return f"{first_()} {last_()}"
    if key in ("email", "email_address"):
        fn = first_().lower()
        ln = last_().lower().replace(" ", "")
        sep = random.choice([".", "_", ""])
        sfx = str(random.randint(1, 999)) if random.random() < 0.3 else ""
        dom = random.choice(NAMES_DATA["email_domains"])
        return f"{fn}{sep}{ln}{sfx}@{dom}"
    if key in ("username", "user_name", "login", "handle"):
        fn = first_().lower()
        ln = last_().lower().replace(" ", "")
        return f"{fn}{ln}{random.randint(1, 999)}"
    if key in ("city", "city_name"):
        return random.choice(NAMES_DATA["cities"])
    if key in ("country", "country_name"):
        return random.choice(NAMES_DATA["countries"])
    if key in ("company", "company_name", "employer", "organization"):
        return random.choice(NAMES_DATA["companies"])
    if key in ("job_title", "jobtitle", "title", "position", "role", "occupation"):
        return random.choice(NAMES_DATA["job_titles"])
    if key in ("street", "street_address"):
        return f"{random.randint(1, 9999)} {random.choice(NAMES_DATA['streets'])}"
    if key in ("state", "state_code"):
        return random.choice(NAMES_DATA["states"])

    # Unknown variable — return the token unchanged so it's visible
    return token


def rand_string(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def rand_int(col):
    return random.randint(col.get("min", 1), col.get("max", 10000))


def rand_float(col):
    return round(random.uniform(col.get("min", 0.0), col.get("max", 1000.0)), 2)


def rand_date(_col):
    start = datetime(2000, 1, 1)
    delta = datetime(2025, 12, 31) - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")


def rand_datetime(_col):
    start = datetime(2000, 1, 1)
    delta = int((datetime(2025, 12, 31) - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta))).strftime("%Y-%m-%d %H:%M:%S")


def rand_bool(_col):
    return random.choice([True, False])


def rand_email(_col):
    fn  = random.choice(NAMES_DATA["first_male"] + NAMES_DATA["first_female"]).lower()
    ln  = random.choice(NAMES_DATA["last"]).lower().replace(" ", "")
    dom = random.choice(NAMES_DATA["email_domains"])
    return f"{fn}.{ln}@{dom}"


def rand_name(_col):
    first = random.choice(NAMES_DATA["first_male"] + NAMES_DATA["first_female"])
    last  = random.choice(NAMES_DATA["last"])
    return f"{first} {last}"


def rand_phone(_col):
    return f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"


def rand_address(_col):
    street = f"{random.randint(1,9999)} {random.choice(NAMES_DATA['streets'])}"
    city   = random.choice(NAMES_DATA["cities"])
    state  = random.choice(NAMES_DATA["states"])
    return f"{street}, {city}, {state}"


def rand_uuid(_col):
    def h(n): return "".join(random.choices("0123456789abcdef", k=n))
    return f"{h(8)}-{h(4)}-4{h(3)}-{random.choice('89ab')}{h(3)}-{h(12)}"


TYPE_MAP = {
    "int":       rand_int,   "integer":  rand_int,
    "bigint":    rand_int,   "smallint": rand_int,   "serial": rand_int,
    "float":     rand_float, "double":   rand_float,
    "decimal":   rand_float, "numeric":  rand_float, "real":   rand_float,
    "bool":      rand_bool,  "boolean":  rand_bool,
    "date":      rand_date,
    "datetime":  rand_datetime, "timestamp": rand_datetime,
    "email":     rand_email, "name":     rand_name,  "fullname": rand_name,
    "phone":     rand_phone, "address":  rand_address,
    "uuid":      rand_uuid,
    "text":      lambda c: rand_string(random.randint(5, 20)),
    "varchar":   lambda c: rand_string(random.randint(1, max(1, min(c.get("length", 20), 20)))),
    "char":      lambda c: rand_string(max(1, c.get("length", 1))),
    "string":    lambda c: rand_string(random.randint(5, 20)),
}


def infer_generator(col):
    col_name  = col.get("name", "").lower()
    base_type = re.split(r"[\s(]", col.get("type", "string").lower())[0]

    if any(k in col_name for k in ("email", "e_mail")):       return rand_email
    if any(k in col_name for k in ("phone", "mobile", "tel")): return rand_phone
    if any(k in col_name for k in ("address", "street", "city")): return rand_address
    if any(k in col_name for k in ("name", "fullname", "first_name", "last_name")): return rand_name
    if any(k in col_name for k in ("uuid", "guid")):           return rand_uuid
    if any(k in col_name for k in ("date", "birthday", "dob", "created", "updated")):
        return rand_datetime if "time" in col_name else rand_date

    return TYPE_MAP.get(base_type, lambda c: rand_string(10))


# ── Regex-based value generator ───────────────────────────────────────────────

_REGEX_METACHAR = re.compile(r'[\\^$.|?*+(){\[\]]')


def _is_pattern(s: str) -> bool:
    return bool(_REGEX_METACHAR.search(s))


def rand_from_pattern(pattern: str) -> str:
    """Generate a random string matching the given regex-like pattern."""
    return _expand(pattern, 0, len(pattern))[0]


def _expand(pat: str, start: int, end: int) -> tuple:
    result = []
    i = start
    while i < end:
        ch = pat[i]

        if ch == '|':
            branches = _split_alternation(pat, start, end)
            chosen = random.choice(branches)
            return _expand(chosen, 0, len(chosen))[0], end

        if ch == '(':
            close = _find_close(pat, i, end, '(', ')')
            inner = pat[i + 1:close]
            i = close + 1
            count, i = _read_quantifier(pat, i, end)
            for _ in range(count):
                branches = _split_alternation(inner, 0, len(inner))
                chosen = random.choice(branches)
                result.append(_expand(chosen, 0, len(chosen))[0])
            continue

        if ch == '[':
            close = pat.index(']', i + 1)
            class_inner = pat[i + 1:close]
            i = close + 1
            count, i = _read_quantifier(pat, i, end)
            for _ in range(count):
                result.append(_rand_from_class(class_inner))
            continue

        if ch == '\\' and i + 1 < end:
            code = pat[i + 1]
            i += 2
            count, i = _read_quantifier(pat, i, end)
            for _ in range(count):
                result.append(_rand_escape(code))
            continue

        if ch == '.':
            i += 1
            count, i = _read_quantifier(pat, i, end)
            for _ in range(count):
                result.append(random.choice(string.ascii_letters + string.digits + ' _-.'))
            continue

        literal = ch
        i += 1
        count, i = _read_quantifier(pat, i, end)
        result.append(literal * count)

    return ''.join(result), end


def _read_quantifier(pat: str, i: int, end: int) -> tuple:
    if i >= end:
        return 1, i
    ch = pat[i]
    if ch == '?': return random.randint(0, 1), i + 1
    if ch == '*': return random.randint(0, 5),  i + 1
    if ch == '+': return random.randint(1, 5),  i + 1
    if ch == '{':
        close = pat.find('}', i + 1)
        if close == -1:
            return 1, i
        spec = pat[i + 1:close]
        if ',' in spec:
            parts = spec.split(',', 1)
            lo = int(parts[0]) if parts[0].strip() else 0
            hi = int(parts[1]) if parts[1].strip() else lo + 5
            count = random.randint(lo, min(hi, 20))
        else:
            count = min(int(spec), 20)
        return count, close + 1
    return 1, i


def _rand_from_class(inner: str) -> str:
    negate = inner.startswith('^')
    if negate:
        inner = inner[1:]
    chars = []
    j = 0
    while j < len(inner):
        if j + 2 < len(inner) and inner[j + 1] == '-':
            chars.extend(chr(c) for c in range(ord(inner[j]), ord(inner[j + 2]) + 1))
            j += 3
        else:
            chars.append(inner[j])
            j += 1
    if negate:
        pool = [c for c in (string.ascii_letters + string.digits + ' _-.') if c not in chars]
        return random.choice(pool) if pool else random.choice(string.ascii_letters)
    return random.choice(chars) if chars else ''


def _rand_escape(code: str) -> str:
    if code == 'd': return random.choice(string.digits)
    if code == 'D': return random.choice(string.ascii_letters + ' _')
    if code == 'w': return random.choice(string.ascii_letters + string.digits + '_')
    if code == 'W': return random.choice(' !@#$%^&*()')
    if code == 's': return random.choice(' \t')
    if code == 'S': return random.choice(string.ascii_letters + string.digits)
    return code


def _find_close(pat: str, open_pos: int, end: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    for k in range(open_pos, end):
        if pat[k] == open_ch:   depth += 1
        elif pat[k] == close_ch:
            depth -= 1
            if depth == 0: return k
    return end - 1


def _split_alternation(pat: str, start: int, end: int) -> list:
    branches  = []
    depth     = 0
    in_class  = False
    seg_start = start
    for k in range(start, end):
        c = pat[k]
        if   c == '[' and not in_class: in_class = True
        elif c == ']' and in_class:     in_class = False
        elif c == '(' and not in_class: depth += 1
        elif c == ')' and not in_class: depth -= 1
        elif c == '|' and depth == 0 and not in_class:
            branches.append(pat[seg_start:k])
            seg_start = k + 1
    branches.append(pat[seg_start:end])
    return branches


def coerce_sample(value: str, col: dict):
    base_type = re.split(r"[\s(]", col.get("type", "string").lower())[0]
    if base_type in ("int", "integer", "bigint", "smallint", "serial"):
        try: return int(value)
        except (ValueError, TypeError): return value
    if base_type in ("float", "double", "decimal", "numeric", "real"):
        try: return float(value)
        except (ValueError, TypeError): return value
    if base_type in ("bool", "boolean"):
        if value.lower() in ("true", "1", "yes"):  return True
        if value.lower() in ("false", "0", "no"):  return False
    return value
