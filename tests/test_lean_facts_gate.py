"""Regression: lean_facts (clone + temp dir + org script) must fail closed unless allow_effects is literally True.

Stdlib unittest (pytest collects it too). Synthetic only: no git, no network, no clone. Every effect
entry point used by lean_facts is replaced with a tripwire, and socket connects are refused.
"""

from __future__ import annotations

import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from szl_evidence import safety
from szl_evidence.audit import github, pipeline

NOT_TESTED = pipeline.NOT_TESTED


def _trip(name):
    def f(*a, **k):
        raise AssertionError(f"{name} must not run without allow_effects=True: {a!r}")
    return f


class LeanFactsGate(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.tmp = Path(self._td.name)
        p = [mock.patch.object(socket.socket, "connect", _trip("socket.connect")),
             mock.patch.object(safety, "run_argv", _trip("run_argv (git/gh clone, org script)")),
             mock.patch.object(tempfile, "mkdtemp", _trip("tempfile.mkdtemp"))]
        for x in p:
            x.start()
            self.addCleanup(x.stop)
        self.addCleanup(self._td.cleanup)

    def test_refused_by_default_before_any_effect(self):
        res = pipeline.lean_facts(self.tmp, {})
        self.assertEqual(res["state"], NOT_TESTED)
        self.assertIn("--allow-effects", res["reason"])

    def test_truthy_non_true_is_refused(self):
        for v in ("yes", 1, "True", object()):
            with self.subTest(v=v):
                self.assertEqual(pipeline.lean_facts(self.tmp, {}, allow_effects=v)["state"], NOT_TESTED)

    def test_run_github_default_does_not_clone_lutar_lean(self):
        out = self.tmp / "out"
        out.mkdir()
        gh = {"org": "o", "org_meta": {"public_repos": 0}, "auth": {}, "repos": [], "clone_root": str(self.tmp / "root"),
              "listing": {"denominator_state": "OBSERVED", "detail": ""}, "completed_at": "t"}
        with mock.patch.object(github, "collect", lambda *a, **k: gh), mock.patch.object(pipeline, "anon_hf_ids", lambda *a, **k: set()):
            st = pipeline.run_github("o", out, clone=False, deep=False, dry_run=False)
        self.assertEqual(st["lean"]["state"], NOT_TESTED)


class LeanFactsOptIn(unittest.TestCase):
    """The opt-in path still reaches the clone (inside an owned temp dir) and reports SOURCE_UNAVAILABLE on failure."""

    def test_opt_in_attempts_clone_in_owned_root(self):
        calls = []

        def fake_run(argv, **k):
            calls.append(list(map(str, argv)))
            return {"exit_code": 128, "output": "synthetic clone failure"}

        with mock.patch.object(socket.socket, "connect", _trip("socket.connect")), mock.patch.object(safety, "run_argv", fake_run), tempfile.TemporaryDirectory() as td:
            res = pipeline.lean_facts(Path(td), {}, allow_effects=True)
        self.assertEqual(res["state"], "SOURCE_UNAVAILABLE")
        self.assertEqual(len(calls), 1)
        self.assertIn("clone", calls[0])
        self.assertTrue(any("szl-holdings/lutar-lean" in a for a in calls[0]))


if __name__ == "__main__":
    unittest.main()
