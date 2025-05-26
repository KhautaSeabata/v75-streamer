from flask import Flask, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

FIREBASE_URL = "https://vix75-f6684-default-rtdb.firebaseio.com"  # update your Firebase URL
SYMBOL = "R_25"

HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>Live Deriv Ticks → Firebase</title></head>
<body style="background:#121212;color:white;text-align:center;padding:50px;font-family:Arial,sans-serif;">
<h1>📡 Live Tick Streaming</h1>
<p>Streaming <b>Deriv</b> tick data for <b>{{symbol}}</b> to <b>Firebase</b>...</p>
<a href="/candles"><button style="font-size:18px;padding:10px 20px;cursor:pointer;">View Candles & Ticks Chart</button></a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML, symbol=SYMBOL)

@app.route("/candles/data")
def candles_data():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json() or {}

        ticks = []
        for item in data.values():
            ticks.append({"epoch": item["epoch"], "quote": item["quote"]})

        ticks.sort(key=lambda x: x["epoch"])

        # Return only latest 5 ticks
        latest_ticks = ticks[-5:] if len(ticks) >= 5 else ticks

        return jsonify(latest_ticks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

CANDLES_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Ticks Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
      body { background:#121212; color:#eee; font-family:Arial,sans-serif; text-align:center; padding:20px;}
      canvas { max-width: 900px; margin: auto; background:#222; border-radius:8px; }
      #status { margin-top: 10px; color:#aaa; }
    </style>
</head>
<body>
<h2>Live Ticks Line Chart (Quote vs Time)</h2>
<canvas id="tickChart" width="900" height="400"></canvas>
<div id="status">Loading...</div>

<script>
const ctx = document.getElementById('tickChart').getContext('2d');
let chart;

function epochToTimeLabel(epoch) {
    const date = new Date(epoch * 1000);
    return date.toLocaleTimeString();
}

async function fetchTickData() {
    try {
        const response = await fetch("/candles/data");
        if (!response.ok) {
            console.error("Failed to fetch tick data");
            document.getElementById('status').textContent = "Failed to load data";
            return [];
        }
        const data = await response.json();
        document.getElementById('status').textContent = `Showing latest ${data.length} ticks (live updating)`;
        return data;
    } catch (e) {
        console.error("Error fetching tick data:", e);
        document.getElementById('status').textContent = "Error loading data";
        return [];
    }
}

async function updateChart() {
    const ticks = await fetchTickData();

    if (!ticks.length) return;

    const labels = ticks.map(t => epochToTimeLabel(t.epoch));
    const quotes = ticks.map(t => t.quote);

    if (!chart) {
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Quote',
                    data: quotes,
                    borderColor: '#00e676',
                    backgroundColor: 'rgba(0,230,118,0.3)',
                    fill: true,
                    pointRadius: 3,
                    tension: 0.2
                }]
            },
            options: {
                responsive: true,
                animation: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Time' },
                        ticks: { color: '#eee' }
                    },
                    y: {
                        title: { display: true, text: 'Quote' },
                        ticks: { color: '#eee' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#eee' } }
                }
            }
        });
    } else {
        chart.data.labels = labels;
        chart.data.datasets[0].data = quotes;
        chart.update();
    }
}

// Initial load + update every 3 seconds
updateChart();
setInterval(updateChart, 3000);
</script>
</body>
</html>
"""

@app.route("/candles")
def candles():
    return render_template_string(CANDLES_HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
