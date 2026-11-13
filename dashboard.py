from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Fraud Detection Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@400;700;800&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg: #060a10;
      --bg2: #0d1520;
      --bg3: #111d2e;
      --green: #00ff88;
      --red: #ff3c5e;
      --yellow: #ffd166;
      --blue: #4fc3f7;
      --text: #cce6ff;
      --muted: #4a6a8a;
      --border: #1a3050;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: var(--bg);
      font-family: 'Syne', sans-serif;
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }

    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
      background-size: 40px 40px;
      opacity: 0.3;
      pointer-events: none;
      z-index: 0;
    }

    .page { position: relative; z-index: 1; padding: 2rem; max-width: 1200px; margin: 0 auto; }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2.5rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
    }

    .logo { display: flex; align-items: center; gap: 0.75rem; }

    .logo-icon {
      width: 42px; height: 42px;
      background: linear-gradient(135deg, var(--green), #00c9ff);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem;
      box-shadow: 0 0 20px rgba(0,255,136,0.4);
    }

    h1 {
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      background: linear-gradient(90deg, var(--green), var(--blue));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .subtitle { font-size: 0.75rem; color: var(--muted); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px; }

    .live-badge {
      display: flex; align-items: center; gap: 0.5rem;
      background: rgba(0,255,136,0.08);
      border: 1px solid rgba(0,255,136,0.25);
      border-radius: 20px;
      padding: 0.4rem 1rem;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      color: var(--green);
    }

    .live-dot {
      width: 8px; height: 8px;
      background: var(--green);
      border-radius: 50%;
      animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,255,136,0.5); }
      50% { opacity: 0.7; box-shadow: 0 0 0 5px rgba(0,255,136,0); }
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.25rem;
      margin-bottom: 2rem;
    }

    .card {
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.5rem;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }

    .card:hover { transform: translateY(-2px); border-color: var(--muted); }

    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
    }

    .card.total::before { background: linear-gradient(90deg, var(--blue), transparent); }
    .card.legit::before { background: linear-gradient(90deg, var(--green), transparent); }
    .card.sus::before   { background: linear-gradient(90deg, var(--red), transparent); }

    .card-label {
      font-size: 0.7rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.75rem;
    }

    .card-value {
      font-family: 'Share Tech Mono', monospace;
      font-size: 2.5rem;
      font-weight: 400;
      line-height: 1;
    }

    .card.total .card-value { color: var(--blue); }
    .card.legit .card-value { color: var(--green); }
    .card.sus   .card-value { color: var(--red); }

    .card-icon {
      position: absolute;
      right: 1.5rem; top: 50%;
      transform: translateY(-50%);
      font-size: 2.5rem;
      opacity: 0.08;
    }

    .tabs { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; }

    .tab {
      padding: 0.5rem 1.25rem;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-family: 'Syne', sans-serif;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      transition: all 0.15s;
    }

    .tab:hover { border-color: var(--muted); color: var(--text); }
    .tab.active { background: var(--blue); border-color: var(--blue); color: #000; }
    .tab.active.red { background: var(--red); border-color: var(--red); color: #fff; }

    .table-wrap {
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }

    table { width: 100%; border-collapse: collapse; }

    thead tr {
      background: var(--bg3);
      border-bottom: 1px solid var(--border);
    }

    th {
      padding: 1rem 1.25rem;
      text-align: left;
      font-size: 0.65rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--muted);
      font-weight: 700;
    }

    tbody tr {
      border-bottom: 1px solid rgba(26,48,80,0.5);
      transition: background 0.15s;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateX(-6px); } to { opacity: 1; transform: none; } }

    tbody tr:hover { background: rgba(255,255,255,0.02); }
    tbody tr:last-child { border-bottom: none; }

    td { padding: 1rem 1.25rem; font-size: 0.875rem; }

    .txn-id {
      font-family: 'Share Tech Mono', monospace;
      color: var(--blue);
      font-size: 0.8rem;
    }

    .amount { font-family: 'Share Tech Mono', monospace; }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.3rem 0.75rem;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .badge.legit {
      background: rgba(0,255,136,0.1);
      color: var(--green);
      border: 1px solid rgba(0,255,136,0.25);
    }

    .badge.sus {
      background: rgba(255,60,94,0.1);
      color: var(--red);
      border: 1px solid rgba(255,60,94,0.3);
      animation: glowRed 2s infinite;
    }

    @keyframes glowRed {
      0%, 100% { box-shadow: none; }
      50% { box-shadow: 0 0 8px rgba(255,60,94,0.3); }
    }

    .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

    .empty { padding: 4rem; text-align: center; color: var(--muted); font-size: 0.9rem; }
    .empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.3; }

    footer {
      margin-top: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.72rem;
      color: var(--muted);
      letter-spacing: 0.08em;
    }

    #last-updated { font-family: 'Share Tech Mono', monospace; }

    .refresh-btn {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--muted);
      padding: 0.4rem 1rem;
      border-radius: 8px;
      font-family: 'Syne', sans-serif;
      font-size: 0.72rem;
      cursor: pointer;
      transition: all 0.15s;
    }

    .refresh-btn:hover { border-color: var(--blue); color: var(--blue); }
  </style>
