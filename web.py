from flask import Flask, render_template_string, jsonify
from analyze import send_telegram_message, get_candles

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html><html><head><title>Signal Dashboard</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>body{font-family:Arial;padding:40px;background:#f4f4f4;}h1{color:#333}#chart{width:600px;height:300px}button{padding:10px 20px;background:#6a1b9a;color:#fff;border:none;border-radius:5px;cursor:pointer;}button:hover{background:#9c4d9d}</style></head>
<body><h1>Signal Dashboard</h1><div id="chart">Loading chart...</div><br>
<button onclick="sendHello()">Send Hello to Telegram</button>
<script>
function sendHello(){fetch('/send_hello').then(r=>r.text()).then(a=>alert(a)).catch(e=>alert('Error:'+e))}
function drawChart(d){const x=d.map(c=>c.timestamp),o=d.map(c=>c.open),h=d.map(c=>c.high),l=d.map(c=>c.low),c=d.map(c=>c.close);
Plotly.newPlot('chart',[{x:x,open:o,high:h,low:l,close:c,type:'candlestick'}],{margin:{t:20},dragmode:!1,xaxis:{type:'category'},yaxis:{autorange:!0}},{responsive:!0})}
function loadChart(){fetch('/candles').then(r=>r.json()).then(d=>Array.isArray(d)&&drawChart(d)).catch(e=>console.error("Error:",e))}
loadChart();setInterval(loadChart,60000);
</script></body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send_hello', methods=['GET'])
def send_hello():
    try:
        send_telegram_message("Hello from Dashboard!")
        return "Message sent to Telegram!"
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/candles', methods=['GET'])
def candles():
    try:
        return jsonify(get_candles())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
