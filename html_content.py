HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Synthetic Data Generator</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 2rem;
    }

    h1 {
      font-size: 1.75rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
      color: #f8fafc;
    }
    .subtitle { color: #94a3b8; margin-bottom: 2rem; font-size: 0.95rem; }

    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 0.75rem;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .card h2 { font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: #cbd5e1; }

    .form-row {
      display: flex;
      gap: 1rem;
      align-items: flex-end;
      flex-wrap: wrap;
    }

    .form-group { display: flex; flex-direction: column; gap: 0.4rem; }
    .form-group label { font-size: 0.85rem; color: #94a3b8; }

    input[type="number"], input[type="file"] {
      background: #0f172a;
      border: 1px solid #475569;
      border-radius: 0.5rem;
      color: #e2e8f0;
      padding: 0.55rem 0.85rem;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s;
    }
    input[type="number"] { width: 140px; }
    input[type="number"]:focus, input[type="file"]:focus { border-color: #6366f1; }
    input[type="file"] { cursor: pointer; padding: 0.45rem 0.75rem; }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.6rem 1.25rem;
      border: none;
      border-radius: 0.5rem;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
    }
    .btn:active { transform: scale(0.97); }
    .btn:disabled { opacity: 0.45; cursor: not-allowed; }

    .btn-primary { background: #6366f1; color: #fff; }
    .btn-primary:hover:not(:disabled) { background: #4f46e5; }
    .btn-success { background: #22c55e; color: #fff; }
    .btn-success:hover:not(:disabled) { background: #16a34a; }

    .schema-preview {
      margin-top: 1rem;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 0.5rem;
      padding: 0.75rem 1rem;
      font-size: 0.8rem;
      color: #94a3b8;
      max-height: 160px;
      overflow-y: auto;
      display: none;
    }
    .schema-preview.show { display: block; }
    .schema-tag {
      display: inline-block;
      background: #1e3a5f;
      border: 1px solid #2563eb;
      border-radius: 0.3rem;
      padding: 0.15rem 0.5rem;
      margin: 0.2rem;
      font-size: 0.78rem;
      color: #93c5fd;
    }

    .alert {
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      font-size: 0.875rem;
      margin-bottom: 1rem;
      display: none;
    }
    .alert.show { display: block; }
    .alert-error   { background: #450a0a; border: 1px solid #b91c1c; color: #fca5a5; }
    .alert-success { background: #052e16; border: 1px solid #15803d; color: #86efac; }

    .spinner {
      display: none;
      width: 16px; height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }
    .spinner.show { display: inline-block; }
    @keyframes spin { to { transform: rotate(360deg); } }

    .table-wrapper {
      overflow-x: auto;
      border-radius: 0.5rem;
      border: 1px solid #334155;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    thead { background: #0f172a; position: sticky; top: 0; z-index: 1; }
    thead th {
      padding: 0.65rem 1rem;
      text-align: left;
      font-weight: 600;
      color: #94a3b8;
      border-bottom: 1px solid #334155;
      white-space: nowrap;
    }
    tbody tr { border-bottom: 1px solid #1e293b; transition: background 0.1s; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: #1e293b; }
    tbody td {
      padding: 0.55rem 1rem;
      color: #e2e8f0;
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .results-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .results-meta { font-size: 0.85rem; color: #64748b; }

    .empty-state {
      text-align: center;
      padding: 3rem;
      color: #475569;
    }
    .empty-state .icon { font-size: 3rem; margin-bottom: 0.75rem; }
    .empty-state p { font-size: 0.9rem; }

    #resultsSection { display: none; }
    #resultsSection.show { display: block; }
  </style>
</head>
<body>

<h1>⚡ Synthetic Data Generator</h1>
<p class="subtitle">Upload your database schema, set the record count, and generate realistic synthetic data instantly.</p>

<div id="alertBox" class="alert"></div>

<div class="card">
  <h2>Configuration</h2>
  <div class="form-row">
    <div class="form-group">
      <label for="schemaFile">Database Schema (.json, .sql, .ddl)</label>
      <input type="file" id="schemaFile" accept=".json,.sql,.ddl,.txt" />
    </div>
    <div class="form-group">
      <label for="numRecords">Number of Records</label>
      <input type="number" id="numRecords" value="10" min="1" max="1000" />
    </div>
    <button class="btn btn-primary" id="generateBtn" onclick="generate()">
      <span class="spinner" id="spinner"></span>
      <span id="generateLabel">Generate Data</span>
    </button>
  </div>
  <div class="schema-preview" id="schemaPreview"></div>
</div>

<div id="resultsSection">
  <div class="card">
    <div class="results-header">
      <h2>Generated Data</h2>
      <div style="display:flex;align-items:center;gap:1rem;">
        <span class="results-meta" id="resultsMeta"></span>
        <button class="btn btn-success" id="exportBtn" onclick="exportCSV()">
          ⬇ Export CSV
        </button>
      </div>
    </div>
    <div class="table-wrapper">
      <table id="dataTable">
        <thead id="tableHead"></thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
  let currentSchema = null;
  let generatedData  = null;

  // ── Schema upload ──────────────────────────────────────────────────────────
  document.getElementById('schemaFile').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const text = await file.text();
    const isJson = file.name.endsWith('.json');

    // Try local JSON parse first (no round-trip needed)
    if (isJson) {
      try {
        currentSchema = JSON.parse(text);
        showSchemaPreview(currentSchema);
        showAlert('Schema loaded: ' + (currentSchema.columns || []).length + ' column(s) detected.', 'success');
        return;
      } catch(_) { /* fall through to server parser */ }
    }

    // Send raw text to /parse-schema for DDL or malformed JSON
    try {
      showAlert('Parsing schema…', 'success');
      const resp = await fetch('/parse-schema', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: text,
      });
      const result = await resp.json();
      if (!resp.ok) {
        showAlert('Parse error: ' + (result.error || 'Unknown error'), 'error');
        currentSchema = null;
        hideSchemaPreview();
        return;
      }
      currentSchema = result;
      showSchemaPreview(currentSchema);
      showAlert('Schema loaded: ' + (currentSchema.columns || []).length + ' column(s) detected from ' + file.name, 'success');
    } catch(err) {
      showAlert('Failed to parse schema: ' + err.message, 'error');
      currentSchema = null;
      hideSchemaPreview();
    }
  });

  function showSchemaPreview(schema) {
    const preview = document.getElementById('schemaPreview');
    const cols = schema.columns || [];
    preview.innerHTML = '<strong style="color:#cbd5e1;">Columns detected:</strong><br>' +
      cols.map(c => `<span class="schema-tag">${escapeHtml(c.name)} <em style="opacity:.7">${escapeHtml(c.type || 'string')}</em></span>`).join('');
    preview.classList.add('show');
  }

  function hideSchemaPreview() {
    document.getElementById('schemaPreview').classList.remove('show');
  }

  // ── Generate ───────────────────────────────────────────────────────────────
  async function generate() {
    if (!currentSchema) {
      showAlert('Please upload a schema file (.json, .sql, .ddl) first.', 'error');
      return;
    }

    const numRecords = parseInt(document.getElementById('numRecords').value, 10);
    if (isNaN(numRecords) || numRecords < 1 || numRecords > 1000) {
      showAlert('Number of records must be between 1 and 1000.', 'error');
      return;
    }

    setLoading(true);
    hideAlert();

    try {
      const resp = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema: currentSchema, num_records: numRecords }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        showAlert('Error: ' + (data.error || 'Unknown error'), 'error');
        return;
      }

      generatedData = data;
      renderTable(data);
      document.getElementById('resultsSection').classList.add('show');
      document.getElementById('resultsMeta').textContent =
        data.rows.length + ' row(s) × ' + data.columns.length + ' column(s)';

    } catch(err) {
      showAlert('Request failed: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  // ── Render table ───────────────────────────────────────────────────────────
  function renderTable(data) {
    const thead = document.getElementById('tableHead');
    const tbody = document.getElementById('tableBody');

    thead.innerHTML = '<tr>' + data.columns.map(c =>
      `<th title="${escapeHtml(c)}">${escapeHtml(c)}</th>`
    ).join('') + '</tr>';

    tbody.innerHTML = data.rows.map(row =>
      '<tr>' + row.map(cell =>
        `<td title="${escapeHtml(String(cell))}">${escapeHtml(String(cell))}</td>`
      ).join('') + '</tr>'
    ).join('');
  }

  // ── Export CSV ─────────────────────────────────────────────────────────────
  async function exportCSV() {
    if (!generatedData) return;

    try {
      const resp = await fetch('/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedData),
      });

      if (!resp.ok) {
        showAlert('Export failed.', 'error');
        return;
      }

      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'synthetic_data.csv';
      a.click();
      URL.revokeObjectURL(url);
    } catch(err) {
      showAlert('Export error: ' + err.message, 'error');
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function setLoading(loading) {
    const btn     = document.getElementById('generateBtn');
    const spinner = document.getElementById('spinner');
    const label   = document.getElementById('generateLabel');
    btn.disabled  = loading;
    spinner.classList.toggle('show', loading);
    label.textContent = loading ? 'Generating…' : 'Generate Data';
  }

  function showAlert(msg, type) {
    const box = document.getElementById('alertBox');
    box.textContent = msg;
    box.className = `alert alert-${type} show`;
  }

  function hideAlert() {
    document.getElementById('alertBox').classList.remove('show');
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
              .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
</script>
</body>
</html>"""
