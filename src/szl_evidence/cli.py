"""szl-audit command-line interface. Every command emits a run receipt and supports --dry-run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .models import canonical_json, sha256_json, utcnow
from .receipts import write_receipt

DEFAULT_OUT = Path("reports")


def _emit_receipt(out: Path, kind: str, payload: dict[str, Any], started: str, status: str) -> Path:
    """Every CLI command's receipt joins the same hash chain as the audit stages (receipts/HEAD)."""
    from .audit.pipeline import receipt

    r = receipt(Path(out), kind, payload, started, status, ["CLI run receipt; see payload for the command's own result."])
    return Path(out) / "receipts" / f"{kind}-{r['run_id']}.json"


def _print(obj: Any, quiet: bool = False) -> None:
    if not quiet:
        print(json.dumps(obj, indent=2, sort_keys=True, default=str))


# ------------------------------------------------------------------ engine
def cmd_verify(a: argparse.Namespace) -> int:
    from .checks import applicable_checks
    from .manifest import ManifestError, load_manifest
    from .verifier import verify

    if a.dry_run:
        try:
            m = load_manifest(a.manifest)
            plan = [c.name for c in applicable_checks(m)]
        except (ManifestError, KeyError) as e:
            _print({"dry_run": True, "status": "ERROR", "error": str(e)})
            return 3
        _print({"dry_run": True, "manifest": str(m.path.name), "inputs": [i.id for i in m.inputs], "checks_planned": plan})
        return 0
    resolver = None
    if a.crossref:
        from .adapters.citations import CrossrefResolver

        resolver = CrossrefResolver()
    r = verify(a.manifest, resolver=resolver)
    rp = Path(a.receipt) if a.receipt else a.output / "receipts" / f"engine-verify-{r['run_id']}.json"
    write_receipt(r, rp)
    summary = {k: r.get(k) for k in ("status", "exit_code", "primary_reason", "reason_codes", "failures", "run_id", "receipt_sha256", "signature_state")}
    summary["receipt_path"] = str(rp)
    if r.get("pass_evidence"):
        summary["pass_evidence"] = {**r["pass_evidence"], "receipt_sha256": r["receipt_sha256"]}
    summary["non_pass"] = [{"check": i["check"], "status": i["result"]["status"], "reason": i["result"]["reason"], "detail": i["result"]["detail"]} for i in r.get("invocations", []) if i["result"]["status"] != "PASS"]
    if r.get("invariant_violations"):
        summary["invariant_violations"] = r["invariant_violations"]
    _print(summary, a.quiet)
    return int(r["exit_code"])


def cmd_verify_receipt(a: argparse.Namespace) -> int:
    from .verifier import verify_receipt

    started = utcnow()
    if a.dry_run:
        _print({"dry_run": True, "would_verify": str(a.receipt)})
        return 0
    r = json.loads(Path(a.receipt).read_text(encoding="utf-8"))
    res = verify_receipt(r)
    _print(res)
    _emit_receipt(a.output, "verify-receipt", {"target_sha256": sha256_json(r), "valid": res["valid"]}, started, "PASS" if res["valid"] else "FAIL")
    return 0 if res["valid"] else 1


def cmd_mutate(a: argparse.Namespace) -> int:
    from .manifest import load_manifest
    from .mutations import run_mutations

    started = utcnow()
    if a.dry_run:
        from .mutations import MUTATIONS

        _print({"dry_run": True, "mutations": [(m.id, m.name, m.target) for m in MUTATIONS]})
        return 0
    m = load_manifest(a.manifest)
    res = run_mutations(m.root)
    _print(res)
    rp = _emit_receipt(a.output, "engine-mutate", {"inputs_sha256": m.sha256, "summary": res.get("summary")}, started, "PASS" if not res.get("error") else "ERROR")
    print(f"receipt: {rp}", file=sys.stderr)
    bs = (res.get("summary") or {}).get("blind_spots", [])
    print(f"BLIND_SPOTS ({len(bs)}): {bs}", file=sys.stderr)
    return 0 if not res.get("error") else 3


