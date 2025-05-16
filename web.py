from flask import Flask, render_template_string, jsonify
from analyze import get_candles  # This should still return your candle data

app = Flask(__name__)

<!DOCTYPE html>
<html>
<head>
    <title>Data Loading Status</title>
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
                    document.getElementById("status").textContent = "
