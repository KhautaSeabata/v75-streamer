# web.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>Deriv Tick Collector is Running</h2><p>Check Firebase for live data.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
