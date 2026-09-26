"""Evidence admission for smoke results produced by an earlier harness revision.

Rule (documented, mechanical):
- A prior result whose clean install SUCCEEDED is admitted: the known harness defect
  (pip cache written into the repository, breaking setuptools flat-layout discovery) can
  only cause false install *failures*, never a false install success or a false test
  outcome. The HEAD SHA it ran against is recorded and compared to the current HEAD.
- A prior install failure of the form "No matching distribution found for <pkg>" is admitted
  only after independent confirmation that <pkg> does not exist on PyPI (JSON API 404).
- Every other prior failure is excluded and stays NOT_TESTED.
"""

from __future__ import annotations

import re
from typing import Any

from ..adapters.http import CachedClient
from ..models import NOT_TESTED, utcnow

NO_DIST = re.compile(r"No matching distribution found for ([A-Za-z0-9_.\-]+)")


def admit(prior: dict[str, Any], prior_heads: dict[str, str | None], current_heads: dict[str, str | None], label: str, cache: Any = None, client: CachedClient | None = None) -> dict[str, Any]:
    client = client or CachedClient(cache, surface="pypi", min_interval=0.1)
    admitted: dict[str, Any] = {}
    excluded: dict[str, str] = {}
    for name, res in prior.items():
        head_then = prior_heads.get(name)
        head_now = current_heads.get(name)
        meta = {"evidence_admission": label, "head_at_test": head_then, "head_now": head_now, "head_changed_since": (head_then != head_now) if head_then and head_now else "UNKNOWN", "admitted_at": utcnow()}
        if res.get("install_ok") is True:
            admitted[name] = {**res, **meta, "admission_rule": "install succeeded under prior harness (defect can only cause false failures)"}
            continue
        inst = next((s for s in res.get("steps", []) if s.get("step") == "install"), {})
        m = NO_DIST.search(str(inst.get("output", "")))
        if res.get("install_ok") is False and m:
            pkg = m.group(1)
            r = client.get(f"https://pypi.org/pypi/{pkg}/json")
            if r.status == 404:
                admitted[name] = {**res, **meta, "tests": {"state": NOT_TESTED, "reason": "install failed"}, "admission_rule": f"dependency '{pkg}' confirmed absent from PyPI (JSON API 404 at {r.retrieved_at})"}
                continue
            excluded[name] = f"dependency '{pkg}' lookup returned {r.status}; not confirmed"
            continue
        excluded[name] = "prior failure could be a harness artefact; not admitted"
    client.close()
    return {"admitted": admitted, "excluded": excluded}
