from flask import Flask, render_template_string, jsonify
from analyze import get_candles  # Your function to get candles data for the chart

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

    <br><button onclick="alert('Telegram disabled, data is only stored in Firebase.')">Send Hello to Telegram</button>

    <script>
        function drawChart(data) {
            const timestamps = data.map(c => c.timestamp);
            const closePrices = data.map(c => c.close);

            const trace = {
                x: timestamps,
                y: closePrices,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: 'blue' },
                marker: { size: 4 }
            };

            const layout = {
                margin: { t: 20 },
                title: 'Close Price Over Time',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Close Price', autorange: true }
            };

            Plotly.newPlot('chart', [trace], layout, { responsive: true });
        }

        function loadChart() {
            fetch('/candles')
                .then(response => response.json())
                .then(data
