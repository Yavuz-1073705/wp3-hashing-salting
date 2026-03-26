(function () {
  "use strict";

  var C_KENNEN = "#1B3A5C";   // dark navy  — for Kennen in all charts & bars
  var C_KUNNEN = "#4A90C4";   // slate-blue — for Kunnen in all charts & bars

  var statsSection = document.getElementById("stat-students");
  if (!statsSection) return;

  var classFilterSelect = document.getElementById("class-filter-select");
  var createClassForm = document.getElementById("create-class-form");
  var newClassNameInput = document.getElementById("new-class-name");
  var classFeedback = document.getElementById("class-feedback");

  var classGoalsChart = null;
  var classTaxonomyChart = null;
  var classes = [];

  bindEvents();
  initializeDashboard();

  function bindEvents() {
    if (classFilterSelect) {
      classFilterSelect.addEventListener("change", function () {
        loadClassData();
      });
    }

    if (createClassForm) {
      createClassForm.addEventListener("submit", function (event) {
        event.preventDefault();
        var className = (newClassNameInput && newClassNameInput.value || "").trim();
        if (!className) {
          showFeedback("Voer een klasnaam in.", "error");
          return;
        }

        createClass(className)
          .then(function () {
            showFeedback("Klas toegevoegd.", "success");
            if (newClassNameInput) newClassNameInput.value = "";
            return loadClasses();
          })
          .then(function () {
            return loadClassData();
          })
          .catch(function (err) {
            showFeedback(err.message || "Klas kon niet worden aangemaakt.", "error");
          });
      });
    }
  }

  function initializeDashboard() {
    loadClasses()
      .then(function () {
        return loadClassData();
      })
      .catch(function (err) {
        console.error("Klaslijst kon niet worden geladen:", err);
        showFeedback("Klaslijst laden is mislukt.", "error");
        loadClassData();
      });
  }

  function getSelectedClassId() {
    if (!classFilterSelect || !classFilterSelect.value) return null;
    return classFilterSelect.value;
  }

  function buildClassOverviewUrl() {
    var selectedClassId = getSelectedClassId();
    var url = "/api/class-overview";
    if (selectedClassId) {
      url += "?class_id=" + encodeURIComponent(selectedClassId);
    }
    return url;
  }

  function loadClasses() {
    return fetch("/api/classes")
      .then(function (res) {
        if (!res.ok) throw new Error("API fout: " + res.status);
        return res.json();
      })
      .then(function (data) {
        classes = Array.isArray(data) ? data : [];
        renderClassFilterOptions();
      });
  }

  function renderClassFilterOptions() {
    if (!classFilterSelect) return;
    var previouslySelected = classFilterSelect.value;

    var html = '<option value="">Alle klassen</option>';
    classes.forEach(function (c) {
      html +=
        '<option value="' +
        c.id +
        '">' +
        escapeHtml(c.name) +
        ' (' +
        c.student_count +
        ')</option>';
    });
    classFilterSelect.innerHTML = html;

    if (previouslySelected) {
      var stillExists = classes.some(function (c) {
        return String(c.id) === String(previouslySelected);
      });
      classFilterSelect.value = stillExists ? previouslySelected : "";
    }
  }

  function createClass(name) {
    return fetch("/api/classes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name }),
    }).then(function (res) {
      if (!res.ok) {
        return res
          .json()
          .catch(function () { return {}; })
          .then(function (err) {
            throw new Error(err.error || "Klas aanmaken mislukt.");
          });
      }
      return res.json();
    });
  }

  function loadClassData() {
    fetch(buildClassOverviewUrl())
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
        showFeedback("Klasoverzicht laden is mislukt.", "error");
      });
  }

  function showFeedback(message, kind) {
    if (!classFeedback) return;
    classFeedback.textContent = message;
    classFeedback.hidden = false;
    classFeedback.classList.remove("is-success", "is-error");
    classFeedback.classList.add(kind === "success" ? "is-success" : "is-error");
  }

  function renderStats(stats) {
    if (!stats) return;
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
            label: "Kennen",
            data: kennenData,
            backgroundColor: C_KENNEN,
            borderRadius: 3,
            barThickness: 10,
          },
          {
            label: "Kunnen",
            data: kunnenData,
            backgroundColor: C_KUNNEN,
            borderRadius: 3,
            barThickness: 10,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            min: 0,
            max: 100,
            border: { display: false },
            ticks: {
              callback: function (v) { return v + "%"; },
              color: "#94a3b8",
              font: { size: 11 },
            },
            grid: { color: "rgba(0,0,0,0.04)" },
          },
          y: {
            border: { display: false },
            ticks: {
              color: "#475569",
              font: { size: 11 },
            },
            grid: { display: false },
          },
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              usePointStyle: true, pointStyle: "circle", boxWidth: 8, boxHeight: 8, color: "#475569", font: { size: 11 }, padding: 16,
            },
          },
          tooltip: {
            backgroundColor: "rgba(15,23,42,0.8)",
            padding: 10,
            callbacks: {
              label: function (ctx) {
                return "  " + ctx.dataset.label + ": " + ctx.parsed.x + "%";
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
            borderWidth: 2,
            backgroundColor: "rgba(27, 58, 92, 0.08)",
            pointBackgroundColor: C_KENNEN,
            pointRadius: 3,
            pointHoverRadius: 5,
          },
          {
            label: "Kunnen",
            data: kunnenData,
            borderColor: C_KUNNEN,
            borderWidth: 2,
            backgroundColor: "rgba(74, 144, 196, 0.12)",
            pointBackgroundColor: C_KUNNEN,
            pointRadius: 3,
            pointHoverRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 4, bottom: 4, left: 8, right: 8 },
        },
        scales: {
          r: {
            min: 0,
            max: 1,
            ticks: { display: false },
            pointLabels: {
              font: { size: 10, weight: "500" },
              color: "#64748b",
            },
            grid: { color: "rgba(0,0,0,0.07)" },
            angleLines: { color: "rgba(0,0,0,0.07)" },
          },
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              usePointStyle: true, pointStyle: "circle", boxWidth: 8, boxHeight: 8, color: "#475569", font: { size: 11 }, padding: 16,
            },
          },
          tooltip: {
            backgroundColor: "rgba(15,23,42,0.8)",
            padding: 10,
            callbacks: {
              label: function (ctx) {
                return "  " + ctx.dataset.label + ": " + (ctx.parsed.r * 100).toFixed(0) + "%";
              },
            },
          },
        },
      },
    });
  }

  function renderStudentsTable(students) {
    var container = document.getElementById("students-overview-table");
    if (!container) return;

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
      "<th>Klas</th>" +
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
        '<td><select class="student-class-select" data-student-id="' +
        s.id +
        '">' +
        buildClassSelectOptions(s.class_id) +
        "</select></td>" +
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
    bindStudentClassSelects(container);
  }

  function buildClassSelectOptions(selectedClassId) {
    var html = '<option value="">Geen klas</option>';
    classes.forEach(function (c) {
      var isSelected = String(c.id) === String(selectedClassId || "");
      html +=
        '<option value="' +
        c.id +
        '"' +
        (isSelected ? " selected" : "") +
        ">" +
        escapeHtml(c.name) +
        "</option>";
    });
    return html;
  }

  function bindStudentClassSelects(container) {
    var selects = container.querySelectorAll(".student-class-select");
    selects.forEach(function (select) {
      select.addEventListener("change", function () {
        var studentId = select.getAttribute("data-student-id");
        var classId = select.value ? parseInt(select.value, 10) : null;
        assignStudentClass(studentId, classId, select);
      });
    });
  }

  function assignStudentClass(studentId, classId, selectEl) {
    if (!studentId) return;

    selectEl.disabled = true;
    fetch("/api/students/" + studentId + "/class", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ class_id: classId }),
    })
      .then(function (res) {
        if (!res.ok) {
          return res
            .json()
            .catch(function () { return {}; })
            .then(function (err) {
              throw new Error(err.error || "Klas koppelen mislukt.");
            });
        }
        return res.json();
      })
      .then(function () {
        showFeedback("Klas van leerling bijgewerkt.", "success");
        return loadClasses();
      })
      .then(function () {
        return loadClassData();
      })
      .catch(function (err) {
        showFeedback(err.message || "Wijzigen van klas mislukt.", "error");
      })
      .finally(function () {
        selectEl.disabled = false;
      });
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


