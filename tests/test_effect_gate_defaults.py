"""Default-refusal contract for effectful audit steps (fail closed unless --allow-effects)."""

from __future__ import annotations

import argparse

import pytest

from szl_evidence.audit import conformance, functional, github
from szl_evidence.audit.effect_gate import EffectRefused, guarded_git_clean
from szl_evidence.cli import build_parser


def test_paired_verifier_refused_by_default(tmp_path):
    with pytest.raises(EffectRefused):
        functional.run_paired_verifier(tmp_path, [], tmp_path, "x")


def test_clone_refused_before_any_git_call(tmp_path, monkeypatch):
    monkeypatch.setattr(github, "run_argv", lambda *a, **k: (_ for _ in ()).throw(AssertionError("git must not run")))
    with pytest.raises(EffectRefused):
        github.clone_repo("o/r", tmp_path / "r")


def test_git_clean_refused_on_unowned_repo_even_with_opt_in(tmp_path):
    (tmp_path / ".git").mkdir()
    calls: list[object] = []
    with pytest.raises(EffectRefused):
        guarded_git_clean(lambda *a, **k: calls.append(a) or {}, "git", tmp_path, True)
    assert calls == []


def test_conformance_reports_not_tested_without_opt_in(monkeypatch):
    monkeypatch.setattr(conformance, "replay_fixture_corpus", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not run")))
    monkeypatch.setattr(conformance, "run_card_scorer", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not run")))
    hf = {"artifacts": [{"kind": "dataset", "id": "o/bench", "files": [{"path": "bench.jsonl"}]}, {"kind": "dataset", "id": "o/score", "files": [{"path": "score.py"}]}]}
    res = conformance.run_all(hf, None)
    assert [c["state"] for c in res["corpora"]] == ["NOT_TESTED", "NOT_TESTED"]
    assert all(c["runs"] == [] and "--allow-effects" in c["reason"] for c in res["corpora"])


def test_cli_flag_defaults_off_and_parses():
    p = build_parser()
    assert p.parse_args(["github"]).allow_effects is False
    assert p.parse_args(["github", "--clone", "--allow-effects"]).allow_effects is True
    assert p.parse_args(["hf", "--functional", "--allow-effects"]).allow_effects is True


def test_cli_github_refusal_exits_2(monkeypatch, tmp_path, capsys):
    from szl_evidence import cli
    from szl_evidence.audit import pipeline

    def refuse(*a, **k):
        assert k.get("allow_effects") is False
        raise EffectRefused("collect(clone=True): effectful step refused")

    monkeypatch.setattr(pipeline, "run_github", refuse)
    ns = argparse.Namespace(org="o", output=tmp_path, clone=True, deep=False, dry_run=False)
    assert cli.cmd_github(ns) == 2
    assert "--allow-effects" in capsys.readouterr().err
