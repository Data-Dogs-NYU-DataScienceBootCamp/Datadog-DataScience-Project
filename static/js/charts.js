

// ─── build chart only if we're on the Charts page ────────────────
const canvas = document.getElementById("sentChart");
if (canvas) {
  fetch("/static/data/distribution.json")
    .then(r => r.json())
    .then(d => {
      new Chart(canvas, {
        type: "bar",
        data: {
          labels: d.labels, 
          datasets: [{
            label: "Sentiment Distribution",
            data: d.datasets[0].data,  
            backgroundColor: d.datasets[0].backgroundColor,
            borderRadius: 6,
            barThickness: 50
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            datalabels: {
              anchor: 'end',
              align: 'top',
              color: '#333',
              font: {
                weight: 'bold',
                size: 14
              },
              formatter: value => `${value}`
            },
            tooltip: {
              callbacks: {
                label: context => ` ${context.label}: ${context.parsed.y}`
              }
            }
          },
          scales: {
            x: {
              ticks: { font: { size: 14 } },
              grid: { display: false }
            },
            y: {
              beginAtZero: true,
              ticks: { font: { size: 14 } }
            }
          }
        },
        plugins: [ChartDataLabels]
      });
    })
    .catch(err => console.error("Chart load error:", err));
}


// ─── live sentiment (Sentiment Analysis page) ───────────────────
async function checkSent() {
  const txt = document.getElementById("postTxt").value;
  const res = await fetch("/api/sentiment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: txt })
  });
  if (!res.ok) { alert("API error"); return; }
  const j = await res.json();
  document.getElementById("mood").innerHTML =
  `<span class="emoji">${j.emoji}</span>
   <span class="label">${j.label.toUpperCase()} ${(j.score*100).toFixed(1)}%</span>`;

}

// ─── next-word generator ────────────────────────────────────────
async function genText() {
  const seed = document.getElementById("seedTxt").value;
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seed })
  });
  if (!res.ok) { alert("API error"); return; }
  const j = await res.json();
  document.getElementById("genOut").innerText = j.generated;
}

// ─── caption generator ────────────────────────────────────────
async function genCaption() {
  const keywords = document.getElementById("keywordsTxt").value;
  const res = await fetch("/api/caption", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keywords })
  });
  if (!res.ok) { alert("API error"); return; }
  const j = await res.json();
  document.getElementById("captionOut").innerText = j.caption;
}
