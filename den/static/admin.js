// ─── Dashboard Logic ───────────────────────────────────────────
const adminForm = document.getElementById("admin-form");
const adminPasswordInput = document.getElementById("admin-password");
const adminError = document.getElementById("admin-error");

const adminLoginView = document.getElementById("admin-login-view");
const dashboardMenuView = document.getElementById("dashboard-menu-view");
const viewBasicLogs = document.getElementById("view-basic-logs");
const viewDetailedReport = document.getElementById("view-detailed-report");
const viewUpdateDb = document.getElementById("view-update-db");

let currentPassword = "";

// ─── Helpers ───────────────────────────────────────────────────
function showView(view) {
  [adminLoginView, dashboardMenuView, viewBasicLogs, viewDetailedReport, viewUpdateDb].forEach(v => v.hidden = true);
  view.hidden = false;
}

// ─── 1. Login ──────────────────────────────────────────────────
adminForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  currentPassword = adminPasswordInput.value;
  adminError.textContent = "Verifying...";

  try {
    const res = await fetch("/admin/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();

    if (res.ok && data.status === "OK") {
      showView(dashboardMenuView);
    } else {
      adminError.textContent = data.message || "Incorrect password";
    }
  } catch {
    adminError.textContent = "Could not reach server";
  }
});

// ─── 2. Dashboard Menu Navigation ─────────────────────────────
document.getElementById("menu-view-logs").addEventListener("click", async () => {
  showView(viewBasicLogs);
  await loadBasicLogs();
});

document.getElementById("menu-view-detailed").addEventListener("click", async () => {
  showView(viewDetailedReport);
  await loadDetailedReport();
});

document.getElementById("menu-update-db").addEventListener("click", async () => {
  showView(viewUpdateDb);
  await loadTimetable();
  await loadStudents();
  await loadDepartments();
});

// Back buttons → dashboard menu
document.getElementById("logs-back-btn").addEventListener("click", () => showView(dashboardMenuView));
document.getElementById("detailed-back-btn").addEventListener("click", () => showView(dashboardMenuView));
document.getElementById("update-back-btn").addEventListener("click", () => showView(dashboardMenuView));

// ─── 3. Load Basic Logs ───────────────────────────────────────
async function loadBasicLogs() {
  try {
    const res = await fetch("/admin/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (res.ok && data.status === "OK") {
      document.getElementById("log-table-body").innerHTML = data.logs.map(log => `
        <tr>
          <td>${log.entry_time || "-"}</td>
          <td>${log.roll_no}</td>
          <td>${log.name}</td>
          <td class="${log.status === "ALLOWED" ? "status-allowed" : "status-denied"}">${log.status}</td>
        </tr>
      `).join("");
    }
  } catch { /* silently fail */ }
}