def cmd_impact(a: argparse.Namespace) -> int:
    from .dependencies import DependencyGraph
    from .manifest import load_manifest
    from .safety import load_yaml

    started = utcnow()
    m = load_manifest(a.manifest)
    dep_in = (m.sections.get("dependencies") or {}).get("input")
    spec = m.input(dep_in) if dep_in else None
    if not spec:
        _print({"status": "ABSTAIN", "reason": "manifest declares no dependency graph"})
        return 2
    g = DependencyGraph.load(load_yaml(m.root / spec.path), m.root)
    current = g.evaluate()
    rep = {"current_evaluation": current}
    if not a.dry_run:
        rep["impact"] = g.impact(a.artifact_id)
    _print(rep)
    _emit_receipt(a.output, "engine-impact", {"inputs_sha256": m.sha256, "artifact": a.artifact_id}, started, "PASS")
    return 0


def cmd_revalidate(a: argparse.Namespace) -> int:
    from .dependencies import DependencyGraph
    from .manifest import load_manifest
    from .safety import load_yaml

    started = utcnow()
    m = load_manifest(a.manifest)
    spec = m.input((m.sections.get("dependencies") or {}).get("input", ""))
    if not spec:
        _print({"status": "ABSTAIN", "reason": "manifest declares no dependency graph"})
        return 2
    g = DependencyGraph.load(load_yaml(m.root / spec.path), m.root)
    g.evaluate()
    if a.dry_run:
        _print({"dry_run": True, "node": a.node, "state": g.nodes[a.node].state.value})
        return 0
    res = g.revalidate(a.node, a.output_sha)
    _print(res)
    _emit_receipt(a.output, "engine-revalidate", {"inputs_sha256": m.sha256, "node": a.node, "result": res["result"]}, started, "PASS")
    return 0


def cmd_package(a: argparse.Namespace) -> int:
    from .packaging import package

    started = utcnow()
    if a.dry_run:
        _print({"dry_run": True, "would_package": str(a.manifest), "into": str(a.pkg_output)})
        return 0
    idx = package(a.manifest, a.pkg_output)
    _print({k: v for k, v in idx.items() if k != "files"} | {"files": len(idx["files"])})
    _emit_receipt(a.output, "engine-package", {"inputs_sha256": idx["receipt_sha256"], "access": idx["access"], "copied": idx["files_copied"]}, started, "PASS")
    return 0


def cmd_engine_report(a: argparse.Namespace) -> int:
    from .audit.pipeline import save
    from .engine_stage import run_engine_stage

    started = utcnow()
    if a.dry_run:
        from .fixturegen import VARIANTS
        from .mutations import MUTATIONS

        _print({"dry_run": True, "fixtures": list(VARIANTS), "mutations": [m.id for m in MUTATIONS], "determinism_seeds": [0, 1, 12345]})
        return 0
    res = run_engine_stage(Path(a.fixtures), rebuild=a.rebuild)
    save(a.output, "engine", res)
    ok = all(f["match"] for f in res["fixtures"])
    _emit_receipt(a.output, "engine-report", {"inputs_sha256": sha256_json([f["receipt_sha256"] for f in res["fixtures"]]), "fixtures_matched": sum(f["match"] for f in res["fixtures"]), "blind_spots": res["mutations"]["summary"]["blind_spots"]}, started, "PASS" if ok else "FAIL")
    _print({"fixtures_matched": f"{sum(f['match'] for f in res['fixtures'])}/{len(res['fixtures'])}", "mutations": res["mutations"]["summary"], "determinism": res["determinism"]["byte_identical"]})
    return 0 if ok else 1


