// Firebase Config (replace with your actual project config)
const firebaseConfig = {
  databaseURL: "https://fir-8908c-default-rtdb.firebaseio.com"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.database();

const ctx = document.getElementById("chart").getContext("2d");
let chart;

function formatData(snapshot) {
  const data = snapshot.val();
  if (!data) return [];

  return Object.values(data)
    .filter(candle => candle.open !== undefined)
    .sort((a, b) => a.epoch - b.epoch)
    .map(candle => ({
      x: new Date(candle.epoch * 1000),
      o: candle.open,
      h: candle.high,
      l: candle.low,
      c: candle.close
    }));
}

function loadChart(data) {
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'candlestick',
    data: {
      datasets: [{
        label: 'Vix25',
        data: data,
        borderColor: '#00e676',
        color: {
          up: '#00e676',
          down: '#ff1744',
          unchanged: '#888'
        }
      }]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          type: 'time',
          time: {
            tooltipFormat: 'MMM dd HH:mm',
            unit: 'minute'
          },
          ticks: { color: '#fff' },
          grid: { color: '#444' }
        },
        y: {
          ticks: { color: '#fff' },
          grid: { color: '#444' }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#fff' }
        }
      }
    }
  });
}

function fetchAndRender(timeframe) {
  const ref = db.ref(timeframe);
  ref.once("value", snapshot => {
    const chartData = formatData(snapshot);
    loadChart(chartData);
  });
}

document.getElementById("timeframe").addEventListener("change", e => {
  fetchAndRender(e.target.value);
});

// Load default
fetchAndRender("1minVix25");
