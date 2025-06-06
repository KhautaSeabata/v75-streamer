const FIREBASE = "https://vix25-486b9-default-rtdb.firebaseio.com";


// ----------- LIVE TICKS -------------
const liveCtx = document.getElementById('liveTicksChart').getContext('2d');
const liveTicksChart = new Chart(liveCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Quote',
            data: [],
            borderColor: '#00e676',
            backgroundColor: 'rgba(0, 230, 118, 0.3)',
            fill: true,
            tension: 0.25,
            pointRadius: 0,
            borderWidth: 2
        }]
    },
    options: {
        animation: false,
        responsive: true,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'second',
                    displayFormats: {
                        second: 'HH:mm:ss'
                    }
                },
                ticks: { color: 'white' },
                grid: { color: '#333' }
            },
            y: {
                ticks: { color: 'white' },
                grid: { color: '#333' }
            }
        },
        plugins: {
            legend: {
                labels: { color: 'white' }
            }
        }
    }
});

async function fetchLiveTicks() {
    const res = await fetch(`${FIREBASE}/ticks/R_25.json?orderBy="epoch"&limitToLast=100`);
    const data = await res.json();
    if (!data) return;

    const ticks = Object.values(data).sort((a, b) => a.epoch - b.epoch);
    const labels = ticks.map(t => new Date(t.epoch * 1000));
    const quotes = ticks.map(t => t.quote);

    liveTicksChart.data.labels = labels;
    liveTicksChart.data.datasets[0].data = quotes;
    liveTicksChart.update();
}

setInterval(fetchLiveTicks, 5000);
fetchLiveTicks();

// ----------- CANDLE FETCHING -------------

async function fetchCandles(path) {
    const res = await fetch(`${FIREBASE}/${path}.json`);
    const data = await res.json();
    if (!data) return [];

    return Object.values(data)
        .sort((a, b) => a.epoch - b.epoch)
        .map(c => ({
            x: new Date(c.epoch * 1000),
            o: c.open,
            h: c.high,
            l: c.low,
            c: c.close
        }));
}

// ----------- 1-MIN CANDLES -------------
const ctx1min = document.getElementById("candlestickChart1min").getContext("2d");
let chart1min;
async function draw1MinChart() {
    const candles = await fetchCandles("1minVix25");
    chart1min = new Chart(ctx1min, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: '1-Min Candles',
                data: candles,
                color: {
                    up: '#00e676',
                    down: '#ff5252',
                    unchanged: '#999'
                }
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    time: { unit: 'minute' },
                    ticks: { color: 'white' },
                    grid: { color: '#333' }
                },
                y: {
                    ticks: { color: 'white' },
                    grid: { color: '#333' }
                }
            }
        }
    });
}

// ----------- 5-MIN CANDLES -------------
const ctx5min = document.getElementById("candlestickChart5min").getContext("2d");
let chart5min;
async function draw5MinChart() {
    const candles = await fetchCandles("5minVix25");
    chart5min = new Chart(ctx5min, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: '5-Min Candles',
                data: candles,
                color: {
                    up: '#00e676',
                    down: '#ff5252',
                    unchanged: '#999'
                }
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    time: { unit: 'minute' },
                    ticks: { color: 'white' },
                    grid: { color: '#333' }
                },
                y: {
                    ticks: { color: 'white' },
                    grid: { color: '#333' }
                }
            }
        }
    });
}

// Draw all charts
draw1MinChart();
draw5MinChart();
