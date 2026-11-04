"""Independent continuum oracle around an integrity-bound upstream solver excerpt."""
from __future__ import annotations

import hashlib
import inspect
import json
import math
import platform
from importlib.resources import files
from typing import Any

from ..models import sha256_json, utcnow
from ..receipts import RECEIPT_STATEMENT, receipt_hash, tool_block

PIN = "b63a2418ca1253440cce12519183c5775b61f84a"
ORACLE = "szl.openislet.peroxide-sine/v1"
HEIGHTS = (1.0, 25000.0, 250000.0)
MESHES = (16, 32, 64, 128)
LENGTH_CM = 0.035
DIFFUSION_CM2_S = 1.40e-5  # Independent declared constant, never read from the solver.
KM_UM = 25000.0
LIMITATIONS = [
    "Synthetic manufactured fields, not measurements or a biological experiment.",
    "Verifies this spatial software discretization only, not physical model correctness.",
    "Does not validate transient dynamics, oxygen/pH coupling, efficacy, safety, or clinical use.",
    "Parameters are declared model inputs, not calibrated or recommended here.",
    "Upstream already tests discrete mass balance and scalar quadratic manufactured solutions.",
    "This additional sine-field check uses spatial coefficient arrays and refinement; no defect or first-in-field novelty is claimed.",
    "UNSIGNED receipts bind content only; anyone able to rewrite all artifacts can reseal them.",
]


class ReplayError(Exception):
    """A named, safe failure that must never be displayed as a scientific result."""


def validate_request(value: Any) -> dict[str, Any]:
    """Closed preset contract. No text, paths, URLs, scripts, or uploaded data."""
    if not isinstance(value, dict) or set(value) - {"amplitude_uM", "kinetics"}:
        raise ValueError("Only amplitude_uM and kinetics are accepted.")
    amplitude = value.get("amplitude_uM", 25000.0)
    kinetics = value.get("kinetics", "nonlinear")
    # Membership in these finite presets also rejects NaN/Inf, without coercing
    # arbitrarily large JSON integers to float (which can raise OverflowError).
    if type(amplitude) not in (int, float) or amplitude not in HEIGHTS:
        raise ValueError("amplitude_uM must be one of the synthetic presets: 1, 25000, 250000.")
    if not isinstance(kinetics, str) or kinetics not in ("linear", "nonlinear"):
        raise ValueError("kinetics must be linear or nonlinear.")
    return {"amplitude_uM": float(amplitude), "kinetics": kinetics}


def provenance() -> dict[str, Any]:
    return json.loads(files(__package__).joinpath("vendor/provenance.json").read_text(encoding="utf-8"))


def _verify_source(layer: Any) -> dict[str, Any]:
    record = provenance()
    for name, expected in record["function_sha256"].items():
        source = inspect.getsource(getattr(layer, name)).replace("\r\n", "\n").encode()
        if hashlib.sha256(source).hexdigest() != expected:
            raise ReplayError("SOURCE_MISMATCH: upstream function excerpt failed its pinned SHA-256.")
    if layer.D_H2O2_HYDROGEL_CM2_S != DIFFUSION_CM2_S:
        raise ReplayError("SOURCE_MISMATCH: upstream diffusivity differs from the independent declaration.")
    return record


