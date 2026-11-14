# Contributing

1. `python -m venv .venv && .venv/bin/pip install -e ".[dev,test]"` (`test` adds the `sign` and
   `openislet` dependencies the full suite imports)
2. `.venv/bin/ruff check src tests --no-cache && .venv/bin/python -m pytest -q`
3. Fixtures are generated: edit `src/szl_evidence/fixturegen.py`, then run
   `python -c "from pathlib import Path; from szl_evidence.fixturegen import build_all; build_all(Path('fixtures'))"`
   and commit the regenerated `fixtures/`. CI fails if they drift.
4. CI installs from the hash-locked `requirements/ci/test.txt`. After changing a dependency in
   `pyproject.toml`, update `requirements/ci/test.in` to match and recompile it with the command
   in that file; `tests/test_ci_requirements.py` fails until the two agree.

Rules for changes:

- A new check must ship with a fixture that makes it FAIL or ABSTAIN, and a mutation it detects.
- Never convert missing evidence into 0, `false`, PASS, or an omitted field. Use
  `UNKNOWN`, `UNAVAILABLE` or `NOT_TESTED`.
- Never suppress a mutation `BLIND_SPOT`; fix it or document it.
- No `shell=True`, no pickle, no unsafe YAML. Remote content is untrusted input.
- Audits are read-only. Anything that writes to a remote service needs explicit owner approval.
