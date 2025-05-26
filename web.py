# web.py
from flask import Flask, render_template_string, send_from_directory

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

@app.route("/")
def home():
    return render_template_string(HTML, symbol="R_25")

@app.route("/candles")
def candles():
    return send_from_directory(".", "candles.html")

@app.route("/candles.js")
def candles_js():
    return send_from_directory(".", "candles.js")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
