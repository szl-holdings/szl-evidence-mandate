"use strict";
const $ = (id) => document.getElementById(id);
const number = (n) => Number.isFinite(n) ? n.toExponential(5) : "Unavailable";
let receipt = null;
let receiptBytes = null;
const checks = {
  all_solves_converged: "All four solves converged",
  balance_below_1e_7: "Balance error below 10⁻⁷",
  finest_error_below_1e_4: "Finest-grid error below 10⁻⁴",
  second_order_refinement: "Refinement ratios between 3.8 and 4.2",
  both_faults_rejected: "Both deliberate faults rejected"
};
function cell(row, value) {
  const td = document.createElement("td");
  td.textContent = value;
  row.append(td);
}
function render(data) {
  const p = data.payload;
  if (!p || !Array.isArray(p.mesh_results) || p.mesh_results.length !== 4 ||
      !Array.isArray(p.negative_controls) || p.negative_controls.length !== 2 ||
      !["PASS", "FAIL"].includes(data.status) || p.biological_validation !== false) {
    throw new Error("The backend returned an incomplete verification receipt.");
  }
  receipt = data;
  const passed = data.status === "PASS";
  $("verdict").className = `badge ${passed ? "passed" : "failed"}`;
  $("verdict").textContent = passed ? "Fixture checks passed" : "Fixture checks failed";
  $("run-status").textContent = `Observed numerical verification ${passed ? "passed" : "failed"} for this synthetic ${p.request.amplitude_uM.toLocaleString()} µM, ${p.request.kinetics} fixture only. Biological validation is not established.`;
  $("error-metric").textContent = number(p.mesh_results.at(-1).relative_linf_error);
  $("order-metric").textContent = p.observed_orders.at(-1).toFixed(4);
  $("controls-metric").textContent = `${p.negative_controls.filter(c => c.rejected).length} / 2`;
  $("mesh-body").replaceChildren();
  p.mesh_results.forEach((mesh, index) => {
    const tr = document.createElement("tr");
    [mesh.intervals.toString(), number(mesh.relative_linf_error),
      index ? `${p.refinement_ratios[index - 1].toFixed(4)}×` : "—",
      number(mesh.relative_balance_error), number(mesh.solver_residual_uM_s)
    ].forEach(v => cell(tr, v));
    $("mesh-body").append(tr);
  });
  $("checks").replaceChildren();
  Object.entries(checks).forEach(([key, label]) => {
    const li = document.createElement("li");
    li.className = p.checks[key] === true ? "check-pass" : "check-fail";
    li.textContent = `${p.checks[key] === true ? "✓" : "✕"} ${label}`;
    $("checks").append(li);
  });
  $("fault-results").replaceChildren();
  p.negative_controls.forEach(control => {
    const card = document.createElement("div");
    card.className = "fault-card";
    const title = document.createElement("strong");
    title.textContent = control.mutation === "diffusivity_x2" ? "Double diffusivity" : "Flatten spatial coefficients";
    const status = document.createElement("span");
    status.className = control.rejected ? "check-pass" : "check-fail";
    status.textContent = control.rejected ? "✓ Rejected as expected" : "✕ Fault was not rejected";
    const error = document.createElement("span");
    error.textContent = `Relative L∞ error: ${number(control.relative_linf_error)}`;
    card.append(title, status, error);
    $("fault-results").append(card);
  });
  $("profile-body").replaceChildren();
  p.finest_profile.forEach(point => {
    const tr = document.createElement("tr");
    [point.x_cm, point.reference_uM, point.solver_uM].forEach(v => cell(tr, number(v)));
    $("profile-body").append(tr);
  });
  $("receipt-hash").textContent = `UNSIGNED · SHA-256 ${data.receipt_sha256}`;
  $("download").disabled = false;
}
function clearResult() {
  receipt = null;
  receiptBytes = null;
  $("download").disabled = true;
  $("error-metric").textContent = "—";
  $("order-metric").textContent = "—";
  $("controls-metric").textContent = "—";
  $("mesh-body").replaceChildren();
  $("checks").replaceChildren();
  $("fault-results").replaceChildren();
  $("profile-body").replaceChildren();
  $("receipt-hash").textContent = "Receipt: not generated for this request.";
}
$("replay-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearResult();
  $("results-panel").setAttribute("aria-busy", "true");
  ["run-button", "amplitude", "kinetics"].forEach(id => { $(id).disabled = true; });
  $("run-label").textContent = "Running bounded replay…";
  $("verdict").textContent = "Running";
  $("verdict").className = "badge neutral";
  $("run-status").className = "run-status";
  $("run-status").textContent = "Executing four meshes and two fault controls on the local pinned solver…";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 22000);
  try {
    const response = await fetch("/api/openislet/replay", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amplitude_uM: Number($("amplitude").value), kinetics: $("kinetics").value }),
      // Keep same-origin preview access cookies; never send them cross-origin.
      signal: controller.signal, credentials: "same-origin"
    });
    const rawBody = await response.text();
    const data = JSON.parse(rawBody);
    if (!response.ok) throw new Error(data.error || `Replay failed (HTTP ${response.status}).`);
    render(data);
    // Preserve the original server serialization. JS round-tripping Python floats
    // (e.g. 25000.0 -> 25000) can change canonical receipt hashes.
    receiptBytes = rawBody;
  } catch (error) {
    clearResult();
    $("verdict").textContent = "Execution error";
    $("verdict").className = "badge failed";
    $("run-status").className = "run-status error";
    $("run-status").textContent = error.name === "AbortError"
      ? "The request timed out. No successful result or receipt is assumed. Try again."
      : `No result established: ${error.message}`;
  } finally {
    clearTimeout(timeout);
    $("results-panel").setAttribute("aria-busy", "false");
    ["run-button", "amplitude", "kinetics"].forEach(id => { $(id).disabled = false; });
    $("run-label").textContent = "Run numerical replay";
    $("run-status").focus({ preventScroll: true });
  }
});
["amplitude", "kinetics"].forEach(id => {
  $(id).addEventListener("change", () => {
    clearResult();
    $("verdict").textContent = "Not executed";
    $("verdict").className = "badge neutral";
    $("run-status").className = "run-status";
    $("run-status").textContent = "Fixture settings changed. Run a fresh replay; previous results are no longer displayed.";
  });
});
$("download").addEventListener("click", () => {
  if (!receipt || !receiptBytes) return;
  const url = URL.createObjectURL(new Blob([receiptBytes], { type: "application/json" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `openislet-${receipt.run_id}.json`;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
(async () => {
  try {
    const response = await fetch("/api/openislet/meta", { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Metadata unavailable (HTTP ${response.status}).`);
    const data = await response.json();
    if (data.source.revision !== "b63a2418ca1253440cce12519183c5775b61f84a")
      throw new Error("The source revision does not match this workbench.");
    $("source-hash").textContent = data.source.source_sha256;
    $("connection").textContent = "Contract loaded. Each run checks the pinned function digests before execution.";
    ["run-button", "amplitude", "kinetics"].forEach(id => { $(id).disabled = false; });
  } catch (error) {
    $("connection").textContent = `Unable to load verification contract: ${error.message} Reload to retry.`;
    $("connection").classList.add("check-fail");
  }
})();
