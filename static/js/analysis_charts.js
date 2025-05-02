/* ───────── Sentiment Distribution ─────────────────────────── */
if (document.getElementById("sentChart")) {
  fetch("/static/data/distribution.json")
    .then(r => r.json())
    .then(d => {
      const cfg = Array.isArray(d.datasets) ? d : {
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [{
          label: "Posts",
          backgroundColor: ["#4caf50", "#ffc107", "#f44336"],
          data: [320, 128, 45]
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
              callbacks: { label: ctx => `${ctx.label}: ${ctx.parsed.y} posts` }
            }
          },
          scales: {
            x: {                                     // <─ X‑axis
              title: {
                display: true,
                text: "Sentiment",
                font: { size: 16, weight: "bold" }
              }
            },
            y: {                                     // <─ Y‑axis
              beginAtZero: true,
              title: {
                display: true,
                text: "Number of Posts",
                font: { size: 16, weight: "bold" }
              }
            }
          }
        }
      });
    });
}

/* ───────── Scatter Retweets × Likes ───────────────────────── */
if (document.getElementById("scatterChart")) {
  fetch("/static/data/scatter.json").then(r => r.json()).then(rows => {
    const colours = { Positive:"#4caf50", Neutral:"#ffc107", Negative:"#f44336" };
    const buckets  = { Positive:[], Neutral:[], Negative:[] };

    rows.forEach(r=>{
      const sent = r.sentiment.charAt(0).toUpperCase()+r.sentiment.slice(1);
      if (sent in buckets) buckets[sent].push({x:r.retweets, y:r.likes});
    });

    const datasets = Object.entries(buckets).map(([label,data])=>({
      label, data,
      backgroundColor: colours[label],
      pointRadius:6, pointHoverRadius:8
    }));

    new Chart(scatterChart,{
      type:"scatter",
      data:{ datasets },
      options:{
        responsive:true,
        plugins:{ legend:{position:"top"} },
        scales:{
          x:{                                      // <─ X
            title:{ display:true, text:"Retweets", font:{size:16,weight:"bold"} }
          },
          y:{                                      // <─ Y
            title:{ display:true, text:"Likes",    font:{size:16,weight:"bold"} }
          }
        }
      }
    });
  });
}

/* ───────── Daily Post Volume (stacked bars) ───────────────── */
if (document.getElementById("timeChart")) {
  fetch("/static/data/timeseries.json").then(r=>r.json()).then(d=>{
    const lines = Object.keys(d.series).map(s=>({ label:s, data:d.series[s] }));
    new Chart(timeChart,{
      type:"bar",
      data:{ labels:d.dates, datasets:lines },
      options:{
        responsive:true,
        plugins:{ legend:{position:"top"} },
        scales:{
          x:{
            stacked:true,
            title:{ display:true, text:"Date", font:{size:16,weight:"bold"} }
          },
          y:{
            stacked:true,
            beginAtZero:true,
            title:{ display:true, text:"Posts per Day", font:{size:16,weight:"bold"} }
          }
        }
      }
    });
  });
}

/* ───────── Heat‑map (DOW × Hour) ──────────────────────────── */
if (document.getElementById("heatChart")) {
  Promise.all([
    import("https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@1.3.0"),
    fetch("/static/data/heatmap.json").then(r=>r.json())
  ]).then(([_,rows])=>{
    const dow = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
    new Chart(heatChart,{
      type:"matrix",
      data:{ datasets:[{
        label:"Median engagement",
        data:rows.map(r=>({ x:r.hour, y:dow.indexOf(r.dow),
                             v:(r.likes+r.retweets)/2 })),
        backgroundColor:ctx=>{
          const v=ctx.raw.v;
          return v>60?"#f44336":v>40?"#ff9800":v>20?"#ffc107":"#4caf50";
        },
        width:20,height:20
      }]},
      options:{
        plugins:{ legend:{display:false} },
        scales:{
          x:{
            type:"linear",
            ticks:{ stepSize:3, callback:v=>`${v}:00` },
            title:{ display:true, text:"Hour of Day", font:{size:16,weight:"bold"} }
          },
          y:{
            type:"linear",
            ticks:{ callback:i=>dow[i] },
            title:{ display:true, text:"Day of Week", font:{size:16,weight:"bold"} }
          }
        }
      }
    });
  });
}

/* ───────── Hourly avg Likes / Retweets line chart ─────────── */
if (document.getElementById("hourChart")) {
  fetch("/static/data/hourly.json").then(r=>r.json()).then(d=>{
    new Chart(hourChart,{
      type:"line",
      data:{
        labels:d.map(r=>`${r.Hour}:00`),
        datasets:[
          {label:"Likes",    data:d.map(r=>r.Likes),    borderWidth:2},
          {label:"Retweets", data:d.map(r=>r.Retweets), borderWidth:2}
        ]
      },
      options:{
        plugins:{ legend:{position:"top"} },
        scales:{
          x:{
            title:{ display:true, text:"Hour of Day", font:{size:16,weight:"bold"} }
          },
          y:{
            title:{ display:true, text:"Average Count", font:{size:16,weight:"bold"} },
            beginAtZero:true
          }
        }
      }
    });
  });
}

Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.color       = "#333";
Chart.defaults.plugins.legend.labels.boxWidth = 14;

