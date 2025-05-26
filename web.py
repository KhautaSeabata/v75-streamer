from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# HTML page for live chart with trendline overlay
CANDLES_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Tick Chart with Trendlines</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: #121212;
            color: white;
            font-family: Arial;
            text-align: center;
        }
        canvas {
            margin-top: 20px;
            background-color: #1e1e1e;
        }
    </style>
</head>
<body>
    <h2>📉 Live Tick Chart with Channel Detection</h2>
    <canvas id="tickChart" width="1000" height="400"></canvas>

    <script>
        const ctx = document.getElementById('tickChart').getContext('2d');
        const tickData = {
            labels: [],
            datasets: [{
                label: 'R_25 Ticks',
                data: [],
                borderColor: 'lime',
                backgroundColor: 'transparent',
                tension: 0.2,
                pointRadius: 0,
            }]
        };

        const trendlineDatasetTemplate = (label, color) => ({
            label: label,
            data: [],
            borderColor: color,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0,
            tension: 0,
        });

        const config = {
            type: 'line',
            data: tickData,
            options: {
                animation: false,
                scales: {
                    x: {
                        ticks: { color: 'white' }
                    },
                    y: {
                        ticks: { color: 'white' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' }}
                }
            }
        };

        const tickChart = new Chart(ctx, config);

        // Fetch ticks every second
        async function fetchTicks() {
            const res = await fetch("https://fir-8908c-default-rtdb.firebaseio.com/ticks/R_25.json");
            const data = await res.json();
            const ticks = Object.values(data || {}).slice(-600);

            tickChart.data.labels = ticks.map(t => new Date(t.epoch * 1000).toLocaleTimeString());
            tickChart.data.datasets[0].data = ticks.map(t => t.quote);
            tickChart.update();
        }

        // Fetch and overlay trendlines
        async function fetchTrendlines() {
            const res = await fetch("https://fir-8908c-default-rtdb.firebaseio.com/analysis/R_25.json");
            const data = await res.json();

            // Remove old trendline datasets
            tickChart.data.datasets = tickChart.data.datasets.slice(0, 1);

            if (!data) return;

            for (const channel of data) {
                const { type, upper, lower } = channel;
                if (!upper || !lower) continue;

                const color = type === "up" ? "blue" : type === "down" ? "red" : "white";

                const upperLine = trendlineDatasetTemplate(`${type.toUpperCase()} Upper`, color);
                const lowerLine = trendlineDatasetTemplate(`${type.toUpperCase()} Lower`, color);

                upperLine.data = upper.map(p => ({ x: new Date(p[0] * 1000).toLocaleTimeString(), y: p[1] }));
                lowerLine.data = lower.map(p => ({ x: new Date(p[0] * 1000).toLocaleTimeString(), y: p[1] }));

                tickChart.data.datasets.push(upperLine, lowerLine);
            }

            tickChart.update();
        }

        setInterval(() => {
            fetchTicks();
            fetchTrendlines();
        }, 1000);

        fetchTicks();
        fetchTrendlines();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Tick Stream Dashboard</title></head>
    <body style="text-align:center;font-family:Arial;background:#121212;color:white;padding:50px;">
        <h1>📡 Streaming Deriv Tick Data for <b>R_25</b> to Firebase</h1>
        <a href="/candles">
            <button style="margin-top:20px;padding:12px 20px;font-size:16px;background:#00e676;border:none;color:white;border-radius:5px;">
                🔍 View Chart
            </button>
        </a>
    </body>
    </html>
    """

@app.route("/candles")
def candles():
    return render_template_string(CANDLES_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
