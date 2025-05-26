from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

# Existing home route...
@app.route("/")
def home():
    # unchanged...

# ✅ Add this new route
@app.route("/candles")
def candles():
    return send_from_directory(".", "candles.html")

@app.route("/candles.js")
def candles_js():
    return send_from_directory(".", "candles.js")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
