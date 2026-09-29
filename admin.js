// Admin Authentication and Dashboard Logic
const adminForm = document.getElementById("admin-form");
const adminPasswordInput = document.getElementById("admin-password");
const adminError = document.getElementById("admin-error");

const adminLoginView = document.getElementById("admin-login-view");
const adminDashboardView = document.getElementById("admin-dashboard-view");

const tabBasicLogs = document.getElementById("tab-basic-logs");
const tabDetailedReport = document.getElementById("tab-detailed-report");
const viewBasicLogs = document.getElementById("view-basic-logs");
const viewDetailedReport = document.getElementById("view-detailed-report");
const downloadCsvBtn = document.getElementById("download-csv-btn");

const logTableBody = document.getElementById("log-table-body");
const reportMonthlyBody = document.getElementById("report-monthly-body");
const reportStudentMonthlyBody = document.getElementById("report-student-monthly-body");
const reportSessionsBody = document.getElementById("report-sessions-body");

let currentPassword = "";

// 1. Handle Login
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
      adminLoginView.hidden = true;
      adminDashboardView.hidden = false;
      
      // Populate Basic Logs immediately
      logTableBody.innerHTML = data.logs.map(log => `
        <tr>
          <td>${log.entry_time || "-"}</td>
          <td>${log.roll_no}</td>
          <td>${log.name}</td>
          <td class="${log.status === "ALLOWED" ? "status-allowed" : "status-denied"}">${log.status}</td>
        </tr>
      `).join("");
    } else {
      adminError.textContent = data.message || "Incorrect password";
    }
  } catch {
    adminError.textContent = "Could not reach server";
  }
});

// 2. Handle Tabs Switching (Basic Logs)
tabBasicLogs.addEventListener("click", () => {
  tabBasicLogs.classList.add("active");
  tabDetailedReport.classList.remove("active");
  viewBasicLogs.hidden = false;
  viewDetailedReport.hidden = true;
});

// 3. Handle Tabs Switching (Detailed Reports Fetch)
tabDetailedReport.addEventListener("click", async () => {
  tabDetailedReport.classList.add("active");
  tabBasicLogs.classList.remove("active");
  viewBasicLogs.hidden = true;
  viewDetailedReport.hidden = false;
  
  try {
    const res = await fetch("/admin/detailed_report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();

    if (res.ok && data.status === "OK") {
      // Load Monthly stats
      reportMonthlyBody.innerHTML = data.monthly_stats.map(stat => `
        <tr>
          <td>${stat.month}</td>
          <td>${stat.total_visits}</td>
        </tr>
      `).join("");

      // Load Individual Student Monthly records
      reportStudentMonthlyBody.innerHTML = data.student_monthly_stats.map(stat => `
        <tr>
          <td>${stat.roll_no}</td>
          <td>${stat.name}</td>
          <td>${stat.month}</td>
          <td>${stat.visits}</td>
        </tr>
      `).join("");

      // Load Detailed Sessions Array
      reportSessionsBody.innerHTML = data.sessions.map(session => `
        <tr>
          <td>${session.start_time || "-"}</td>
          <td>${session.roll_no}</td>
          <td>${session.name}</td>
          <td>${session.action_type}</td>
          <td>${session.activity_name || session.equipment_item || "-"}</td>
          <td class="${session.status === 'ACTIVE' ? 'status-allowed' : 'status-denied'}">${session.status}</td>
        </tr>
      `).join("");
    } else {
      alert(data.message || "Error loading report.");
    }
  } catch {
    alert("Could not fetch detailed report.");
  }
});

// 4. Handle "Download Excel" (CSV export of the detailed report)
function csvValue(value) {
  if (value === null || value === undefined) return "";
  const str = String(value);
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function buildDetailedReportCsv(data) {
  const lines = [];

  lines.push("Monthly Total Visitors");
  lines.push(["Month", "Total Entry Visits"].join(","));
  data.monthly_stats.forEach(stat => {
    lines.push([stat.month, stat.total_visits].map(csvValue).join(","));
  });
  lines.push("");

  lines.push("Student Monthly Visits");
  lines.push(["Roll No", "Name", "Month", "Total Visits"].join(","));
  data.student_monthly_stats.forEach(stat => {
    lines.push([stat.roll_no, stat.name, stat.month, stat.visits].map(csvValue).join(","));
  });
  lines.push("");

  lines.push("Session & Equipment Details");
  lines.push(["Start Time", "Roll No", "Name", "Action", "Item/Activity", "Status"].join(","));
  data.sessions.forEach(session => {
    lines.push([
      session.start_time,
      session.roll_no,
      session.name,
      session.action_type,
      session.activity_name || session.equipment_item || "-",
      session.status
    ].map(csvValue).join(","));
  });

  return lines.join("\n");
}

downloadCsvBtn.addEventListener("click", async () => {
  const originalLabel = downloadCsvBtn.textContent;
  downloadCsvBtn.disabled = true;
  downloadCsvBtn.textContent = "Preparing...";

  try {
    const res = await fetch("/admin/detailed_report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: currentPassword })
    });
    const data = await res.json();

    if (res.ok && data.status === "OK") {
      const csv = buildDetailedReportCsv(data);
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
    } else {
      alert(data.message || "Could not generate report.");
    }
  } catch {
    alert("Could not reach server.");
  } finally {
    downloadCsvBtn.disabled = false;
    downloadCsvBtn.textContent = originalLabel;
  }
});