# ------------------------------------------------------------------ audits
def cmd_github(a: argparse.Namespace) -> int:
    from .audit.pipeline import run_github

    st = run_github(a.org, a.output, clone=a.clone, deep=a.deep, dry_run=a.dry_run, admit_smoke=getattr(a, "admit_smoke", None), stream=getattr(a, "stream", False))
    if a.dry_run:
        _print(st)
        return 0
    _print({"repos": len(st["gh"]["repos"]), "listing": st["gh"]["listing"], "cloned": sum(1 for r in st["gh"]["repos"] if r["clone"].get("ok")), "smoke_tested": sum(1 for v in st["smoke"].values() if v.get("install_ok") not in ("NOT_TESTED",))})
    return 0


def cmd_hf(a: argparse.Namespace) -> int:
    from .audit.pipeline import run_hf

    st = run_hf(a.org, a.output, functional_tests=a.functional, dry_run=a.dry_run)
    if a.dry_run:
        _print(st)
        return 0
    _print({"listing": st["hf"]["listing"], "public_counts": st["public_counts"], "conformance": [(c["dataset"], [(r.get("verifier"), r.get("matched"), r.get("fixtures")) for r in c.get("runs", [])]) for c in st["conformance"].get("corpora", [])]})
    return 0


def cmd_rescore(a: argparse.Namespace) -> int:
    from .audit.pipeline import rescore

    if a.dry_run:
        _print({"dry_run": True, "reads": "state/github.json"})
        return 0
    res = rescore(a.output)
    _print(res)
    return 0 if res.get("state") == "PASS" else 2


def cmd_reconcile(a: argparse.Namespace) -> int:
    from .audit.pipeline import run_reconcile

    if a.dry_run:
        _print({"dry_run": True, "requires": ["state/github.json", "state/hf.json"], "present": [p.name for p in (a.output / "state").glob("*.json")] if (a.output / "state").exists() else []})
        return 0
    rec = run_reconcile(a.output)
    if rec.get("state") == "ABSTAIN":
        _print(rec)
        return 2
    _print({"orphaned_hf": len(rec["orphaned_hf"]), "orphaned_repo_claims": len(rec["orphaned_repo_claims"]), "version_drift": len(rec["version_drift"]), "receipt_schema_ids": rec["receipt_schema_distinct"], "inventory_drift": [(c["location"], c["verdict"], c["evidence"]) for c in rec["inventory_drift"]][:10]})
    return 0


def cmd_zoomout(a: argparse.Namespace) -> int:
    from .audit.pipeline import run_zoomout
    from .audit.render import render_all

    if a.dry_run:
        _print({"dry_run": True})
        return 0
    z = run_zoomout(a.output)
    if z.get("state") == "ABSTAIN":
        _print(z)
        return 2
    written = render_all(a.output)
    from collections import Counter

    _print({"findings": len(z["findings"]), "by_severity": dict(Counter(f["severity"] for f in z["findings"])), "bandaids": len(z["bandaids"]), "reports_written": written})
    return 0


def cmd_report(a: argparse.Namespace) -> int:
    from .audit.render import render_all

    from .audit.pipeline import receipt

    started = utcnow()
    if a.dry_run:
        _print({"dry_run": True, "would_render_from": str(a.output / "state")})
        return 0
    written = render_all(a.output, public=getattr(a, "public", False))
    receipt(a.output, "report", {"inputs_sha256": sha256_json(written), "public": getattr(a, "public", False), "files": len(written)}, started, "PASS", ["Rendering only; no new measurement."])
    _print({"reports_written": written})
    return 0


