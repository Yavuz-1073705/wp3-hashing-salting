/**
 * Student Dashboard – AJAX data loading & Chart.js visualisaties.
 * Filters (vak, leerdoel, kernwoord, datumbereik) worden asynchroon
 * toegepast via query-parameters op /api/students/<id>.
 */

(function () {
  "use strict";

  var dashboard = document.getElementById("studentDashboard");
  if (!dashboard) return;

  var studentId = dashboard.dataset.studentId;
  if (!studentId) return;

  var progressChart = null;
  var taxonomyChart = null;
  var dropdownsPopulated = false;

  // ---- UI helpers --------------------------------------------------------

  function showLoading() {
    var el = document.getElementById("filter-loading");
    if (el) el.hidden = false;
  }

  function hideLoading() {
    var el = document.getElementById("filter-loading");
    if (el) el.hidden = true;
  }

  function showNoResults(msg) {
    var el = document.getElementById("filter-no-results");
    if (!el) return;
    if (msg) el.innerHTML = msg;
    el.hidden = false;
  }

  function clearNoResults() {
    var el = document.getElementById("filter-no-results");
    if (el) el.hidden = true;
  }

  function clearAllFilters() {
    var ids = ["filter-subject", "filter-learning-goal", "filter-keyword",
               "filter-date-from", "filter-date-to"];
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.value = "";
    });
    clearNoResults();
  }

  // ---- Initialise --------------------------------------------------------

  loadData();

  var applyFiltersBtn = document.getElementById("apply-filters-btn");
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener("click", function () {
      clearNoResults();
      loadData();
    });
  }

  var resetFiltersBtn = document.getElementById("reset-filters-btn");
  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener("click", function () {
      clearAllFilters();
      loadData();
    });
  }

  function buildApiUrl() {
    var baseUrl = "/api/students/" + studentId;
    var params = [];

    var subject = document.getElementById("filter-subject");
    var learningGoal = document.getElementById("filter-learning-goal");
    var keyword = document.getElementById("filter-keyword");
    var dateFrom = document.getElementById("filter-date-from");
    var dateTo = document.getElementById("filter-date-to");

    if (subject && subject.value) {
      params.push("subject=" + encodeURIComponent(subject.value));
    }
    if (learningGoal && learningGoal.value) {
      params.push("learning_goal=" + encodeURIComponent(learningGoal.value));
    }
    if (keyword && keyword.value) {
      params.push("keyword=" + encodeURIComponent(keyword.value));
    }
    if (dateFrom && dateFrom.value) {
      params.push("date_from=" + encodeURIComponent(dateFrom.value));
    }
    if (dateTo && dateTo.value) {
      params.push("date_to=" + encodeURIComponent(dateTo.value));
    }

    return params.length ? baseUrl + "?" + params.join("&") : baseUrl;
  }

  function populateFilterDropdowns(goals) {
    var subjects = {};
    var learningGoals = {};
    var keywords = {};

    goals.forEach(function (g) {
      if (g.subject && g.subject.name) subjects[g.subject.name] = true;
      learningGoals[g.title] = true;
      (g.keywords || []).forEach(function (w) { keywords[w] = true; });
    });

    var subjectSelect = document.getElementById("filter-subject");
    var goalSelect = document.getElementById("filter-learning-goal");
    var kwSelect = document.getElementById("filter-keyword");

    if (subjectSelect) {
      while (subjectSelect.options.length > 1) {
        subjectSelect.remove(1);
      }
      Object.keys(subjects).sort().forEach(function (subject) {
        var option = document.createElement("option");
        option.value = subject;
        option.textContent = subject;
        subjectSelect.appendChild(option);
      });
    }

    if (goalSelect) {
      while (goalSelect.options.length > 1) {
        goalSelect.remove(1);
      }
      Object.keys(learningGoals).sort().forEach(function (goal) {
        var option = document.createElement("option");
        option.value = goal;
        option.textContent = goal.length > 40 ? goal.substring(0, 40) + "..." : goal;
        goalSelect.appendChild(option);
      });
    }

    if (kwSelect) {
      while (kwSelect.options.length > 1) {
        kwSelect.remove(1);
      }
      Object.keys(keywords).sort().forEach(function (word) {
        var option = document.createElement("option");
        option.value = word;
        option.textContent = word;
        kwSelect.appendChild(option);
      });
    }
  }

  function loadData() {
    var apiUrl = buildApiUrl();
    showLoading();
    clearNoResults();

    fetch(apiUrl)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        hideLoading();
        var goals = data.learningGoals || [];

        if (!dropdownsPopulated) {
          // populate dropdowns once from the unfiltered initial load
          populateFilterDropdowns(goals);
          dropdownsPopulated = true;
        }

        if (!goals.length) {
          showNoResults(
            "Geen resultaten gevonden voor de gekozen filters. " +
            "Pas je filters aan of klik op <strong>Reset</strong> om alle data te bekijken."
          );
          renderStats([]);
          renderProgressChart([]);
          renderGoalsList([]);
          renderTaxonomyChart([]);
          return;
        }

        renderStats(goals);
        renderProgressChart(goals);
        renderGoalsList(goals);
        renderTaxonomyChart(goals);
      })
      .catch(function (err) {
        hideLoading();
        showNoResults(
          "Er is een fout opgetreden bij het ophalen van de gegevens. " +
          "Probeer het opnieuw of neem contact op met de beheerder."
        );
        console.error("loadData fout:", err);
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

  function renderGoalsList(goals) {
    var container = document.getElementById("learning-goals-list");

    if (!goals.length) {
      container.innerHTML =
        '<p class="no-data-message">Er zijn nog geen leerdoelen beschikbaar voor deze student.</p>';
      return;
    }

    var html = "";
    goals.forEach(function (g) {
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

      var avgKen = cnt ? kenSum / cnt : 0;
      var avgKun = cnt ? kunSum / cnt : 0;
      var kenPct = Math.round(avgKen * 100);
      var kunPct = Math.round(avgKun * 100);

      var cssClass =
        avgKun >= 0.75
          ? "goal-strong"
          : avgKun >= 0.5
          ? "goal-moderate"
          : "goal-weak";
      var badge =
        avgKun >= 0.75
          ? "&#10003; Sterk"
          : avgKun >= 0.5
          ? "~ Gemiddeld"
          : "! Zwak";

      var subjectHtml = g.subject
        ? '<div class="goal-subject">Gerelateerd aan: <strong>' + escapeHtml(g.subject.name) + "</strong></div>"
        : "";

      var kwHtml = "";
      if (g.keywords && g.keywords.length) {
        kwHtml = '<div class="goal-keyword-tags">';
        g.keywords.forEach(function (w) {
          kwHtml += '<span class="goal-keyword-tag">' + escapeHtml(w) + "</span>";
        });
        kwHtml += "</div>";
      }

      html +=
        '<div class="goal-card ' + cssClass + '">' +
          '<div class="goal-header">' +
            "<h3>" + escapeHtml(g.title) + "</h3>" +
            '<span class="goal-status-badge">' + badge + "</span>" +
          "</div>" +
          subjectHtml +
          kwHtml +
          '<div class="goal-scores">' +
            '<div class="score-item">' +
              '<span class="score-label">Kennen:</span>' +
              '<div class="progress-bar"><div class="progress-fill" style="width:' + kenPct + '%"></div></div>' +
              '<span class="score-percentage">' + kenPct + "%</span>" +
            "</div>" +
            '<div class="score-item">' +
              '<span class="score-label">Kunnen:</span>' +
              '<div class="progress-bar"><div class="progress-fill" style="width:' + kunPct + '%"></div></div>' +
              '<span class="score-percentage">' + kunPct + "%</span>" +
            "</div>" +
          "</div>" +
        "</div>";
    });

    container.innerHTML = html;
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }
})();
