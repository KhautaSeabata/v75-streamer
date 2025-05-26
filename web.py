from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

FIREBASE_URL = "https://fir-8908c-default-rtdb.firebaseio.com"
SYMBOL = "R_25"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Tick Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: #121212;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
        }
        canvas {
            background: #1e1e1e;
            border-radius: 8px;
        }
        h2 {
            color: #00e676;
        }
    </style>
</head>
<body>
    <h2>Live Tick Chart (Last 600)</h2>
    <canvas id="lineChart" width="900" height="400"></canvas>

    <script>
        const ctx = document.getElementById('lineChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Quote',
                    data: [],
                    borderColor: '#00e676',
                    backgroundColor: 'rgba(0,230,118,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                animation: false,
                scales: {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: '#333' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: '#333' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });

        async function fetchTicks() {
            try {
                const res = await fetch('/ticks');
                const ticks = await res.json();

                const labels = ticks.map(t => new Date(t.epoch * 1000).toLocaleTimeString());
                const data = ticks.map(t => t.quote);

                chart.data.labels = labels;
                chart.data.datasets[0].data = data;
                chart.update();
            } catch (e) {
                console.error("Failed to load ticks:", e);
            }
        }

        // Load ticks every second
        fetchTicks();
        setInterval(fetchTicks, 1000);
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/ticks")
def get_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        res = requests.get(url)
        data = res.json() or {}

        ticks = [{"epoch": v["epoch"], "quote": v["quote"]} for v in data.values()]
        ticks.sort(key=lambda x: x["epoch"])

        return jsonify(ticks[-600:])  # Latest 600 ticks
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