def run_replay(request: dict[str, Any]) -> dict[str, Any]:
    """One preset, four grids and two deliberate faults. No I/O beyond package reads."""
    selected = validate_request(request)
    started = utcnow()
    try:
        import numpy as np

        from .vendor import peroxide as layer
    except ImportError as exc:
        raise ReplayError('DEPENDENCY_UNAVAILABLE: install szl-evidence-mandate[openislet].') from exc
    record = _verify_source(layer)
    height = selected["amplitude_uM"]
    km = KM_UM if selected["kinetics"] == "nonlinear" else None
    rows = []
    controls = []
    profile = None
    try:
        with np.errstate(all="raise"):
            for intervals in MESHES:
                dx = LENGTH_CM / intervals
                x = np.arange(1, intervals) * dx
                truth = height * np.sin(math.pi * x / LENGTH_CM)
                catalytic = 0.10 + 0.05 * x / LENGTH_CM
                perfusion = 0.01 + 0.02 * (x / LENGTH_CM) ** 2
                saturation = 1.0 if km is None else 1.0 + truth / km
                source = DIFFUSION_CM2_S * (math.pi / LENGTH_CM) ** 2 * truth
                source += catalytic * truth / saturation + perfusion * truth
                result = layer._solve_peroxide_slab_bvp(source, dx, catalytic, perfusion, km_uM=km)
                h = result["concentration_uM"]
                error = float(np.max(np.abs(h - truth))) / height
                supplied = float(np.sum(source) * dx)
                removed = float(np.sum(result["decomposition_uM_s"] + perfusion * h) * dx)
                removed += DIFFUSION_CM2_S * (h[0] + h[-1]) / dx
                balance = abs(supplied - removed) / supplied
                rows.append({
                    "intervals": intervals, "interior_nodes": intervals - 1, "dx_cm": dx,
                    "relative_linf_error": error, "relative_balance_error": balance,
                    "solver_residual_uM_s": result["residual_inf_uM_s"],
                    "iterations": result["iterations"], "converged": result["converged"],
                })
                if intervals == MESHES[-1]:
                    profile = [
                        {"x_cm": float(xx), "reference_uM": float(ref), "solver_uM": float(actual)}
                        for xx, ref, actual in zip(x, truth, h, strict=True)
                    ]
                    for mutation in ("diffusivity_x2", "flatten_spatial_coefficients"):
                        try:
                            layer.D_H2O2_HYDROGEL_CM2_S = DIFFUSION_CM2_S * (2 if mutation == "diffusivity_x2" else 1)
                            flatten = mutation == "flatten_spatial_coefficients"
                            cat = float(np.mean(catalytic)) if flatten else catalytic
                            perf = float(np.mean(perfusion)) if flatten else perfusion
                            bad = layer._solve_peroxide_slab_bvp(source, dx, cat, perf, km_uM=km)
                            bad_error = float(np.max(np.abs(bad["concentration_uM"] - truth))) / height
                            controls.append({
                                "mutation": mutation, "relative_linf_error": bad_error,
                                "rejected": bad_error > 0.001,
                            })
                        finally:
                            layer.D_H2O2_HYDROGEL_CM2_S = DIFFUSION_CM2_S
    except (ValueError, ArithmeticError) as exc:
        raise ReplayError("NUMERIC_ERROR: the bounded solver could not complete this replay.") from exc
    ratios = [a["relative_linf_error"] / b["relative_linf_error"] for a, b in zip(rows, rows[1:], strict=False)]
    checks = {
        "all_solves_converged": all(row["converged"] for row in rows),
        "balance_below_1e_7": all(row["relative_balance_error"] < 1e-7 for row in rows),
        "finest_error_below_1e_4": rows[-1]["relative_linf_error"] < 1e-4,
        "second_order_refinement": all(3.8 < ratio < 4.2 for ratio in ratios),
        "both_faults_rejected": len(controls) == 2 and all(c["rejected"] for c in controls),
    }
    payload = {
        "oracle": ORACLE,
        "oracle_source_sha256": hashlib.sha256(files(__package__).joinpath("replay.py").read_bytes()).hexdigest(),
        "input_class": "SYNTHETIC_MANUFACTURED_SOLUTION",
        "inputs_sha256": sha256_json(selected), "request": selected, "source": record,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "parameters": {"length_cm": LENGTH_CM, "diffusion_cm2_s": DIFFUSION_CM2_S, "km_uM": km,
                       "catalytic_s_inv": "0.10 + 0.05*x/L", "perfusion_s_inv": "0.01 + 0.02*(x/L)^2"},
        "reference": {"concentration": "H(x) = amplitude*sin(pi*x/L)",
                      "source": "q(x) = D*(pi/L)^2*H + k_cat(x)*H/(1+H/Km) + k_perf(x)*H",
                      "linear_branch": "Replace (1+H/Km) by 1.",
                      "boundaries": "H(0) = H(L) = 0 uM"},
        "mesh_results": rows, "refinement_ratios": ratios, "observed_orders": [math.log2(r) for r in ratios],
        "negative_controls": controls, "checks": checks, "finest_profile": profile,
        "tolerances": {"finest_relative_linf": 1e-4, "relative_balance": 1e-7,
                       "refinement_ratio_open_interval": [3.8, 4.2], "fault_relative_linf_above": 0.001},
        "biological_validation": False,
    }
    receipt = {
        "schema_version": "szl.evidence.receipt/v1", "kind": "openislet-peroxide-replay",
        "run_id": sha256_json([ORACLE, selected, record])[:16], "tool": tool_block(),
        "started_at": started, "completed_at": utcnow(), "status": "PASS" if all(checks.values()) else "FAIL",
        "payload": payload, "limitations": LIMITATIONS, "receipt_statement": RECEIPT_STATEMENT,
        "parent_sha256": None, "signature_state": "UNSIGNED",
    }
    receipt["receipt_sha256"] = receipt_hash(receipt)
    # Fail closed on non-finite output even if a future upstream change misses it.
    try:
        json.dumps(receipt, allow_nan=False)
    except ValueError as exc:
        raise ReplayError("NUMERIC_ERROR: non-finite output was refused.") from exc
    return receipt
