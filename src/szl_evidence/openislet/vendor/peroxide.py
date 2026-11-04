# Copyright (c) 2026 OpenIslet.org Contributors.
# SPDX-License-Identifier: Apache-2.0
# Extracted from OpenIslet/openislet@b63a2418ca1253440cce12519183c5775b61f84a,
# scripts/run_layer4_tissue_and_metabolic_twin.py.
# Modification: only these two functions and one constant are retained; imports
# are reduced. Function bodies are verbatim. See NOTICE.txt and provenance.json.
from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np

D_H2O2_HYDROGEL_CM2_S = 1.40e-5            # Effective H2O2 diffusivity in hydrogel slab (cm^2/s)


def _tridiag_thomas_solve(lo: np.ndarray, diag: np.ndarray, up: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Exact O(N) Thomas algorithm for tridiagonal linear systems."""
    n = len(diag)
    dc = diag.astype(np.float64, copy=True)
    bc = rhs.astype(np.float64, copy=True)
    for i in range(1, n):
        w = lo[i - 1] / dc[i - 1]
        dc[i] -= w * up[i - 1]
        bc[i] -= w * bc[i - 1]
    x = np.empty(n, dtype=np.float64)
    x[-1] = bc[-1] / dc[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (bc[i] - up[i] * x[i + 1]) / dc[i]
    return x


def _solve_peroxide_slab_bvp(
    source_uM_s: np.ndarray, dz_cm: float, catalytic_rate_s_inv: float | np.ndarray,
    perfusion_rate_s_inv: float | np.ndarray, *, km_uM: float | None = None,
) -> Dict[str, Any]:
    """Solve local peroxide clearance with zero-concentration host boundaries.

    Michaelis-Menten clearance is evaluated at every node of the solved state;
    the returned decomposition rate is also the stoichiometric oxygen source.
    Supports both scalar and nodewise 1D spatial profiles for catalytic_rate_s_inv and perfusion_rate_s_inv.
    """
    source = np.asarray(source_uM_s)
    if (source.ndim != 1 or not len(source)
            or not (np.issubdtype(source.dtype, np.integer) or np.issubdtype(source.dtype, np.floating))
            or not np.all(np.isfinite(source)) or np.any(source < 0)):
        raise ValueError("Peroxide source must be a finite nonnegative real vector")
    if (isinstance(dz_cm, bool) or not isinstance(dz_cm, (int, float)) or not math.isfinite(dz_cm) or dz_cm <= 0):
        raise ValueError("dz_cm outside its finite physical domain")
    if isinstance(perfusion_rate_s_inv, np.ndarray):
        perf_vec = np.asarray(perfusion_rate_s_inv, dtype=float)
        if (perf_vec.ndim != 1 or len(perf_vec) != len(source)
                or not np.all(np.isfinite(perf_vec)) or np.any(perf_vec < 0)):
            raise ValueError("perfusion_rate_s_inv vector outside its finite nonnegative physical domain")
    else:
        if (isinstance(perfusion_rate_s_inv, bool) or not isinstance(perfusion_rate_s_inv, (int, float))
                or not math.isfinite(perfusion_rate_s_inv) or perfusion_rate_s_inv < 0):
            raise ValueError("perfusion_rate_s_inv outside its finite physical domain")
        perf_vec = np.full(len(source), float(perfusion_rate_s_inv), dtype=float)
    if isinstance(catalytic_rate_s_inv, np.ndarray):
        cat_vec = np.asarray(catalytic_rate_s_inv, dtype=float)
        if (cat_vec.ndim != 1 or len(cat_vec) != len(source)
                or not np.all(np.isfinite(cat_vec)) or np.any(cat_vec < 0)):
            raise ValueError("catalytic_rate_s_inv vector outside its finite nonnegative physical domain")
    else:
        if (isinstance(catalytic_rate_s_inv, bool) or not isinstance(catalytic_rate_s_inv, (int, float))
                or not math.isfinite(catalytic_rate_s_inv) or catalytic_rate_s_inv < 0):
            raise ValueError("catalytic_rate_s_inv outside its finite physical domain")
        cat_vec = np.full(len(source), float(catalytic_rate_s_inv), dtype=float)
    if km_uM is not None and (isinstance(km_uM, bool) or not isinstance(km_uM, (int, float))
                             or not math.isfinite(km_uM) or km_uM <= 0):
        raise ValueError("km_uM must be finite and positive")
    source = source.astype(float, copy=False)
    try:
        diffusion = D_H2O2_HYDROGEL_CM2_S / (dz_cm * dz_cm)
    except (ZeroDivisionError, OverflowError) as exc:
        raise ValueError("Peroxide grid is outside representable numeric range") from exc
    if not math.isfinite(diffusion) or diffusion <= 0:
        raise ValueError("Peroxide grid is outside representable numeric range")
    off = np.full(len(source)-1, diffusion)
    linear_diag = -2.0*diffusion - perf_vec - cat_vec
    h = _tridiag_thomas_solve(off, linear_diag, off, -source)
    tolerance = 1e-8 + 1e-10*max(1.0, float(np.max(source)))
    converged = False
    residual_inf = math.inf
    for iteration in range(80):
        saturation = np.ones_like(h) if km_uM is None else 1.0 + h/km_uM
        decomposition = cat_vec * (h/saturation)
        residual = (-2.0*diffusion-perf_vec)*h - decomposition + source
        residual[:-1] += diffusion*h[1:]
        residual[1:] += diffusion*h[:-1]
        if not np.all(np.isfinite(h)) or np.any(h < 0) or not np.all(np.isfinite(residual)):
            raise ValueError("Peroxide solve left its finite nonnegative domain")
        residual_inf = float(np.max(np.abs(residual)))
        if residual_inf <= tolerance:
            converged = True
            break
        derivative = cat_vec / saturation / saturation
        diagonal = -2.0*diffusion-perf_vec-derivative
        step = _tridiag_thomas_solve(off, diagonal, off, -residual)
        factor = 1.0
        while np.any(h+factor*step < 0) and factor > 1e-12:
            factor *= 0.5
        h = h+factor*step
    if not converged:
        raise ValueError("Peroxide nonlinear BVP did not converge")
    return {"concentration_uM": h, "decomposition_uM_s": decomposition,
            "converged": True, "iterations": iteration+1,
            "residual_inf_uM_s": residual_inf,
            "kinetics": "NODEWISE_MICHAELIS_MENTEN" if km_uM is not None else "LINEAR_FIRST_ORDER"}
