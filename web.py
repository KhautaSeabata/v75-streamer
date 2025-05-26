# web.py
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# ... (keep the previous home route and HTML unchanged)

CHART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MT5-style Vix25 Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        body {
            margin: 0;
            background: #121212;
            color: white;
            font-family: Arial, sans-serif;
        }
        canvas {
            max-height: 90vh;
        }
        .container {
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>📈 Vix25 (1m) - MT5 Style Chart</h2>
        <canvas id="candlestickChart"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('candlestickChart').getContext('2d');
        let chart;

        async function fetchData() {
            const res = await fetch("https://fir-8908c-default-rtdb.firebaseio.com/1minVix25.json");
            const rawData = await res.json();
            const entries = Object.values(rawData || {}).sort((a, b) => a.epoch - b.epoch);

            return entries.map(item => ({
                x: new Date(item.epoch * 1000),
                o: item.open,
                h: item.high,
                l: item.low,
                c: item.close
            }));
        }

        async function initChart() {
            const initialData = await fetchData();
            const candles = initialData.slice(-5); // show only last 5 to start

            chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: 'Vix25 1m',
                        data: candles,
                        borderColor: '#00e676',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'minute',
                                tooltipFormat: 'HH:mm'
                            },
                            ticks: {
                                color: '#ffffff'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#ffffff'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    }
                }
            });
        }

        async function pollForNewCandle() {
            setInterval(async () => {
                const data = await fetchData();
                const latest = data[data.length - 1];
                const lastPlotted = chart.data.datasets[0].data.at(-1);

                if (!lastPlotted || lastPlotted.x.getTime() !== latest.x.getTime()) {
                    chart.data.datasets[0].data.push(latest);
                    if (chart.data.datasets[0].data.length > 30) {
                        chart.data.datasets[0].data.shift(); // Keep chart clean
                    }
                    chart.update();
                }
            }, 5000); // poll every 5s
        }

        initChart().then(pollForNewCandle);
    </script>
</body>
</html>
"""

@app.route("/chart")
def chart():
    return render_template_string(CHART_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
