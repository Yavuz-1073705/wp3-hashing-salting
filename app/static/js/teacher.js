(function () {
  "use strict";

  var C_KENNEN = "#1B3A5C";   // dark navy  — for Kennen in all charts & bars
  var C_KUNNEN = "#4A90C4";   // slate-blue — for Kunnen in all charts & bars

  var statsSection = document.getElementById("stat-students");
  if (!statsSection) return;

  var classGoalsChart = null;
  var classTaxonomyChart = null;

  loadClassData();

  function loadClassData() {
    fetch("/api/class-overview")
      .then(function (res) {
        if (!res.ok) throw new Error("API fout: " + res.status);
        return res.json();
      })
      .then(function (data) {
        renderStats(data.stats);
        renderGoalsChart(data.learning_goals);
        renderTaxonomyChart(data.taxonomy_levels);
        renderStudentsTable(data.students);
        renderKeywords(data.keywords);
      })
      .catch(function (err) {
        console.error("Klasoverzicht kon niet worden geladen:", err);
      });
  }

  function renderStats(stats) {
    document.getElementById("stat-students").textContent = stats.total_students;
    document.getElementById("stat-class-avg").textContent =
      Math.round(stats.class_avg_kunnen * 100) + "%";
    document.getElementById("stat-weak-goals").textContent = stats.weak_goals_count;
    document.getElementById("stat-problem-kw").textContent = stats.problem_keywords_count;
  }

  function renderGoalsChart(goals) {
    var topGoals = goals.slice(0, 10);
    var labels = topGoals.map(function (g) {
      return g.title.length > 35 ? g.title.substring(0, 35) + "\u2026" : g.title;
    });
    var kennenData = topGoals.map(function (g) {
      return Math.round(g.avg_kennen * 100);
    });
    var kunnenData = topGoals.map(function (g) {
      return Math.round(g.avg_kunnen * 100);
    });

    if (classGoalsChart) classGoalsChart.destroy();

    var ctx = document.getElementById("classGoalsChart").getContext("2d");
    classGoalsChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Kennen %",
            data: kennenData,
            backgroundColor: C_KENNEN,
          },
          {
            label: "Kunnen %",
            data: kunnenData,
            backgroundColor: C_KUNNEN,
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
          tooltip: {
            callbacks: {
              label: function (ctx) {
                return ctx.dataset.label + ": " + ctx.parsed.x + "%";
              },
            },
          },
        },
      },
    });
  }

  function renderTaxonomyChart(levels) {
    var labels = levels.map(function (l) { return l.level; });
    var kennenData = levels.map(function (l) { return l.avg_kennen; });
    var kunnenData = levels.map(function (l) { return l.avg_kunnen; });

    if (classTaxonomyChart) classTaxonomyChart.destroy();

    var ctx = document.getElementById("classTaxonomyChart").getContext("2d");
    classTaxonomyChart = new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Kennen",
            data: kennenData,
            borderColor: C_KENNEN,
            backgroundColor: "rgba(27, 58, 92, 0.12)",
            pointBackgroundColor: C_KENNEN,
          },
          {
            label: "Kunnen",
            data: kunnenData,
            borderColor: C_KUNNEN,
            backgroundColor: "rgba(74, 144, 196, 0.15)",
            pointBackgroundColor: C_KUNNEN,
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
                return (
                  ctx.dataset.label +
                  ": " +
                  (ctx.parsed.r * 100).toFixed(0) +
                  "%"
                );
              },
            },
          },
        },
      },
    });
  }

  function renderStudentsTable(students) {
    var container = document.getElementById("students-overview-table");

    if (!students.length) {
      container.innerHTML =
        '<p class="no-data-message">Geen leerlingen gevonden.</p>';
      return;
    }

    var withData = students.filter(function (s) {
      return s.snapshot_count > 0;
    });
    var classAvg =
      withData.length
        ? withData.reduce(function (acc, s) {
            return acc + s.avg_kunnen;
          }, 0) / withData.length
        : 0;

    var sorted = students.slice().sort(function (a, b) {
      return b.avg_kunnen - a.avg_kunnen;
    });

    var html =
      '<table class="students-table">' +
      "<thead><tr>" +
      "<th>Leerling</th>" +
      "<th>Kennen</th>" +
      "<th>Kunnen</th>" +
      "<th>Snapshots</th>" +
      "<th>Status</th>" +
      "</tr></thead><tbody>";

    sorted.forEach(function (s) {
      var kunPct = Math.round(s.avg_kunnen * 100);
      var kenPct = Math.round(s.avg_kennen * 100);
      var isWeak = s.avg_kunnen < classAvg * 0.85;
      var isStrong = s.avg_kunnen > classAvg * 1.15;
      var rowClass = isWeak ? "row-weak" : isStrong ? "row-strong" : "";
      var badgeClass = isWeak
        ? "badge-weak"
        : isStrong
        ? "badge-strong"
        : "badge-avg";
      var statusText = isWeak
        ? "! Achterlopen"
        : isStrong
        ? "+ Uitblinken"
        : "~ Gemiddeld";

      html +=
        '<tr class="' +
        rowClass +
        '">' +
        '<td><a href="/student/dashboard/' +
        s.id +
        '">' +
        escapeHtml(s.name) +
        "</a></td>" +
        "<td>" +
        '<div class="table-score-row">' +
        '<div class="progress-bar small"><div class="progress-fill" style="width:' +
        kenPct +
        '%"></div></div>' +
        '<span class="score-percentage">' +
        kenPct +
        "%</span>" +
        "</div>" +
        "</td>" +
        "<td>" +
        '<div class="table-score-row">' +
        '<div class="progress-bar small"><div class="progress-fill" style="width:' +
        kunPct +
        '%"></div></div>' +
        '<span class="score-percentage">' +
        kunPct +
        "%</span>" +
        "</div>" +
        "</td>" +
        "<td>" +
        s.snapshot_count +
        "</td>" +
        '<td><span class="student-status-badge ' +
        badgeClass +
        '">' +
        statusText +
        "</span></td>" +
        "</tr>";
    });

    html += "</tbody></table>";
    container.innerHTML = html;
  }

  function renderKeywords(keywords) {
    var container = document.getElementById("class-keywords-list");

    if (!keywords.length) {
      container.innerHTML =
        '<p class="no-data-message">Geen kernwoorden gevonden.</p>';
      return;
    }

    var html = '<div class="kw-cloud">';
    keywords.forEach(function (kw) {
      var pct = Math.round(kw.avg_score * 100);
      var status =
        kw.avg_score >= 0.75
          ? "strong"
          : kw.avg_score >= 0.5
          ? "moderate"
          : "weak";

      html +=
        '<span class="kw-pill kw-pill-' + status + '" title="Gemiddelde score: ' + pct + '%">' +
        escapeHtml(kw.word) +
        '<span class="kw-pill-score">' + pct + '%</span>' +
        '</span>';
    });
    html += "</div>";

    container.innerHTML = html;
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }
})();
