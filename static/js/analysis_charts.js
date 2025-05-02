if (document.getElementById("sentChart")) {
  fetch("/static/data/distribution.json")
    .then(r => r.json())
    .then(d => {
      const cfg = Array.isArray(d.datasets)              
        ? d                                         
        : {                                          
            labels: d.labels,
            datasets: [{
              label: "Sentiment Distribution",
              backgroundColor: ["#4caf50", "#ffc107", "#f44336"],
              data: d.counts
            }]
          };

          new Chart(sentChart, {
            type: "bar",
            data: cfg,
            options: {
              responsive: true,
              plugins: {
                legend: { display: false },
                tooltip: {
                  backgroundColor: "#1f1f1f",
                  titleColor: "#fff",
                  bodyColor: "#fff",
                  callbacks: {
                    label: ctx => ` ${ctx.parsed.y} posts`
                  }
                }
              },
              datasets: { bar: { borderRadius: 6 } },
              animation: { duration: 800, easing: "easeOutQuart" }
            }
          });          
    });
}

if (document.getElementById("scatterChart")) {
  fetch("/static/data/scatter.json")
    .then(r => r.json())
    .then(rows => {

      const colours = {
        Positive: "#4caf50",
        Neutral:  "#ffc107",
        Negative: "#f44336"
      };

      const buckets = { Positive: [], Neutral: [], Negative: [] };
      rows.forEach(r => buckets[r.sentiment].push({ x: r.retweets, y: r.likes }));

      const datasets = Object.keys(buckets).map(k => ({
        label: k,
        data:  buckets[k],
        backgroundColor: colours[k],
        pointRadius: 4
      }));

      new Chart(scatterChart, {
        type: "scatter",
        data: { datasets },
        options: {
          plugins: { legend: { position: "top" } },
          scales: {
            x: { title: { text: "Retweets" } },
            y: { title: { text: "Likes"    } }
          }
        }
      });
    });
}

if (document.getElementById("timeChart")) {
  fetch("/static/data/timeseries.json").then(r => r.json()).then(d => {
    const lines = Object.keys(d.series).map(sent => ({
      label: sent,
      data: d.series[sent]
    }));
    new Chart(timeChart, {
      type: "bar",
      data: { labels: d.dates, datasets: lines },
      options: {
        responsive:true,
        scales:{ x:{ stacked:true }, y:{ stacked:true, title:{text:"Posts"} } },
        plugins:{ legend:{ position:"top" } }
      }
    });
  });
}

if (document.getElementById("heatChart")) {
  Promise.all([
    import("https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@1.3.0"),
    fetch("/static/data/heatmap.json").then(r => r.json())
  ]).then(([_, rows]) => {

    const dow = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

    new Chart(heatChart, {
      type: "matrix",
      data: {
        datasets: [{
          label: "Median engagement",
          data: rows.map(r => ({
            x: r.hour,
            y: dow.indexOf(r.dow),
            v: (r.likes + r.retweets) / 2
          })),
          backgroundColor: ctx => {
            const v = ctx.raw.v;
            return v > 60 ? "#f44336" :
                   v > 40 ? "#ff9800" :
                   v > 20 ? "#ffc107" : "#4caf50";
          },
          width: 20,
          height: 20
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { type: "linear", ticks: { stepSize: 3, callback: v => `${v}:00` } },
          y: { type: "linear", ticks: { callback: i => dow[i] } }
        }
      }
    });
  });
}

if (document.getElementById("hourChart")) {
  fetch("/static/data/hourly.json")
    .then(r => r.json())
    .then(d => {
      new Chart(hourChart, {
        type: "line",
        data: {
          labels: d.map(r => `${r.Hour}:00`),
          datasets: [
            { label: "Likes",    data: d.map(r => r.Likes),    borderWidth: 2 },
            { label: "Retweets", data: d.map(r => r.Retweets), borderWidth: 2 }
          ]
        },
        options: {
          plugins:{legend:{position:"top"}},
          scales:{x:{title:{text:"Hour of Day"}},y:{title:{text:"Avg Count"}}}
        }
      });
    });
}

if (document.getElementById("platChart")) {
  fetch("/static/data/platform.json")
    .then(r => r.json())
    .then(d => {
      new Chart(platChart, {
        type: "doughnut",
        data: {
          labels: d.labels,
          datasets: [{
            data: d.data,
            backgroundColor: d.colors
          }]
        },
        options: {
          plugins: {
            legend: { position: "right" },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.label}: ${ctx.parsed} posts`
              }
            }
          }
        }
      });
    });
}

Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color = "#333";
Chart.defaults.plugins.legend.labels.boxWidth = 14;
