const calorieLineChart = document.getElementById("calorieLineChart");

// Apply progress widths from data attributes so HTML stays style-free.
document.querySelectorAll(".stats-progress-fill[data-progress]").forEach((bar) => {
  const progress = Number.parseFloat(bar.dataset.progress || "0") || 0;
  bar.style.width = `${Math.max(0, Math.min(progress, 100))}%`;
});

if (calorieLineChart && typeof Chart !== "undefined") {
  // Read styling and data from the DOM before building the weekly chart.
  const chartStyles = getComputedStyle(calorieLineChart);
  const chartLabels = JSON.parse(calorieLineChart.dataset.labels || "[]");
  const chartValues = JSON.parse(calorieLineChart.dataset.values || "[]");
  const chartMax = Number.parseFloat(calorieLineChart.dataset.max || "0") || 0;
  const chartBarBorderWidth =
    Number.parseFloat(chartStyles.getPropertyValue("--stats-bar-border-width")) || 1.5;
  const chartBarRadius =
    Number.parseFloat(chartStyles.getPropertyValue("--stats-bar-radius")) || 10;
  const chartAnimationDuration =
    Number.parseInt(chartStyles.getPropertyValue("--stats-animation-duration"), 10) || 700;
  const chartAxisFontFamily =
    chartStyles.getPropertyValue("--stats-axis-font-family").trim() || "DM Sans";
  const chartAxisFontSizeX =
    Number.parseInt(chartStyles.getPropertyValue("--stats-axis-font-size-x"), 10) || 12;
  const chartAxisFontSizeY =
    Number.parseInt(chartStyles.getPropertyValue("--stats-axis-font-size-y"), 10) || 11;
  const chartAxisFontWeightX =
    chartStyles.getPropertyValue("--stats-axis-font-weight-x").trim() || "600";

  new Chart(calorieLineChart, {
    type: "line",
    data: {
      labels: chartLabels,
      datasets: [
        {
          label: "Calories",
          data: chartValues,
          backgroundColor: chartStyles.getPropertyValue("--stats-bar-fill").trim(),
          borderColor: chartStyles.getPropertyValue("--stats-bar-border").trim(),
          borderWidth: chartBarBorderWidth,
          fill: false,
          tension: 0,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: chartStyles.getPropertyValue("--stats-bar-border").trim(),
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointHoverBackgroundColor: chartStyles.getPropertyValue("--stats-bar-hover").trim(),
          pointHoverBorderColor: "#ffffff",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: chartAnimationDuration,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          displayColors: false,
          intersect: false,
          mode: "index",
          callbacks: {
            label(context) {
              return `${context.parsed.y} kcal`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: chartStyles.getPropertyValue("--stats-grid-line").trim(),
            drawBorder: false,
          },
          ticks: {
            color: chartStyles.getPropertyValue("--stats-axis-text").trim(),
            font: {
              family: chartAxisFontFamily,
              size: chartAxisFontSizeX,
              weight: chartAxisFontWeightX,
            },
          },
          border: {
            color: chartStyles.getPropertyValue("--stats-axis-line").trim(),
          },
        },
        y: {
          beginAtZero: true,
          suggestedMax: chartMax,
          ticks: {
            color: chartStyles.getPropertyValue("--stats-axis-text").trim(),
            stepSize: Math.max(Math.ceil(chartMax / 4), 1),
            callback(value) {
              return `${value} kcal`;
            },
            font: {
              family: chartAxisFontFamily,
              size: chartAxisFontSizeY,
            },
          },
          grid: {
            color: chartStyles.getPropertyValue("--stats-grid-line").trim(),
            drawBorder: false,
          },
          border: {
            color: chartStyles.getPropertyValue("--stats-axis-line").trim(),
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
    },
  });
}
