import os
from flask import Flask, render_template_string, jsonify
from analyze import get_candles

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vix25 Candle Data Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 40px;
            background: #f9f9f9;
            color: #333;
            text-align: center;
        }
        .status {
            font-size: 24px;
            margin-top: 100px;
        }
    </style>
</head>
<body>
    <div class="status" id="status">Loading data...</div>

    <script>
        function checkDataStatus() {
            fetch('/candles')
                .then(response => response.json())
                .then(data => {
                    if (data && Array.isArray(data) && data.length > 0) {
                        document.getElementById("status").textContent = "Data Loaded ✅";
                    } else {
                        document.getElementById("status").textContent = "No Data Found ❌";
                    }
                })
                .catch(err => {
                    document.getElementById("status").textContent = "Error loading data ⚠️";
                });
        }

        checkDataStatus();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/candles")
def candles():
    data = get_candles()
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
    app.run(host="0.0.0.0", port=port, debug=True)