// ─── 4. Load Detailed Report ──────────────────────────────────
async function loadDetailedReport() {
  try {
    const res = await fetch("/admin/detailed_report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();

    if (res.ok && data.status === "OK") {
      document.getElementById("report-monthly-body").innerHTML = data.monthly_stats.map(stat => `
        <tr><td>${stat.month}</td><td>${stat.total_visits}</td></tr>
      `).join("");

      document.getElementById("report-student-monthly-body").innerHTML = data.student_monthly_stats.map(stat => `
        <tr><td>${stat.roll_no}</td><td>${stat.name}</td><td>${stat.month}</td><td>${stat.visits}</td></tr>
      `).join("");

      document.getElementById("report-sessions-body").innerHTML = data.sessions.map(session => `
        <tr>
          <td>${session.start_time || "-"}</td>
          <td>${session.roll_no}</td>
          <td>${session.name}</td>
          <td>${session.action_type}</td>
          <td>${session.activity_name || session.equipment_item || "-"}</td>
          <td class="${session.status === 'ACTIVE' ? 'status-allowed' : 'status-denied'}">${session.status}</td>
        </tr>
      `).join("");
    }
  } catch {
    alert("Could not fetch detailed report.");
  }
}

// ─── 5. CSV Download ──────────────────────────────────────────
function csvValue(value) {
  if (value === null || value === undefined) return "";
  const str = String(value);
  if (/[",\n]/.test(str)) return `"${str.replace(/"/g, '""')}"`;
  return str;
}

function buildDetailedReportCsv(data) {
  const lines = [];
  lines.push("Monthly Total Visitors");
  lines.push(["Month", "Total Entry Visits"].join(","));
  data.monthly_stats.forEach(stat => lines.push([stat.month, stat.total_visits].map(csvValue).join(",")));
  lines.push("");
  lines.push("Student Monthly Visits");
  lines.push(["Roll No", "Name", "Month", "Total Visits"].join(","));
  data.student_monthly_stats.forEach(stat => lines.push([stat.roll_no, stat.name, stat.month, stat.visits].map(csvValue).join(",")));
  lines.push("");
  lines.push("Session & Equipment Details");
  lines.push(["Start Time", "Roll No", "Name", "Action", "Item/Activity", "Status"].join(","));
  data.sessions.forEach(session => lines.push([session.start_time, session.roll_no, session.name, session.action_type, session.activity_name || session.equipment_item || "-", session.status].map(csvValue).join(",")));
  return lines.join("\n");
}

// Download from basic logs view
document.getElementById("download-csv-btn").addEventListener("click", async () => {
  const btn = document.getElementById("download-csv-btn");
  const originalLabel = btn.textContent;
  btn.disabled = true; btn.textContent = "Preparing...";
  try {
    const res = await fetch("/admin/detailed_report", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (res.ok && data.status === "OK") downloadCsv(buildDetailedReportCsv(data));
    else alert(data.message || "Could not generate report.");
  } catch { alert("Could not reach server."); }
  finally { btn.disabled = false; btn.textContent = originalLabel; }
});

// Download from detailed report view
document.getElementById("download-detailed-csv-btn").addEventListener("click", async () => {
  const btn = document.getElementById("download-detailed-csv-btn");
  const originalLabel = btn.textContent;
  btn.disabled = true; btn.textContent = "Preparing...";
  try {
    const res = await fetch("/admin/detailed_report", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (res.ok && data.status === "OK") downloadCsv(buildDetailedReportCsv(data));
    else alert(data.message || "Could not generate report.");
  } catch { alert("Could not reach server."); }
  finally { btn.disabled = false; btn.textContent = originalLabel; }
});

function downloadCsv(csv) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const dateStamp = new Date().toISOString().slice(0, 10);
  const link = document.createElement("a");
  link.href = url;
  link.download = `den_detailed_report_${dateStamp}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// ─── 6. Update Database – Sub-tab switching ───────────────────
const tabTimetable = document.getElementById("tab-timetable");
const tabStudents = document.getElementById("tab-students");
const tabDepartments = document.getElementById("tab-departments");
const sectionTimetable = document.getElementById("section-timetable");
const sectionStudents = document.getElementById("section-students");
const sectionDepartments = document.getElementById("section-departments");

function switchUpdateTab(activeTab, activeSection) {
  [tabTimetable, tabStudents, tabDepartments].forEach(t => t.classList.remove("active"));
  [sectionTimetable, sectionStudents, sectionDepartments].forEach(s => s.hidden = true);
  activeTab.classList.add("active");
  activeSection.hidden = false;
}

tabTimetable.addEventListener("click", () => switchUpdateTab(tabTimetable, sectionTimetable));
tabStudents.addEventListener("click", () => switchUpdateTab(tabStudents, sectionStudents));
tabDepartments.addEventListener("click", () => switchUpdateTab(tabDepartments, sectionDepartments));

// ─── 7. Timetable CRUD ───────────────────────────────────────
async function loadTimetable() {
  try {
    const res = await fetch("/admin/timetable", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (data.status === "OK") {
      document.getElementById("timetable-body").innerHTML = data.entries.map(e => `
        <tr>
          <td>${e.id}</td><td>${e.department_id}</td><td>${e.day_of_week}</td>
          <td>${e.start_time}</td><td>${e.end_time}</td><td>${e.subject}</td>
          <td><button class="delete-row-btn" onclick="deleteTimetable(${e.id})">🗑️</button></td>
        </tr>
      `).join("");
    }
  } catch { /* silently fail */ }
}

document.getElementById("form-timetable").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = document.getElementById("tt-status");
  status.textContent = "Saving..."; status.className = "form-status";
  try {
    const res = await fetch("/admin/timetable/add", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: currentPassword,
        department_id: parseInt(document.getElementById("tt-dept-id").value),
        day_of_week: document.getElementById("tt-day").value,
        start_time: document.getElementById("tt-start").value,
        end_time: document.getElementById("tt-end").value,
        subject: document.getElementById("tt-subject").value
      })
    });
    const data = await res.json();
    status.textContent = data.message;
    status.className = res.ok ? "form-status form-status--ok" : "form-status form-status--err";
    if (res.ok) { e.target.reset(); await loadTimetable(); }
  } catch { status.textContent = "Server error"; status.className = "form-status form-status--err"; }
});

window.deleteTimetable = async function (id) {
  if (!confirm("Delete this timetable entry?")) return;
  try {
    const res = await fetch("/admin/timetable/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword, id })
    });
    const data = await res.json();
    if (res.ok) await loadTimetable();
    else alert(data.message);
  } catch { alert("Server error"); }
};

// ─── 8. Students CRUD ────────────────────────────────────────
async function loadStudents() {
  try {
    const res = await fetch("/admin/students", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (data.status === "OK") {
      document.getElementById("students-body").innerHTML = data.students.map(s => `
        <tr>
          <td>${s.roll_no}</td><td>${s.name}</td><td>${s.department_id}</td>
          <td><button class="delete-row-btn" onclick="deleteStudent('${s.roll_no}')">🗑️</button></td>
        </tr>
      `).join("");
    }
  } catch { /* silently fail */ }
}

document.getElementById("form-student").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = document.getElementById("st-status");
  status.textContent = "Saving..."; status.className = "form-status";
  try {
    const res = await fetch("/admin/students/upsert", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: currentPassword,
        roll_no: document.getElementById("st-roll").value.trim(),
        name: document.getElementById("st-name").value.trim(),
        department_id: parseInt(document.getElementById("st-dept").value)
      })
    });
    const data = await res.json();
    status.textContent = data.message;
    status.className = res.ok ? "form-status form-status--ok" : "form-status form-status--err";
    if (res.ok) { e.target.reset(); await loadStudents(); }
  } catch { status.textContent = "Server error"; status.className = "form-status form-status--err"; }
});

