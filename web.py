from flask import Flask, render_template_string, jsonify
from main import send_telegram_message  # Optional if you want to trigger Telegram
from analyze import get_candles

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Signal Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 40px;
            background: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        #chart {
            width: 600px;
            height: 300px;
        }
        button {
            padding: 10px 20px;
            background-color: #6a1b9a;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #9c4d9d;
        }
    </style>
</head>
<body>
    <h1>Signal Dashboard</h1>

    <div id="chart">Loading chart...</div>

    <br><button onclick="sendHello()">Send Hello to Telegram</button>

    <script>
        function sendHello() {
            fetch('/send_hello', { method: 'GET' })
                .then(response => response.text())
                .then(data => alert(data))
                .catch(error => alert('Error sending message: ' + error));
        }

        function drawChart(data) {
            const timestamps = data.map(c => c.timestamp);
            const open = data.map(c => c.open);
            const high = data.map(c => c.high);
            const low = data.map(c => c.low);
            const close = data.map(c => c.close);

            const trace = {
                x: timestamps,
                open: open,
                high: high,
                low: low,
                close: close,
                type: 'candlestick',
                xaxis: 'x',
                yaxis: 'y'
            };

            const layout = {
                margin: { t: 20 },
                dragmode: false,
                xaxis: { type: 'category' },
                yaxis: { autorange: true }
            };

            Plotly.newPlot('chart', [trace], layout, { responsive: true });
        }

        function loadChart() {
            fetch('/candles')
                .then(response => response.json())
                .then(data => {
                    if (data && Array.isArray(data)) {
                        drawChart(data);
                    }
                })
                .catch(err => console.error("Error loading candle data:", err));
        }

        // Load chart every 60 seconds
        loadChart();
        setInterval(loadChart, 60000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send_hello', methods=['GET'])
def send_hello():
    try:
        send_telegram_message("Hello")  # Optional: requires Telegram bot integration
        return "Message sent to Telegram!"
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/candles', methods=['GET'])
def candles():
    try:
        return jsonify(get_candles())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
