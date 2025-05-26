# web.py
from flask import Flask, render_template_string

app = Flask(__name__)

# Home Page HTML (static)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Deriv Ticks → Firebase</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #121212;
            color: white;
            text-align: center;
            padding: 50px;
        }
        .loader-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 40px;
        }
        .symbol {
            width: 100px;
            margin: 0 30px;
            animation: float 2s ease-in-out infinite;
        }
        .arrow {
            width: 60px;
            margin: 0 20px;
            animation: bounce 1s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        h1 {
            font-size: 28px;
            color: #00e676;
        }
        p {
            font-size: 18px;
            color: #bbbbbb;
        }
    </style>
</head>
<body>
    <h1>📡 Live Tick Streaming</h1>
    <p>Streaming <b>Deriv</b> tick data for <b>{{symbol}}</b> to <b>Firebase</b>...</p>

    <div class="loader-container">
        <img class="symbol" src="https://img.icons8.com/fluency/96/database.png" alt="Database" />
        <img class="arrow" src="https://img.icons8.com/ios-filled/50/00e676/right.png" alt="Arrow" />
        <img class="symbol" src="https://img.icons8.com/fluency/96/bar-chart.png" alt="Ticks" />
    </div>
</body>
</html>
"""

# Chart Page HTML (live candlestick)
CHART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MT5-style Vix25 Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@3.3.0"></script>
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
        h2 {
            color: #00e676;
            text-align: center;
            margin-bottom: 10px;
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
                        color: {
                            up: '#00e676',
                            down: '#ff3d00',
                            unchanged: '#999'
                        }
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
                        chart.data.datasets[0].data.shift();
                    }
                    chart.update();
                }
            }, 5000);
        }

        initChart().then(pollForNewCandle);
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, symbol="R_25")

@app.route("/chart")
def chart():
    return render_template_string(CHART_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