window.deleteStudent = async function (roll_no) {
  if (!confirm(`Delete student ${roll_no}?`)) return;
  try {
    const res = await fetch("/admin/students/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword, roll_no })
    });
    const data = await res.json();
    if (res.ok) await loadStudents();
    else alert(data.message);
  } catch { alert("Server error"); }
};

// ─── 9. Departments CRUD ────────────────────────────────────
async function loadDepartments() {
  try {
    const res = await fetch("/admin/departments", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();
    if (data.status === "OK") {
      document.getElementById("departments-body").innerHTML = data.departments.map(d => `
        <tr>
          <td>${d.department_id}</td><td>${d.department_name}</td>
          <td><button class="delete-row-btn" onclick="deleteDepartment(${d.department_id})">🗑️</button></td>
        </tr>
      `).join("");
    }
  } catch { /* silently fail */ }
}

document.getElementById("form-department").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = document.getElementById("dp-status");
  status.textContent = "Saving..."; status.className = "form-status";
  try {
    const res = await fetch("/admin/departments/add", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password: currentPassword,
        department_name: document.getElementById("dp-name").value.trim()
      })
    });
    const data = await res.json();
    status.textContent = data.message;
    status.className = res.ok ? "form-status form-status--ok" : "form-status form-status--err";
    if (res.ok) { e.target.reset(); await loadDepartments(); }
  } catch { status.textContent = "Server error"; status.className = "form-status form-status--err"; }
});

window.deleteDepartment = async function (id) {
  if (!confirm("Delete this department?")) return;
  try {
    const res = await fetch("/admin/departments/delete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword, department_id: id })
    });
    const data = await res.json();
    if (res.ok) await loadDepartments();
    else alert(data.message);
  } catch { alert("Server error"); }
};
