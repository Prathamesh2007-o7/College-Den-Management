let currentRoll = "";
let selectedEquipment = "";

const entryForm = document.getElementById("entry-form");
const rollInput = document.getElementById("roll_number");
const checkoutStep = document.getElementById("checkout-step");
const activeStudentName = document.getElementById("active-student-name");
const activeActivityName = document.getElementById("active-activity-name");
const activeTimeLeft = document.getElementById("active-time-left");
const checkoutBtn = document.getElementById("checkout-btn");

const actionStep = document.getElementById("action-selection-step");
const equipStep = document.getElementById("equipment-selection-step");
const durationStep = document.getElementById("duration-selection-step");

const result = document.getElementById("result");
const statusEl = result.querySelector(".result__status");
const reasonEl = result.querySelector(".result__reason");

function setResult(state, status, reason) {
  result.dataset.state = state;
  statusEl.textContent = status;
  reasonEl.textContent = reason || "";
}

function resetFlow() {
  currentRoll = "";
  selectedEquipment = "";
  entryForm.hidden = false;
  checkoutStep.hidden = true;
  actionStep.hidden = true;
  equipStep.hidden = true;
  durationStep.hidden = true;

  document.querySelectorAll(".option-btn, .equip-btn, .duration-btn, #checkout-btn").forEach(btn => {
    btn.disabled = false;
  });

  setResult("idle", "Waiting for roll number", "");
  rollInput.value = "";
  rollInput.focus();
}

// Step-by-Step Back Navigation
document.querySelectorAll(".back-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    if (!durationStep.hidden) {
      durationStep.hidden = true;
      equipStep.hidden = false;
    } else if (!equipStep.hidden) {
      equipStep.hidden = true;
      actionStep.hidden = false;
    } else if (!actionStep.hidden || !checkoutStep.hidden) {
      resetFlow();
    }
  });
});

// Stage 1: Submit Roll Number
entryForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const roll = rollInput.value.trim();
  if (!roll) return;

  setResult("idle", "Verifying...", "");

  try {
    const res = await fetch("/check_entry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_number: roll })
    });
    const data = await res.json();

    if (data.status === "ACTIVE_SESSION") {
      currentRoll = data.roll_no;
      entryForm.hidden = true;
      checkoutStep.hidden = false;
      activeStudentName.textContent = `${data.student_name} (${data.roll_no})`;
      activeActivityName.textContent = data.activity;
      activeTimeLeft.textContent = `${data.minutes_left} minutes left`;
      setResult("allowed", "ACTIVE SESSION", `Started at ${data.start_time}`);
    } else if (data.status === "ALLOWED") {
      currentRoll = data.roll_no;
      entryForm.hidden = true;
      actionStep.hidden = false;
      setResult("allowed", data.message, data.reason);
    } else {
      setResult("denied", data.message, data.reason);
    }
  } catch {
    setResult("error", "CONNECTION ERROR", "Could not reach the server.");
  }
});

// Checkout Action
checkoutBtn.addEventListener("click", async () => {
  checkoutBtn.disabled = true;
  try {
    const res = await fetch("/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_no: currentRoll })
    });
    const data = await res.json();

    if (res.ok && data.status === "OK") {
      checkoutStep.hidden = true;
      setResult("allowed", data.message, data.reason);
    } else {
      setResult("denied", "CHECKOUT FAILED", data.message || "Error checking out");
    }
  } catch {
    setResult("error", "ERROR", "Server unreachable.");
  } finally {
    setTimeout(resetFlow, 2500);
  }
});

// Stage 2: Activity or Rent Option
document.querySelectorAll(".option-btn:not(.back-btn)").forEach(btn => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;
    const value = btn.dataset.value;

    if (action === "rent-mode") {
      actionStep.hidden = true;
      equipStep.hidden = false;
    } else if (action === "activity") {
      submitFinalAction({
        roll_no: currentRoll,
        action_type: "ACTIVITY",
        activity_name: value
      });
    }
  });
});

// Stage 3: Equipment Selection
document.querySelectorAll(".equip-btn:not(.back-btn)").forEach(btn => {
  btn.addEventListener("click", () => {
    selectedEquipment = btn.dataset.item;
    equipStep.hidden = true;
    durationStep.hidden = false;
  });
});

// Stage 4: Duration Selection
document.querySelectorAll(".duration-btn:not(.back-btn)").forEach(btn => {
  btn.addEventListener("click", () => {
    const hours = btn.dataset.hours;
    submitFinalAction({
      roll_no: currentRoll,
      action_type: "RENTAL",
      equipment_item: selectedEquipment,
      duration: hours
    });
  });
});

async function submitFinalAction(payload) {
  document.querySelectorAll(".option-btn, .equip-btn, .duration-btn").forEach(btn => btn.disabled = true);
  actionStep.hidden = true;
  equipStep.hidden = true;
  durationStep.hidden = true;

  try {
    const res = await fetch("/select_action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (res.ok && data.status === "ALLOWED") {
      setResult("allowed", data.message, data.reason);
    } else {
      setResult("denied", data.message || "DENIED", data.reason || "Slot full or action failed.");
    }
  } catch {
    setResult("error", "ERROR", "Server unreachable.");
  } finally {
    setTimeout(resetFlow, 3500);
  }
}
