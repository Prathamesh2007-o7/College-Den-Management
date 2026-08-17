// ---- Entry check form ----
const form = document.getElementById("entry-form");
const input = document.getElementById("roll_number");
const button = form.querySelector(".kiosk__button");
const result = document.getElementById("result");
const statusEl = result.querySelector(".result__status");
const reasonEl = result.querySelector(".result__reason");

function setResult(state, status, reason) {
  result.dataset.state = state;
  statusEl.textContent = status;
  reasonEl.textContent = reason || "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const rollNumber = input.value.trim();
  if (!rollNumber) {
    setResult("error", "MISSING ROLL NUMBER", "Please enter a roll number.");
    return;
  }

  button.disabled = true;
  setResult("idle", "Checking...", "");

  try {
    const response = await fetch("/check_entry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_number: rollNumber })
    });

    const data = await response.json();

    if (data.status === "ALLOWED") {
      setResult("allowed", data.message, data.reason);
    } else if (data.status === "DENIED") {
      setResult("denied", data.message, data.reason);
    } else {
      setResult("error", data.message || "ERROR", data.reason || "Something went wrong.");
    }
  } catch (err) {
    setResult("error", "CONNECTION ERROR", "Could not reach the server.");
  } finally {
    button.disabled = false;
    input.value = "";
    input.focus();
  }
});

// ---- Admin modal ----
const adminBtn = document.getElementById("admin-btn");
const adminModal = document.getElementById("admin-modal");
const modalBackdrop = document.getElementById("modal-backdrop");
const modalClose = document.getElementById("modal-close");

const adminLoginView = document.getElementById("admin-login-view");
const adminLogsView = document.getElementById("admin-logs-view");
const adminForm = document.getElementById("admin-form");
const adminPasswordInput = document.getElementById("admin-password");
const adminError = document.getElementById("admin-error");
const logTableBody = document.getElementById("log-table-body");

function openAdminModal() {
  adminModal.hidden = false;
  adminLoginView.hidden = false;
  adminLogsView.hidden = true;
  adminError.textContent = "";
  adminPasswordInput.value = "";
  adminPasswordInput.focus();
}

function closeAdminModal() {
  adminModal.hidden = true;
}

adminBtn.addEventListener("click", openAdminModal);
modalClose.addEventListener("click", closeAdminModal);
modalBackdrop.addEventListener("click", closeAdminModal);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !adminModal.hidden) {
    closeAdminModal();
  }
});

adminForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const password = adminPasswordInput.value;
  adminError.textContent = "";

  const submitBtn = adminForm.querySelector(".kiosk__button");
  submitBtn.disabled = true;

  try {
    const response = await fetch("/admin/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });

    const data = await response.json();

    if (response.ok && data.status === "OK") {
      renderLogs(data.logs);
      adminLoginView.hidden = true;
      adminLogsView.hidden = false;
    } else {
      adminError.textContent = data.message || "Incorrect password";
    }
  } catch (err) {
    adminError.textContent = "Could not reach the server.";
  } finally {
    submitBtn.disabled = false;
  }
});

function renderLogs(logs) {
  logTableBody.innerHTML = "";

  if (!logs || logs.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="4" class="log-table__empty">No entries yet</td>`;
    logTableBody.appendChild(row);
    return;
  }

  for (const log of logs) {
    const row = document.createElement("tr");
    const statusClass = log.status === "GRANTED" || log.status === "ALLOWED"
      ? "status-allowed"
      : "status-denied";

    row.innerHTML = `
      <td>${log.entry_time || "-"}</td>
      <td>${log.roll_no}</td>
      <td>${log.name}</td>
      <td class="${statusClass}">${log.status}</td>
    `;
    logTableBody.appendChild(row);
  }
}
