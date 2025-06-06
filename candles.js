const tickURL = "https://fir-8908c-default-rtdb.firebaseio.com/ticks/R_25.json?orderBy=\"epoch\"&limitToLast=100";
const oneMinURL = "https://fir-8908c-default-rtdb.firebaseio.com/1minVix25.json";
const fiveMinURL = "https://fir-8908c-default-rtdb.firebaseio.com/5minVix25.json";

const ctxLive = document.getElementById('liveTicksChart').getContext('2d');
const ctx1m = document.getElementById('candlestickChart1m').getContext('2d');
const ctx5m = document.getElementById('candlestickChart5m').getContext('2d');

// Live tick line chart
const liveTicksChart = new Chart(ctxLive, {
    type: 'line',
    data: {
        labels: [],
        datasets
