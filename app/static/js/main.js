/**
 * Student Dashboard – AJAX data loading & Chart.js visualisaties.
 *
 * TODO (FILTERS):
 *   Voeg hier de filterfunctionaliteit toe. Wat moet er gebeuren:
 *   1. Voeg een filter-sectie toe in student/dashboard.html met dropdowns voor
 *      vak (subject), leerdoel (learning_goal) en datumbereik (date_from / date_to).
 *   2. Schrijf een functie buildApiUrl() die de filterwaarden uitleest en als
 *      query-parameters toevoegt aan "/api/students/<id>".
 *      De API ondersteunt al: ?subject=, ?learning_goal=, ?date_from=, ?date_to=
 *   3. Koppel een click-event aan de "Filters Toepassen"-knop die loadData() aanroept.
 *   4. Vul de dropdowns dynamisch vanuit de API-data (vakken en leerdoelen).
 */

(function () {
  "use strict";

  var dashboard = document.getElementById("studentDashboard");
  if (!dashboard) return;

  var studentId = dashboard.dataset.studentId;
  if (!studentId) return;

  var progressChart = null;
  var goalsChart = null;
  var taxonomyChart = null;

  loadData();

  function loadData() {
    fetch("/api/students/" + studentId)
      .then(function (res) {
        if (!res.ok) throw new Error("API fout: " + res.status);
        return res.json();
      })
      .then(function (data) {
        var goals = data.learningGoals || [];

        renderStats(goals);
        renderProgressChart(goals);
        renderGoalsChart(goals);
        renderTaxonomyChart(goals);
      })
      .catch(function (err) {
        console.error(err);
      });
  }

  function renderStats(goals) {
    var totalSnapshots = 0;
    var avgScoreSum = 0;
    var weakPoints = 0;

    goals.forEach(function (g) {
      totalSnapshots += g.snapshots.length;

      var kenSum = 0,
        kunSum = 0,
        cnt = 0;
      g.snapshots.forEach(function (s) {
        s.taxonomy.forEach(function (t) {
          kenSum += t.kennen;
          kunSum += t.kunnen;
          cnt++;
        });
      });

      if (cnt > 0) {
        var avgKun = kunSum / cnt;
        avgScoreSum += (kenSum / cnt + avgKun) / 2;
        if (avgKun < 0.5) weakPoints++;
      }
    });

    var avgPct = goals.length
      ? Math.round((avgScoreSum / goals.length) * 100)
      : 0;

    document.getElementById("stat-snapshots").textContent = totalSnapshots;
    document.getElementById("stat-avg-score").textContent = avgPct + "%";
    document.getElementById("stat-goals").textContent = goals.length;
    document.getElementById("stat-weak").textContent = weakPoints;
  }

  function renderProgressChart(goals) {
    var dateMap = {};

    goals.forEach(function (g) {
      g.snapshots.forEach(function (s) {
        if (!dateMap[s.date]) {
          dateMap[s.date] = { kennenSum: 0, kunnenSum: 0, count: 0 };
        }
        s.taxonomy.forEach(function (t) {
          dateMap[s.date].kennenSum += t.kennen;
          dateMap[s.date].kunnenSum += t.kunnen;
          dateMap[s.date].count++;
        });
      });
    });

    var dates = Object.keys(dateMap).sort();

    var kennenData = dates.map(function (d) {
      return dateMap[d].count
        ? Math.round((dateMap[d].kennenSum / dateMap[d].count) * 100) / 100
        : 0;
    });
    var kunnenData = dates.map(function (d) {
      return dateMap[d].count
        ? Math.round((dateMap[d].kunnenSum / dateMap[d].count) * 100) / 100
        : 0;
    });

    if (progressChart) progressChart.destroy();

    var ctx = document.getElementById("progressChart").getContext("2d");
    progressChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Kennen",
            data: kennenData,
            borderColor: "#4a90d9",
            backgroundColor: "rgba(74, 144, 217, 0.1)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Kunnen",
            data: kunnenData,
            borderColor: "#e67e22",
            backgroundColor: "rgba(230, 126, 34, 0.1)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: {
            min: 0,
            max: 1,
            title: { display: true, text: "Score" },
          },
          x: {
            title: { display: true, text: "Datum" },
          },
        },
        plugins: {
          legend: { position: "top" },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.dataset.label + ": " + (ctx.parsed.y * 100).toFixed(0) + "%";
              },
            },
          },
        },
      },
    });
  }

  function renderGoalsChart(goals) {
    var labels = [];
    var kennenScores = [];
    var kunnenScores = [];

    goals.forEach(function (g) {
      labels.push(g.title.length > 30 ? g.title.substring(0, 30) + "\u2026" : g.title);

      var kenSum = 0,
        kunSum = 0,
        cnt = 0;
      g.snapshots.forEach(function (s) {
        s.taxonomy.forEach(function (t) {
          kenSum += t.kennen;
          kunSum += t.kunnen;
          cnt++;
        });
      });

      kennenScores.push(cnt ? Math.round((kenSum / cnt) * 100) : 0);
      kunnenScores.push(cnt ? Math.round((kunSum / cnt) * 100) : 0);
    });

    if (goalsChart) goalsChart.destroy();

    var ctx = document.getElementById("goalsChart").getContext("2d");
    goalsChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Kennen %",
            data: kennenScores,
            backgroundColor: "#4a90d9",
          },
          {
            label: "Kunnen %",
            data: kunnenScores,
            backgroundColor: "#e67e22",
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        scales: {
          x: {
            min: 0,
            max: 100,
            title: { display: true, text: "Score %" },
          },
        },
        plugins: {
          legend: { position: "top" },
        },
      },
    });
  }

  function renderTaxonomyChart(goals) {
    var levels = ["Onthouden", "Begrijpen", "Toepassen", "Analyseren"];
    var kennenByLevel = {};
    var kunnenByLevel = {};
    var countByLevel = {};

    levels.forEach(function (l) {
      kennenByLevel[l] = 0;
      kunnenByLevel[l] = 0;
      countByLevel[l] = 0;
    });

    goals.forEach(function (g) {
      g.snapshots.forEach(function (s) {
        s.taxonomy.forEach(function (t) {
          if (kennenByLevel.hasOwnProperty(t.level)) {
            kennenByLevel[t.level] += t.kennen;
            kunnenByLevel[t.level] += t.kunnen;
            countByLevel[t.level]++;
          }
        });
      });
    });

    var kennenData = levels.map(function (l) {
      return countByLevel[l]
        ? Math.round((kennenByLevel[l] / countByLevel[l]) * 100) / 100
        : 0;
    });
    var kunnenData = levels.map(function (l) {
      return countByLevel[l]
        ? Math.round((kunnenByLevel[l] / countByLevel[l]) * 100) / 100
        : 0;
    });

    if (taxonomyChart) taxonomyChart.destroy();

    var ctx = document.getElementById("taxonomyChart").getContext("2d");
    taxonomyChart = new Chart(ctx, {
      type: "radar",
      data: {
        labels: levels,
        datasets: [
          {
            label: "Kennen",
            data: kennenData,
            borderColor: "#4a90d9",
            backgroundColor: "rgba(74, 144, 217, 0.2)",
            pointBackgroundColor: "#4a90d9",
          },
          {
            label: "Kunnen",
            data: kunnenData,
            borderColor: "#e67e22",
            backgroundColor: "rgba(230, 126, 34, 0.2)",
            pointBackgroundColor: "#e67e22",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          r: {
            min: 0,
            max: 1,
            ticks: {
              stepSize: 0.2,
              callback: function (v) {
                return (v * 100).toFixed(0) + "%";
              },
            },
          },
        },
        plugins: {
          legend: { position: "top" },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.dataset.label + ": " + (ctx.parsed.r * 100).toFixed(0) + "%";
              },
            },
          },
        },
      },
    });
  }
})();
