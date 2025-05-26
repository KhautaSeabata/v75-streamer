from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

FIREBASE_URL = "https://fir-8908c-default-rtdb.firebaseio.com"
SYMBOL = "R_25"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Ticks & Candles</title>
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
            background: #222;
            margin-bottom: 40px;
            border-radius: 6px;
        }
        h2 {
            margin-bottom: 10px;
            color: #00e676;
        }
    </style>
</head>
<body>
    <h2>Live Ticks (Latest 5)</h2>
    <canvas id="lineChart" width="800" height="300"></canvas>

    <h2>1-Minute Candlestick Chart</h2>
    <canvas id="candlestickChart" width="800" height="400"></canvas>

    <script>
        const lineCtx = document.getElementById('lineChart').getContext('2d');
        const candleCtx = document.getElementById('candlestickChart').getContext('2d');

        // Line chart for ticks
        const lineChart = new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Quote',
                    data: [],
                    borderColor: '#00e676',
                    backgroundColor: 'rgba(0,230,118,0.2)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: { parser: 'unix', unit: 'second', displayFormats: { second: 'HH:mm:ss' }},
                        ticks: { color: 'white' },
                        grid: { color: '#444' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: '#444' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });

        // Candlestick chart using financial plugin (needs Chart.js financial plugin)
        // Since we cannot import it via CDN easily here, we'll do a simplified OHLC style candle using 'bar' chart with custom colors.
        // For better visuals, you should integrate Chart.js Financial plugin in production.

        const candlestickChart = new Chart(candleCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Open-Close',
                        data: [],
                        backgroundColor: function(context) {
                            const open = context.raw.open;
                            const close = context.raw.close;
                            return close > open ? '#4caf50' : '#f44336'; // green or red
                        },
                        borderSkipped: false,
                        borderRadius: 2,
                        barPercentage: 0.7,
                    },
                    {
                        label: 'High-Low',
                        data: [],
                        type: 'line',
                        borderColor: 'white',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: false,
                        tension: 0,
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: '#444' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: '#444' }
                    }
                },
                plugins: {
                    legend: { labels: { color: 'white' } }
                }
            }
        });

        // Fetch and update latest 5 ticks every 3 seconds
        async function updateTicks() {
            try {
                const res = await fetch('/candles/ticks');
                if(!res.ok) throw new Error('Failed to fetch ticks');
                const ticks = await res.json();

                const labels = ticks.map(t => new Date(t.epoch * 1000));
                const data = ticks.map(t => t.quote);

                lineChart.data.labels = labels;
                lineChart.data.datasets[0].data = data;
                lineChart.update();
            } catch (err) {
                console.error(err);
            }
        }

        // Fetch and update 1min candles every 10 seconds
        async function updateCandles() {
            try {
                const res = await fetch('/candles/1min');
                if(!res.ok) throw new Error('Failed to fetch candles');
                const candles = await res.json();

                // candles is array of {epoch, open, high, low, close}

                candlestickChart.data.labels = candles.map(c => new Date(c.epoch * 1000));

                // Prepare open-close as bar height data
                candlestickChart.data.datasets[0].data = candles.map(c => ({
                    open: c.open,
                    close: c.close,
                    y: (c.open + c.close) / 2,
                    // We'll use y as middle of open-close for bar position (hack)
                }));

                // Prepare high-low as line data
                candlestickChart.data.datasets[1].data = candles.map(c => [c.low, c.high]);

                candlestickChart.update();
            } catch (err) {
                console.error(err);
            }
        }

        // Initial update
        updateTicks();
        updateCandles();

        // Poll intervals
        setInterval(updateTicks, 3000);
        setInterval(updateCandles, 10000);
    </script>
</body>
</html>
"""

@app.route("/candles")
def candles():
    return render_template_string(HTML)

@app.route("/candles/ticks")
def get_ticks():
    try:
        url = f"{FIREBASE_URL}/ticks/{SYMBOL}.json"
        response = requests.get(url)
        data = response.json() or {}

        ticks = []
        for item in data.values():
            ticks.append({"epoch": item["epoch"], "quote": item["quote"]})

        ticks.sort(key=lambda x: x["epoch"])
        latest_ticks = ticks[-5:] if len(ticks) >= 5 else ticks

        return jsonify(latest_ticks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/candles/1min")
def get_1min_candles():
    try:
        url = f"{FIREBASE_URL}/1minVix25.json"
        response = requests.get(url)
        data = response.json() or {}

        candles = []
        for item in data.values():
            candles.append({
                "epoch": item.get("epoch"),
                "open": item.get("open"),
                "high": item.get("high"),
                "low": item.get("low"),
                "close": item.get("close"),
            })

        candles.sort(key=lambda x: x["epoch"])
        # Return last 20 candles max for performance
        return jsonify(candles[-20:])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