def cmd_all(a: argparse.Namespace) -> int:
    for fn, ns in (
        (cmd_engine_report, argparse.Namespace(**{**vars(a), "fixtures": a.fixtures, "rebuild": False})),
        (cmd_github, argparse.Namespace(**{**vars(a), "org": a.github_org, "clone": True, "deep": a.deep})),
        (cmd_hf, argparse.Namespace(**{**vars(a), "org": a.hf_org, "functional": True})),
        (cmd_reconcile, a),
        (cmd_zoomout, a),
    ):
        rc = fn(ns)
        if a.dry_run:
            continue
        if rc not in (0, 1):
            return rc
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="szl-audit", description="Scientific Evidence Gate engine and estate audits (read-only).")
    p.add_argument("--version", action="version", version=f"szl-audit {__version__}")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--output", type=Path, default=DEFAULT_OUT, help="report/receipt output directory (default: reports/)")
    common.add_argument("--dry-run", action="store_true", help="plan only; no checks executed and nothing fetched beyond listings")
    sub = p.add_subparsers(dest="cmd", required=True)

    eng = sub.add_parser("engine", help="evidence gate engine")
    es = eng.add_subparsers(dest="ecmd", required=True)
    v = es.add_parser("verify", parents=[common])
    v.add_argument("manifest")
    v.add_argument("--receipt")
    v.add_argument("--quiet", action="store_true")
    v.add_argument("--crossref", action="store_true", help="resolve DOIs against live Crossref (network)")
    v.set_defaults(fn=cmd_verify)
    vr = es.add_parser("verify-receipt", parents=[common])
    vr.add_argument("receipt")
    vr.set_defaults(fn=cmd_verify_receipt)
    mu = es.add_parser("mutate", parents=[common])
    mu.add_argument("manifest")
    mu.set_defaults(fn=cmd_mutate)
    im = es.add_parser("impact", parents=[common])
    im.add_argument("artifact_id")
    im.add_argument("--manifest", required=True)
    im.set_defaults(fn=cmd_impact)
    rv = es.add_parser("revalidate", parents=[common])
    rv.add_argument("node")
    rv.add_argument("--manifest", required=True)
    rv.add_argument("--output-sha", required=True)
    rv.set_defaults(fn=cmd_revalidate)
    dry = argparse.ArgumentParser(add_help=False)
    dry.add_argument("--dry-run", action="store_true")
    pk = es.add_parser("package", parents=[dry])
    pk.add_argument("manifest")
    pk.add_argument("--output", dest="pkg_output", type=Path, required=True)
    pk.set_defaults(fn=cmd_package, output=DEFAULT_OUT)
    er = es.add_parser("report", parents=[common])
    er.add_argument("--fixtures", default="fixtures")
    er.add_argument("--rebuild", action="store_true")
    er.set_defaults(fn=cmd_engine_report)

    g = sub.add_parser("github", parents=[common])
    g.add_argument("--org", default="szl-holdings")
    g.add_argument("--clone", action="store_true")
    g.add_argument("--deep", action="store_true", help="smoke-test every Python/Node repo, not only the priority tier")
    g.add_argument("--stream", action="store_true", help="with --clone: clone, analyse, smoke-test and delete one repo at a time (bounded disk)")
    g.add_argument("--admit-smoke", type=Path, help="JSON {results, heads, label} of prior smoke evidence, admitted under audit/admission.py rules")
    g.set_defaults(fn=cmd_github)
    h = sub.add_parser("hf", parents=[common])
    h.add_argument("--org", default="SZLHOLDINGS")
    h.add_argument("--functional", action="store_true")
    h.set_defaults(fn=cmd_hf)
    sub.add_parser("rescore", parents=[common], help="offline: re-attribute recorded smoke outcomes and recompute scorecards").set_defaults(fn=cmd_rescore)
    sub.add_parser("reconcile", parents=[common]).set_defaults(fn=cmd_reconcile)
    sub.add_parser("zoomout", parents=[common]).set_defaults(fn=cmd_zoomout)
    rp = sub.add_parser("report", parents=[common], help="re-render reports from persisted state")
    rp.add_argument("--public", action="store_true", help="write a shareable copy to <output>/public/ without private repos/artifacts")
    rp.set_defaults(fn=cmd_report)
    al = sub.add_parser("all", parents=[common])
    al.add_argument("--github-org", default="szl-holdings")
    al.add_argument("--hf-org", default="SZLHOLDINGS")
    al.add_argument("--fixtures", default="fixtures")
    al.add_argument("--deep", action="store_true")
    al.set_defaults(fn=cmd_all)
    return p


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if getattr(a, "cmd", None) != "engine" or a.ecmd != "package":
        a.output = Path(a.output)
    else:
        a.output = DEFAULT_OUT
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())


_ = canonical_json
