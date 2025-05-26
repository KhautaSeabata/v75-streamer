const firebaseURL = "https://fir-8908c-default-rtdb.firebaseio.com/1minVix25.json";

async function fetchCandles() {
    const res = await fetch(firebaseURL);
    const data = await res.json();
    const ohlc = Object.values(data || {});
    return ohlc.sort((a, b) => a.epoch - b.epoch).map(item => ({
        x: new Date(item.epoch * 1000),
        o: item.open,
        h: item.high,
        l: item.low,
        c: item.close
    }));
}

async function drawChart() {
    const ctx = document.getElementById("candlestickChart").getContext("2d");
    const candles = await fetchCandles();

    new Chart(ctx, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: 'VIX 25 - 1min',
                data: candles,
                borderColor: '#00e676',
                color: {
                    up: '#00e676',
                    down: '#ff5252',
                    unchanged: '#ccc'
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
                    adapters: {
                        date: {
                            locale: 'en-US'
                        }
                    }
                }
            }
        }
    });
}

drawChart();
