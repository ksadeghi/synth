HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Synthetic Data Generator</title>
  <style>
    /* ── Theme tokens ─────────────────────────────────────────────────────── */
    html[data-theme="dark"] {
      --bg:              #0f172a;   --bg-card:    #1e293b;
      --bg-input:        #0f172a;   --bg-thead:   #0f172a;
      --bg-row-hover:    #1e293b;   --bg-collapse:#0f172a;
      --bg-collapse-hov: #1a2540;   --bg-schema-row-hov: #1a2540;
      --border:          #334155;   --border-input:#475569;
      --text:            #e2e8f0;   --text-h1:   #f8fafc;
      --text-h2:         #cbd5e1;   --text-muted:#94a3b8;
      --text-dim:        #64748b;   --text-faint:#475569;
      --col-name:        #93c5fd;
      --fk-bg:#1e3a5f; --fk-border:#2563eb; --fk-color:#93c5fd;
      --badge-bg:#1e3a5f; --badge-border:#2563eb; --badge-color:#93c5fd;
      --badge-root-bg:#1a3a2a; --badge-root-border:#16a34a; --badge-root-color:#86efac;
      --alert-err-bg:#450a0a; --alert-err-border:#b91c1c; --alert-err-text:#fca5a5;
      --alert-ok-bg:#052e16;  --alert-ok-border:#15803d;  --alert-ok-text:#86efac;
      --toggle-track:#334155; --toggle-thumb:#94a3b8;
    }
    html[data-theme="light"] {
      --bg:              #f1f5f9;   --bg-card:    #ffffff;
      --bg-input:        #f8fafc;   --bg-thead:   #f1f5f9;
      --bg-row-hover:    #f1f5f9;   --bg-collapse:#f1f5f9;
      --bg-collapse-hov: #e2e8f0;   --bg-schema-row-hov: #f8fafc;
      --border:          #cbd5e1;   --border-input:#94a3b8;
      --text:            #1e293b;   --text-h1:   #0f172a;
      --text-h2:         #1e293b;   --text-muted:#475569;
      --text-dim:        #64748b;   --text-faint:#94a3b8;
      --col-name:        #2563eb;
      --fk-bg:#dbeafe; --fk-border:#3b82f6; --fk-color:#1d4ed8;
      --badge-bg:#dbeafe; --badge-border:#3b82f6; --badge-color:#1d4ed8;
      --badge-root-bg:#dcfce7; --badge-root-border:#16a34a; --badge-root-color:#15803d;
      --alert-err-bg:#fef2f2; --alert-err-border:#fca5a5; --alert-err-text:#b91c1c;
      --alert-ok-bg:#f0fdf4;  --alert-ok-border:#86efac;  --alert-ok-text:#15803d;
      --toggle-track:#6366f1; --toggle-thumb:#ffffff;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 2rem;
      transition: background 0.2s, color 0.2s;
    }

    /* ── Page header ── */
    .page-header {
      display: flex; align-items: flex-start; justify-content: space-between;
      margin-bottom: 2rem; gap: 1rem; flex-wrap: wrap;
    }
    h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem; color: var(--text-h1); }
    .subtitle { color: var(--text-muted); font-size: 0.95rem; }

    /* ── Theme toggle ── */
    .theme-toggle {
      display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0;
      font-size: 0.82rem; color: var(--text-dim);
      cursor: pointer; user-select: none; padding-top: 0.25rem;
    }
    .toggle-track {
      position: relative; width: 40px; height: 22px; border-radius: 999px;
      background: var(--toggle-track); transition: background 0.2s; flex-shrink: 0;
    }
    .toggle-thumb {
      position: absolute; top: 3px; left: 3px;
      width: 16px; height: 16px; border-radius: 50%;
      background: var(--toggle-thumb); transition: transform 0.2s;
    }
    html[data-theme="light"] .toggle-thumb { transform: translateX(18px); }

    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      transition: background 0.2s, border-color 0.2s;
    }
    .card h2 { font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-h2); }

    /* ── Form controls ── */
    .form-row { display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap; }
    .form-group { display: flex; flex-direction: column; gap: 0.4rem; }
    .form-group label { font-size: 0.85rem; color: var(--text-muted); }

    input[type="number"], input[type="file"] {
      background: var(--bg-input);
      border: 1px solid var(--border-input);
      border-radius: 0.5rem;
      color: var(--text);
      padding: 0.55rem 0.85rem;
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s, background 0.2s;
    }
    input[type="number"] { width: 140px; }
    input[type="number"]:focus, input[type="file"]:focus { border-color: #6366f1; }
    input[type="file"] { cursor: pointer; padding: 0.45rem 0.75rem; }

    /* ── Buttons ── */
    .btn {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.6rem 1.25rem;
      border: none; border-radius: 0.5rem;
      font-size: 0.9rem; font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
    }
    .btn:active { transform: scale(0.97); }
    .btn:disabled { opacity: 0.45; cursor: not-allowed; }
    .btn-primary { background: #6366f1; color: #fff; }
    .btn-primary:hover:not(:disabled) { background: #4f46e5; }
    .btn-success { background: #22c55e; color: #fff; }
    .btn-success:hover:not(:disabled) { background: #16a34a; }
    .btn-sql { background: #0ea5e9; color: #fff; }
    .btn-sql:hover:not(:disabled) { background: #0284c7; }

    /* ── Alerts ── */
    .alert { padding: 0.75rem 1rem; border-radius: 0.5rem; font-size: 0.875rem; margin-bottom: 1rem; display: none; }
    .alert.show { display: block; }
    .alert-error   { background: var(--alert-err-bg); border: 1px solid var(--alert-err-border); color: var(--alert-err-text); }
    .alert-success { background: var(--alert-ok-bg);  border: 1px solid var(--alert-ok-border);  color: var(--alert-ok-text); }

    /* ── Spinner ── */
    .spinner { display: none; width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.6s linear infinite; }
    .spinner.show { display: inline-block; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Tabs ── */
    .tabs { display: flex; gap: 0; border-bottom: 1px solid var(--border); margin-bottom: 1rem; flex-wrap: wrap; }
    .tab-btn {
      padding: 0.5rem 1.1rem;
      background: none; border: none;
      color: var(--text-dim); font-size: 0.85rem; font-weight: 500;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
      transition: color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }
    .tab-btn:hover { color: var(--text); }
    .tab-btn.active { color: #6366f1; border-bottom-color: #6366f1; }

    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    /* ── Schema table (per-table column list + samples) ── */
    .schema-preview { margin-top: 1rem; display: none; }
    .schema-preview.show { display: block; }

    .hint {
      font-size: 0.82rem; color: var(--text-dim); margin-bottom: 0.75rem; line-height: 1.6;
    }
    .hint code {
      color: var(--col-name); background: var(--bg-input);
      padding: 0.1rem 0.35rem; border-radius: 0.25rem;
    }

    .schema-tbl-wrap { overflow-x: auto; border-radius: 0.5rem; border: 1px solid var(--border); }
    .schema-tbl { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
    .schema-tbl thead { background: var(--bg-thead); }
    .schema-tbl thead th {
      padding: 0.5rem 0.9rem; text-align: left;
      font-weight: 600; color: var(--text-dim);
      border-bottom: 1px solid var(--border); white-space: nowrap;
    }
    .schema-tbl tbody tr { border-bottom: 1px solid var(--border); }
    .schema-tbl tbody tr:last-child { border-bottom: none; }
    .schema-tbl tbody tr:hover { background: var(--bg-schema-row-hov); }
    .schema-tbl tbody td { padding: 0.45rem 0.9rem; vertical-align: middle; }

    .col-name { font-weight: 600; color: var(--col-name); font-family: monospace; }
    .col-type { color: var(--text-muted); font-family: monospace; font-size: 0.78rem; }
    .fk-badge {
      display: inline-block;
      font-size: 0.7rem; font-weight: 600;
      background: var(--fk-bg); border: 1px solid var(--fk-border); color: var(--fk-color);
      border-radius: 0.25rem; padding: 0.1rem 0.4rem; margin-left: 0.4rem; white-space: nowrap;
    }

    .samples-input {
      width: 100%; min-width: 200px;
      background: var(--bg-input); border: 1px solid var(--border); border-radius: 0.4rem;
      color: var(--text); padding: 0.4rem 0.7rem; font-size: 0.82rem;
      outline: none; transition: border-color 0.2s;
    }
    .samples-input:focus { border-color: #6366f1; }
    .samples-input::placeholder { color: var(--text-faint); }
    .samples-input:disabled { opacity: 0.4; cursor: not-allowed; }

    /* ── Results ── */
    #resultsSection { display: none; }
    #resultsSection.show { display: block; }

    .results-header {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;
    }
    .results-meta { font-size: 0.85rem; color: var(--text-dim); }

    .data-tbl-wrap { overflow-x: auto; border-radius: 0.5rem; border: 1px solid var(--border); max-height: 420px; overflow-y: auto; }
    .data-tbl { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .data-tbl thead { background: var(--bg-thead); position: sticky; top: 0; z-index: 1; }
    .data-tbl thead th {
      padding: 0.65rem 1rem; text-align: left;
      font-weight: 600; color: var(--text-muted);
      border-bottom: 1px solid var(--border); white-space: nowrap;
      cursor: pointer;
    }
    .data-tbl thead th:hover { color: var(--text); }
    .data-tbl tbody tr { border-bottom: 1px solid var(--border); transition: background 0.1s; }
    .data-tbl tbody tr:last-child { border-bottom: none; }
    .data-tbl tbody tr:hover { background: var(--bg-row-hover); }
    .data-tbl tbody td {
      padding: 0.55rem 1rem; color: var(--text);
      max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }

    .empty-state { text-align: center; padding: 3rem; color: var(--text-faint); }

    /* ── Row-count preview badges ── */
    .count-badge {
      display: inline-block; font-size: 0.72rem; font-weight: 600;
      background: var(--badge-bg); border: 1px solid var(--badge-border); color: var(--badge-color);
      border-radius: 0.9rem; padding: 0.1rem 0.55rem; margin-left: 0.45rem;
      white-space: nowrap; vertical-align: middle;
    }
    .count-badge.root {
      background: var(--badge-root-bg); border-color: var(--badge-root-border); color: var(--badge-root-color);
    }

    .fanout-hint { margin-top: 0.6rem; font-size: 0.8rem; color: var(--text-dim); line-height: 1.5; }

    /* ── Collapsible schema preview ── */
    .collapse-toggle {
      display: flex; align-items: center; justify-content: space-between;
      cursor: pointer; user-select: none;
      margin-top: 1rem; padding: 0.5rem 0.75rem;
      background: var(--bg-collapse); border: 1px solid var(--border); border-radius: 0.5rem;
      font-size: 0.85rem; font-weight: 600; color: var(--text-muted);
      transition: background 0.15s;
    }
    .collapse-toggle:hover { background: var(--bg-collapse-hov); color: var(--text); }
    .collapse-toggle .arrow { font-size: 0.75rem; transition: transform 0.2s; display: inline-block; }
    .collapse-toggle.open .arrow { transform: rotate(180deg); }
    .collapse-body { overflow: hidden; }
    .collapse-body.hidden { display: none; }

    /* ── Search bar ── */
    .search-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem; }
    .search-input {
      flex: 1; background: var(--bg-input); border: 1px solid var(--border); border-radius: 0.4rem;
      color: var(--text); padding: 0.4rem 0.75rem; font-size: 0.83rem;
      outline: none; transition: border-color 0.2s;
    }
    .search-input:focus { border-color: #6366f1; }
    .search-input::placeholder { color: var(--text-faint); }
    .search-count { font-size: 0.78rem; color: var(--text-dim); white-space: nowrap; }

    /* ── Sortable column headers ── */
    .data-tbl thead th .sort-arrow {
      display: inline-block; margin-left: 0.3rem; font-size: 0.65rem; opacity: 0.35; transition: opacity 0.15s;
    }
    .data-tbl thead th.sort-asc  .sort-arrow,
    .data-tbl thead th.sort-desc .sort-arrow { opacity: 1; color: #6366f1; }
    .data-tbl thead th.sort-asc  .sort-arrow::after { content: ' ▲'; }
    .data-tbl thead th.sort-desc .sort-arrow::after { content: ' ▼'; }
    .data-tbl thead th:not(.sort-asc):not(.sort-desc) .sort-arrow::after { content: ' ⇅'; }
  </style>
</head>
<body>

<!-- ── Page header ───────────────────────────────────────────────────────── -->
<div class="page-header">
  <div>
    <h1>&#9889; Synthetic Data Generator</h1>
    <p class="subtitle">Upload a schema with one or more tables, configure sample seeds, and generate referentially consistent synthetic data.</p>
  </div>
  <label class="theme-toggle" title="Toggle light / dark mode" onclick="toggleTheme()">
    <span>&#9790;</span>
    <div class="toggle-track"><div class="toggle-thumb"></div></div>
    <span>&#9788;</span>
  </label>
</div>

<div id="alertBox" class="alert"></div>

<!-- ── Configuration card ─────────────────────────────────────────────────── -->
<div class="card">
  <h2>Configuration</h2>
  <div class="form-row">
    <div class="form-group">
      <label for="schemaFile">Schema file &mdash; .json, .sql, .ddl (single or multi-table)</label>
      <input type="file" id="schemaFile" accept=".json,.sql,.ddl,.txt" />
    </div>
    <div class="form-group">
      <label for="numRecords">Base rows <span style="color:#475569;font-weight:400">(root tables)</span></label>
      <input type="number" id="numRecords" value="10" min="1" max="1000"
             oninput="refreshCountBadges()" />
    </div>
    <div class="form-group">
      <label for="fanOut">Child fan-out <span style="color:#475569;font-weight:400">(× per FK level)</span></label>
      <input type="number" id="fanOut" value="3" min="1" max="20"
             oninput="refreshCountBadges()" />
    </div>
    <button class="btn btn-primary" id="generateBtn" onclick="generate()">
      <span class="spinner" id="spinner"></span>
      <span id="generateLabel">Generate Data</span>
    </button>
  </div>
  <div class="fanout-hint" id="fanoutHint" style="display:none;">
    Root tables shown in <span style="color:#86efac;font-weight:600">green</span>,
    child tables in <span style="color:#93c5fd;font-weight:600">blue</span> &mdash;
    row counts shown on each tab update as you change the inputs above.
  </div>

  <!-- Schema preview: collapsible, one tab per table -->
  <div class="schema-preview" id="schemaPreview">
    <div class="collapse-toggle open" id="schemaToggle" onclick="toggleSchemaCollapse()">
      <span id="schemaToggleLabel">Column Seeds &amp; Samples</span>
      <span class="arrow">&#9660;</span>
    </div>
    <div class="collapse-body" id="schemaCollapseBody">
      <div class="hint" style="margin-top:0.75rem;">
        Optionally seed any column with comma-separated <strong style="color:#e2e8f0">literals</strong>,
        <strong style="color:#e2e8f0">regex patterns</strong>, or
        <strong style="color:#e2e8f0">{variables}</strong> &mdash; the generator randomises a value each row.<br>
        <span style="color:#6366f1;font-weight:600">Regex:</span>
        <code>ORD-[A-Z]{2}[0-9]{4}</code> &nbsp;
        <span style="color:#6366f1;font-weight:600">Variables:</span>
        <code>{first_name}</code> <code>{last_name}</code> <code>{full_name}</code>
        <code>{email}</code> <code>{username}</code> <code>{city}</code>
        <code>{country}</code> <code>{company}</code> <code>{job_title}</code>
        <code>{male_name}</code> <code>{female_name}</code> <code>{street}</code><br>
        Mix freely: <code>{first_name}, Alice, BOB-[0-9]{4}</code> &nbsp;|&nbsp;
        Template: <code>{first_name} {last_name}</code> &nbsp;|&nbsp;
        <code>{first_name}.{last_name}@corp.com</code>
        &nbsp;&nbsp;<span style="color:#475569">&bull;</span>&nbsp;&nbsp;
        <span style="color:#6366f1;">&#8594;</span> columns marked <span class="fk-badge">FK</span> are auto-filled from the parent table.
      </div>
      <div class="tabs" id="schemaTabs"></div>
      <div id="schemaPanels"></div>
    </div>
  </div>
</div>

<!-- ── Results card ───────────────────────────────────────────────────────── -->
<div id="resultsSection">
  <div class="card">
    <div class="results-header">
      <h2>Generated Data</h2>
      <div style="display:flex;align-items:center;gap:1rem;">
        <span class="results-meta" id="resultsMeta"></span>
        <button class="btn btn-success" id="exportBtn" onclick="exportZip()">
          &#11015; Export ZIP (CSV per table)
        </button>
        <button class="btn btn-sql" id="exportSqlBtn" onclick="exportSql()">
          &#11015; Export SQL Script
        </button>
      </div>
    </div>
    <div class="tabs" id="resultTabs"></div>
    <div id="resultPanels"></div>
  </div>
</div>

<script>
  let currentSchema = null;
  let generatedData  = null;
  let _lastCounts   = {};

  // ── Theme ──────────────────────────────────────────────────────────────────
  (function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
  })();

  function toggleTheme() {
    const html = document.documentElement;
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }

  function setLoading(on) {
    document.getElementById('generateBtn').disabled = on;
    document.getElementById('spinner').classList.toggle('show', on);
    document.getElementById('generateLabel').textContent = on ? 'Generating\u2026' : 'Generate Data';
  }

  function showAlert(msg, type) {
    const box = document.getElementById('alertBox');
    box.textContent = msg;
    box.className = `alert alert-${type} show`;
  }
  function hideAlert() { document.getElementById('alertBox').classList.remove('show'); }

  // ── Tab helpers ────────────────────────────────────────────────────────────
  function buildTabs(tabsEl, panelsEl, items, renderPanel) {
    tabsEl.innerHTML   = '';
    panelsEl.innerHTML = '';
    items.forEach((item, idx) => {
      const btn = document.createElement('button');
      btn.className = 'tab-btn' + (idx === 0 ? ' active' : '');
      btn.dataset.tabName = item.name;
      btn.onclick = () => switchTab(tabsEl, panelsEl, idx);
      tabsEl.appendChild(btn);
      _setTabLabel(btn, item.name, _lastCounts);

      const panel = document.createElement('div');
      panel.className = 'tab-panel' + (idx === 0 ? ' active' : '');
      panel.id = panelsEl.id + '_panel_' + idx;
      panel.innerHTML = renderPanel(item, idx);
      panelsEl.appendChild(panel);
    });
  }

  function _setTabLabel(btn, tableName, counts) {
    const n = counts[tableName];
    if (n == null) {
      btn.textContent = tableName;
      return;
    }
    btn.innerHTML =
      escapeHtml(tableName) +
      ` <span class="count-badge${_isRoot(tableName) ? ' root' : ''}">${n} rows</span>`;
  }

  function _isRoot(tableName) {
    if (!currentSchema) return true;
    const tbl = (currentSchema.tables || []).find(t => t.name === tableName);
    if (!tbl) return true;
    const schemaNames = new Set((currentSchema.tables || []).map(t => t.name));
    return !(tbl.foreign_keys || []).some(fk => schemaNames.has(fk.ref_table));
  }

  function switchTab(tabsEl, panelsEl, idx) {
    tabsEl.querySelectorAll('.tab-btn').forEach((b, i) =>
      b.classList.toggle('active', i === idx));
    panelsEl.querySelectorAll('.tab-panel').forEach((p, i) =>
      p.classList.toggle('active', i === idx));
  }

  // ── Live count badge refresh ───────────────────────────────────────────────
  async function refreshCountBadges() {
    if (!currentSchema) return;
    const baseN   = parseInt(document.getElementById('numRecords').value, 10) || 10;
    const fanOut  = parseInt(document.getElementById('fanOut').value, 10)     || 3;
    try {
      const resp = await fetch('/table-counts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema: currentSchema, base_n: baseN, fan_out: fanOut }),
      });
      if (!resp.ok) return;
      const data = await resp.json();
      _lastCounts = data.counts || {};
      // Update tab labels in schema preview
      document.querySelectorAll('#schemaTabs .tab-btn').forEach(btn => {
        _setTabLabel(btn, btn.dataset.tabName, _lastCounts);
      });
    } catch(_) { /* silent — badges just won't update */ }
  }

  // ── Schema collapse toggle ─────────────────────────────────────────────────
  function toggleSchemaCollapse() {
    const toggle = document.getElementById('schemaToggle');
    const body   = document.getElementById('schemaCollapseBody');
    const isOpen = toggle.classList.contains('open');
    toggle.classList.toggle('open', !isOpen);
    body.classList.toggle('hidden', isOpen);
  }
  document.getElementById('schemaFile').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const text = await file.text();

    if (file.name.endsWith('.json')) {
      try {
        const raw = JSON.parse(text);
        currentSchema = normaliseSchema(raw);
        await refreshCountBadges();
        showSchemaPreview(currentSchema);
        const n = currentSchema.tables.length;
        showAlert(`Schema loaded: ${n} table${n>1?'s':''} detected.`, 'success');
        return;
      } catch(_) { /* fall through */ }
    }

    try {
      showAlert('Parsing schema\u2026', 'success');
      const resp = await fetch('/parse-schema', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: text,
      });
      const result = await resp.json();
      if (!resp.ok) {
        showAlert('Parse error: ' + (result.error || 'Unknown'), 'error');
        currentSchema = null; hideSchemaPreview(); return;
      }
      currentSchema = result;
      await refreshCountBadges();
      showSchemaPreview(currentSchema);
      const n = currentSchema.tables.length;
      showAlert(`Schema loaded: ${n} table${n>1?'s':''} from ${file.name}`, 'success');
    } catch(err) {
      showAlert('Failed to parse schema: ' + err.message, 'error');
      currentSchema = null; hideSchemaPreview();
    }
  });

  // Normalise a legacy single-table {columns:[]} to {tables:[]}
  function normaliseSchema(raw) {
    if (raw.tables) {
      raw.tables.forEach(t => { t.foreign_keys = t.foreign_keys || []; });
      return raw;
    }
    if (raw.columns) {
      return { tables: [{ name: 'table1', columns: raw.columns, foreign_keys: [] }] };
    }
    throw new Error('Schema must have "tables" or "columns"');
  }

  // ── Schema preview ─────────────────────────────────────────────────────────
  function showSchemaPreview(schema) {
    const tables = schema.tables || [];
    buildTabs(
      document.getElementById('schemaTabs'),
      document.getElementById('schemaPanels'),
      tables,
      (tbl, tblIdx) => renderSchemaPanel(tbl, tblIdx)
    );
    document.getElementById('schemaPreview').classList.add('show');
    document.getElementById('fanoutHint').style.display = '';
    // Reset collapse to open
    document.getElementById('schemaToggle').classList.add('open');
    document.getElementById('schemaCollapseBody').classList.remove('hidden');
  }

  function hideSchemaPreview() {
    document.getElementById('schemaPreview').classList.remove('show');
    document.getElementById('schemaTabs').innerHTML   = '';
    document.getElementById('schemaPanels').innerHTML = '';
    document.getElementById('fanoutHint').style.display = 'none';
    _lastCounts = {};
  }

  function renderSchemaPanel(tbl, tblIdx) {
    const fkSet = new Set((tbl.foreign_keys || []).map(fk => fk.column));
    const fkMap = {};
    (tbl.foreign_keys || []).forEach(fk => { fkMap[fk.column] = `${fk.ref_table}.${fk.ref_column}`; });

    const rows = (tbl.columns || []).map((c, colIdx) => {
      const isFk    = fkSet.has(c.name);
      const fkLabel = isFk ? `<span class="fk-badge" title="References ${fkMap[c.name]}">FK &rarr; ${fkMap[c.name]}</span>` : '';
      const typeStr = escapeHtml(c.type || 'string') + (c.length ? `(${c.length})` : '');
      return `
        <tr>
          <td class="col-name">${escapeHtml(c.name)}${fkLabel}</td>
          <td class="col-type">${typeStr}</td>
          <td>
            <input
              class="samples-input"
              id="samples_${tblIdx}_${colIdx}"
              type="text"
              placeholder="${isFk ? 'Auto-filled from ' + fkMap[c.name] : 'e.g. Alice, Bob  or  ORD-[A-Z]{2}[0-9]{4}'}"
              autocomplete="off"
              ${isFk ? 'disabled title="FK column \u2014 value comes from parent table"' : ''}
            />
          </td>
        </tr>`;
    }).join('');

    return `
      <div class="schema-tbl-wrap">
        <table class="schema-tbl">
          <thead>
            <tr>
              <th>Column</th>
              <th>Type</th>
              <th>Values / Patterns <span style="font-weight:400;color:#475569">(comma-separated, optional)</span></th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }

  // ── Generate ───────────────────────────────────────────────────────────────
  async function generate() {
    if (!currentSchema) {
      showAlert('Please upload a schema file first.', 'error'); return;
    }
    const numRecords = parseInt(document.getElementById('numRecords').value, 10);
    const fanOut     = parseInt(document.getElementById('fanOut').value, 10);
    if (isNaN(numRecords) || numRecords < 1 || numRecords > 1000) {
      showAlert('Base rows must be between 1 and 1000.', 'error'); return;
    }
    if (isNaN(fanOut) || fanOut < 1 || fanOut > 20) {
      showAlert('Child fan-out must be between 1 and 20.', 'error'); return;
    }

    // Collect sample seeds from the UI and attach to each column
    const enrichedTables = (currentSchema.tables || []).map((tbl, tblIdx) => {
      const fkSet = new Set((tbl.foreign_keys || []).map(fk => fk.column));
      const enrichedCols = (tbl.columns || []).map((col, colIdx) => {
        if (fkSet.has(col.name)) return { ...col };
        const input   = document.getElementById(`samples_${tblIdx}_${colIdx}`);
        const raw     = input ? input.value.trim() : '';
        const samples = raw
          ? raw.split(',').map(s => s.trim()).filter(s => s.length > 0)
          : [];
        return samples.length > 0 ? { ...col, samples } : { ...col };
      });
      return { ...tbl, columns: enrichedCols };
    });

    setLoading(true); hideAlert();

    try {
      const resp = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schema:      { tables: enrichedTables },
          num_records: numRecords,
          fan_out:     fanOut,
        }),
      });
      const data = await resp.json();
      if (!resp.ok) { showAlert('Error: ' + (data.error || 'Unknown'), 'error'); return; }

      generatedData = data;
      renderResults(data);

      const total = (data.tables || []).reduce((s, t) => s + (t.rows || []).length, 0);
      const summary = (data.tables || []).map(t =>
        `${t.name}\u00a0(${t.rows.length})`).join(', ');
      document.getElementById('resultsMeta').textContent =
        `${data.tables.length} table${data.tables.length>1?'s':''} \u00b7 ${total} rows total \u2014 ${summary}`;
      document.getElementById('resultsSection').classList.add('show');

    } catch(err) {
      showAlert('Request failed: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  }

  // ── Results rendering ──────────────────────────────────────────────────────
  // Each panel stores its full data on the DOM element so search/sort can
  // re-render without hitting the server again.

  function renderResults(data) {
    const tables = data.tables || [];
    buildTabs(
      document.getElementById('resultTabs'),
      document.getElementById('resultPanels'),
      tables,
      (tbl) => renderResultPanel(tbl)
    );
  }

  function renderResultPanel(tbl) {
    const cols    = tbl.columns || [];
    const rows    = tbl.rows    || [];
    const tblId   = 'rt_' + tbl.name.replace(/\W/g, '_');

    // Store full data as JSON — must NOT be HTML-escaped or JSON.parse will fail.
    // Only escape the closing script tag sequence to avoid breaking the page.
    const dataJson = JSON.stringify({ cols, rows }).replace(/<\/script/gi, '<\\/script');

    const thead = '<tr>' + cols.map((c, ci) => `
      <th data-col="${ci}" onclick="sortResultCol('${tblId}', ${ci})" title="Sort by ${escapeHtml(c)}">
        ${escapeHtml(c)}<span class="sort-arrow"></span>
      </th>`).join('') + '</tr>';

    const tbodyHtml = _buildTbody(rows, cols.length);

    return `
      <script type="application/json" id="${tblId}_data">${dataJson}<\/script>
      <div style="font-size:0.82rem;color:#64748b;margin-bottom:0.5rem;">
        <span id="${tblId}_count">${rows.length} row${rows.length!==1?'s':''}</span>
        &times; ${cols.length} column${cols.length!==1?'s':''}
      </div>
      <div class="search-row">
        <input
          class="search-input"
          id="${tblId}_search"
          type="text"
          placeholder="Search across all columns\u2026"
          oninput="searchResultTable('${tblId}')"
          autocomplete="off"
        />
        <span class="search-count" id="${tblId}_searchCount"></span>
      </div>
      <div class="data-tbl-wrap">
        <table class="data-tbl" id="${tblId}_tbl">
          <thead id="${tblId}_thead">${thead}</thead>
          <tbody id="${tblId}_tbody">${tbodyHtml}</tbody>
        </table>
      </div>`;
  }

  function _buildTbody(rows, _numCols) {
    if (!rows.length) return '<tr><td colspan="99" style="text-align:center;color:#475569;padding:2rem;">No rows</td></tr>';
    return rows.map(row =>
      '<tr>' + row.map(cell => `<td title="${escapeHtml(cell)}">${escapeHtml(cell)}</td>`).join('') + '</tr>'
    ).join('');
  }

  // Per-table sort state: { tblId: {col: int, dir: 'asc'|'desc'|null} }
  const _sortState = {};

  function sortResultCol(tblId, colIdx) {
    const stored = JSON.parse(document.getElementById(tblId + '_data').textContent);
    const q      = (document.getElementById(tblId + '_search') || {}).value || '';

    // Cycle: none → asc → desc → none
    const prev = (_sortState[tblId] || {});
    let dir;
    if (prev.col !== colIdx || prev.dir == null) dir = 'asc';
    else if (prev.dir === 'asc')  dir = 'desc';
    else                          dir = null;
    _sortState[tblId] = { col: colIdx, dir };

    // Update header arrows
    const thead = document.getElementById(tblId + '_thead');
    thead.querySelectorAll('th').forEach((th, i) => {
      th.classList.remove('sort-asc', 'sort-desc');
      if (i === colIdx && dir) th.classList.add('sort-' + dir);
    });

    _applyFilterSort(tblId, stored, q);
  }

  function searchResultTable(tblId) {
    const stored = JSON.parse(document.getElementById(tblId + '_data').textContent);
    const q      = document.getElementById(tblId + '_search').value;
    _applyFilterSort(tblId, stored, q);
  }

  function _applyFilterSort(tblId, stored, q) {
    const { cols, rows } = stored;
    const needle = q.trim().toLowerCase();

    // Filter
    let visible = needle
      ? rows.filter(row => row.some(cell => String(cell).toLowerCase().includes(needle)))
      : rows;

    // Sort
    const s = _sortState[tblId] || {};
    if (s.dir && s.col != null) {
      visible = [...visible].sort((a, b) => {
        const av = a[s.col], bv = b[s.col];
        // Numeric comparison if both look like numbers
        const an = parseFloat(av), bn = parseFloat(bv);
        const numericCmp = !isNaN(an) && !isNaN(bn) ? an - bn
                         : String(av).localeCompare(String(bv), undefined, { sensitivity: 'base' });
        return s.dir === 'asc' ? numericCmp : -numericCmp;
      });
    }

    // Re-render tbody
    document.getElementById(tblId + '_tbody').innerHTML = _buildTbody(visible, cols.length);

    // Update count
    const countEl = document.getElementById(tblId + '_count');
    if (countEl) countEl.textContent = visible.length + ' row' + (visible.length !== 1 ? 's' : '');

    const searchCountEl = document.getElementById(tblId + '_searchCount');
    if (searchCountEl) {
      searchCountEl.textContent = needle
        ? `${visible.length} of ${rows.length} rows`
        : '';
    }
  }

  // ── Export ZIP ─────────────────────────────────────────────────────────────
  async function exportZip() {
    if (!generatedData) return;
    try {
      const resp = await fetch('/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedData),
      });
      if (!resp.ok) { showAlert('Export failed.', 'error'); return; }

      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'synthetic_data.zip';
      a.click();
      URL.revokeObjectURL(url);
    } catch(err) {
      showAlert('Export error: ' + err.message, 'error');
    }
  }

  // ── Export SQL Script ──────────────────────────────────────────────────────
  async function exportSql() {
    if (!generatedData || !currentSchema) return;
    const btn = document.getElementById('exportSqlBtn');
    btn.disabled = true;
    try {
      const resp = await fetch('/export-sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schema: currentSchema, data: generatedData }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        showAlert('SQL export failed: ' + (err.error || resp.statusText), 'error');
        return;
      }
      const text = await resp.text();
      const blob = new Blob([text], { type: 'text/plain' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'synthetic_data.sql';
      a.click();
      URL.revokeObjectURL(url);
    } catch(err) {
      showAlert('SQL export error: ' + err.message, 'error');
    } finally {
      btn.disabled = false;
    }
  }
</script>
</body>
</html>"""
