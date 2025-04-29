/*  1. sentiment bar  (already existed)  */
if (document.getElementById("sentChart")) {
    fetch("/static/data/distribution.json")
      .then(r=>r.json())
      .then(d=>{
        new Chart(sentChart, {
          type:"bar",
          data:{labels:d.labels, datasets:[{data:d.counts}]}
        });
      });
  }
  
  /*  2. scatter: retweets vs likes */
  if (document.getElementById("scatterChart")) {
    fetch("/static/data/scatter.json").then(r=>r.json()).then(rows=>{
      constColours = {Positive:"#4caf50",Neutral:"#ff9800",Negative:"#f44336"};
      new Chart(scatterChart,{
        type:"scatter",
        data:{
          datasets: rows.map(r=>({
            x:r.Retweets, y:r.Likes,
            backgroundColor: constColours[r.Sentiment] || "#2196f3",
            radius:3
          }))
        },
        options:{scales:{x:{title:{text:"Retweets"}},y:{title:{text:"Likes"}}}}
      });
    });
  }
  
  /*  3. time-series line */
  if (document.getElementById("timeChart")) {
    fetch("/static/data/timeseries.json").then(r=>r.json()).then(d=>{
      const lines = Object.keys(d.series).map(sent=>({
          label:sent,
          data:d.dates.map(date=>d.series[sent][date]||0)
      }));
      new Chart(timeChart,{
        type:"line",
        data:{labels:d.dates, datasets:lines},
        options:{responsive:true, tension:0.3}
      });
    });
  }
  
  /*  4. heat-map   */
  if (document.getElementById("heatChart")) {
    Promise.all([
      import("https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@1.3.0"),  // plugin
      fetch("/static/data/heatmap.json").then(r=>r.json())
    ]).then(([_, rows])=>{
      const dowOrder = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
      new Chart(heatChart,{
        type:"matrix",
        data:{
          datasets:[{
            data: rows.map(r=>({
               x:r.Hour, y:dowOrder.indexOf(r.DOW),
               v: (r.Likes+r.Retweets)/2         // median engagement
            }))
          }]
        },
        options:{
          scales:{x:{type:"linear",ticks:{stepSize:3}},y:{type:"linear",
                 ticks:{callback:i=>dowOrder[i]}}}
        }
      });
    });
  }
  