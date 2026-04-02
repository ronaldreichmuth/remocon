"""
Web-Interface: Temperaturverlauf der letzten 3 Tage im Browser.
Starten: .venv/bin/python web.py  →  http://localhost:5005
"""

import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string

import os
DB_FILE = os.environ.get("DB_FILE", "/data/heizung.db")

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Warmwasser Temperaturverlauf</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; background: #f4f4f4; padding: 2rem; }
        h1 { font-size: 1.4rem; color: #333; margin-bottom: 1rem; }
        .card { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .meta { margin-top: 0.8rem; font-size: 0.85rem; color: #888; text-align: right; }
        .current { font-size: 2.5rem; font-weight: bold; color: #e05a2b; margin-bottom: 1rem; }
        .current span { font-size: 1rem; color: #888; font-weight: normal; }
    </style>
</head>
<body>
    <h1>Heizung – Temperaturverlauf letzte 3 Tage</h1>

    <div class="card" style="margin-bottom:1.5rem;">
        <div class="current" id="current-ww">– <span>°C Warmwasser</span></div>
        <canvas id="chart-ww" height="100"></canvas>
    </div>

    <div class="card">
        <div class="current" style="color:#4a90d9;" id="current-out">– <span>°C Aussentemperatur</span></div>
        <canvas id="chart-out" height="100"></canvas>
        <div class="meta" id="meta">wird geladen…</div>
    </div>

    <script>
        const options = (title) => ({
            scales: {
                x: { type: 'time', time: { unit: 'hour', displayFormats: { hour: 'dd.MM HH:mm' } }, ticks: { maxTicksLimit: 12 } },
                y: { title: { display: true, text: title } }
            },
            plugins: { legend: { display: false } },
            animation: false,
            aspectRatio: 1.25,
        });

        const chartWW = new Chart(document.getElementById('chart-ww').getContext('2d'), {
            type: 'line',
            data: { datasets: [{
                label: 'Warmwasser (°C)',
                data: [],
                borderColor: '#e05a2b',
                backgroundColor: 'rgba(224,90,43,0.1)',
                fill: true, tension: 0.3, pointRadius: 2,
            }]},
            options: options('°C'),
        });

        const chartOut = new Chart(document.getElementById('chart-out').getContext('2d'), {
            type: 'line',
            data: { datasets: [{
                label: 'Aussen (°C)',
                data: [],
                borderColor: '#4a90d9',
                backgroundColor: 'rgba(74,144,217,0.08)',
                fill: true, tension: 0.3, pointRadius: 2,
            }]},
            options: options('°C'),
        });

        async function load() {
            const res = await fetch('/api/data');
            const rows = await res.json();

            chartWW.data.datasets[0].data = rows.map(r => ({ x: r.timestamp, y: r.temp_c }));
            chartWW.update();

            const outRows = rows.filter(r => r.outside_temp !== null);
            chartOut.data.datasets[0].data = outRows.map(r => ({ x: r.timestamp, y: r.outside_temp }));
            chartOut.update();

            if (rows.length > 0) {
                const last = rows[rows.length - 1];
                document.getElementById('current-ww').innerHTML = `${last.temp_c.toFixed(1)} <span>°C Warmwasser</span>`;
                if (last.outside_temp !== null)
                    document.getElementById('current-out').innerHTML = `${last.outside_temp.toFixed(1)} <span>°C Aussentemperatur</span>`;
            }
            document.getElementById('meta').textContent =
                `${rows.length} Messwerte · aktualisiert: ${new Date().toLocaleTimeString('de-CH')}`;
        }

        load();
        setInterval(load, 5 * 60 * 1000);
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/data")
def api_data():
    seit = datetime.now() - timedelta(days=3)
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT timestamp, temp_c, outside_temp FROM warmwasser WHERE timestamp >= ? ORDER BY timestamp",
        (seit.strftime("%Y-%m-%d %H:%M:%S"),),
    ).fetchall()
    con.close()

    def to_iso(ts_str):
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").astimezone().isoformat()

    return jsonify([{"timestamp": to_iso(r[0]), "temp_c": r[1], "outside_temp": r[2]} for r in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5005)