</head>
<body>
<div class="page">

  <header>
    <div class="logo">
      <div class="logo-icon">🛡</div>
      <div>
        <h1>FraudShield</h1>
        <div class="subtitle">Real-Time Detection Dashboard</div>
      </div>
    </div>
    <div class="live-badge">
      <div class="live-dot"></div>
      LIVE MONITORING
    </div>
  </header>

  <div class="stats">
    <div class="card total">
      <div class="card-icon">📊</div>
      <div class="card-label">Total Transactions</div>
      <div class="card-value" id="count-total">—</div>
    </div>
    <div class="card legit">
      <div class="card-icon">✅</div>
      <div class="card-label">Legitimate</div>
      <div class="card-value" id="count-legit">—</div>
    </div>
    <div class="card sus">
      <div class="card-icon">⚠️</div>
      <div class="card-label">Suspicious</div>
      <div class="card-value" id="count-sus">—</div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" id="tab-all" onclick="switchTab('all')">All Transactions</button>
    <button class="tab" id="tab-sus" onclick="switchTab('sus')">⚠ Suspicious Only</button>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Transaction ID</th>
          <th>Amount</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody id="table-body">
        <tr><td colspan="4"><div class="empty"><div class="empty-icon">📡</div>Waiting for data...</div></td></tr>
      </tbody>
    </table>
  </div>

  <footer>
    <span>Auto-refreshes every 3 seconds</span>
    <span id="last-updated">—</span>
    <button class="refresh-btn" onclick="loadData()">↻ Refresh Now</button>
  </footer>

</div>

<script>
  let currentTab = 'all';

  function switchTab(tab) {
    currentTab = tab;
    document.getElementById('tab-all').classList.remove('active', 'red');
    document.getElementById('tab-sus').classList.remove('active', 'red');
    if (tab === 'all') {
      document.getElementById('tab-all').classList.add('active');
    } else {
      document.getElementById('tab-sus').classList.add('active', 'red');
    }
    loadData();
  }

  async function loadStats() {
    try {
      const res = await fetch('/api/all');
      const data = await res.json();
      const sus = data.filter(d => d.status.includes('SUSPICIOUS'));
      document.getElementById('count-total').textContent = data.length;
      document.getElementById('count-legit').textContent = data.length - sus.length;
      document.getElementById('count-sus').textContent = sus.length;
    } catch(e) {}
  }

  async function loadData() {
    const url = currentTab === 'sus' ? '/api/suspicious' : '/api/all';
    try {
      const res = await fetch(url);
      const data = await res.json();
      const tbody = document.getElementById('table-body');

      if (!data.length) {
        tbody.innerHTML = '<tr><td colspan="4"><div class="empty"><div class="empty-icon">📡</div>No transactions yet. Start the producer!</div></td></tr>';
        return;
      }

      tbody.innerHTML = data.map((row, i) => {
        const isSus = row.status.includes('SUSPICIOUS');
        const badge = isSus
          ? '<span class="badge sus"><span class="badge-dot"></span>' + row.status + '</span>'
          : '<span class="badge legit"><span class="badge-dot"></span>LEGITIMATE</span>';
        const amtColor = isSus ? 'color: var(--red)' : 'color: var(--green)';
        return '<tr>'
          + '<td style="color:var(--muted);font-family:Share Tech Mono,monospace;font-size:0.75rem">' + String(i+1).padStart(2,'0') + '</td>'
          + '<td><span class="txn-id">' + row.transaction_id + '</span></td>'
          + '<td><span class="amount" style="' + amtColor + '">&#8377; ' + Number(row.amount).toFixed(2) + '</span></td>'
          + '<td>' + badge + '</td>'
          + '</tr>';
      }).join('');

      document.getElementById('last-updated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
    } catch(e) {
      document.getElementById('table-body').innerHTML = '<tr><td colspan="4"><div class="empty"><div class="empty-icon">❌</div>Cannot reach API. Is the server running?</div></td></tr>';
    }
    loadStats();
  }

  loadData();
  setInterval(loadData, 3000);
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTML

@app.get("/api/all")
def get_all():
    conn = sqlite3.connect("results.db")
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY rowid DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [{"transaction_id": r[0], "amount": r[1], "status": r[2]} for r in rows]

@app.get("/api/suspicious")
def get_suspicious():
    conn = sqlite3.connect("results.db")
    rows = conn.execute(
        "SELECT * FROM transactions WHERE status LIKE '%SUSPICIOUS%' ORDER BY rowid DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [{"transaction_id": r[0], "amount": r[1], "status": r[2]} for r in rows]