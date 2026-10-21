"""Fail-closed gate for effectful audit steps (install, import, test, build, clone, git clean).

Every effectful step is refused unless BOTH hold:
  1. the caller passes allow_effects=True (the literal True; truthy strings/ints are refused), and
  2. the target path is sandboxed: a directory created by THIS process via owned_tempdir(), or a
     clone registered by THIS process via register_clone() strictly inside such a directory.
Paths are compared after os.path.realpath + normcase, so links that resolve outside an owned
root are refused. Stdlib only. Residual risk: a path swapped between check and use (TOCTOU).
"""

from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable

__all__ = ["EffectRefused", "require_opt_in", "owned_tempdir", "assert_owned_root", "assert_clone_slot",
           "register_clone", "assert_owned_clone", "guarded_git_clean"]


class EffectRefused(PermissionError):
    """An effectful audit step was refused by the fail-closed gate."""


_LOCK = threading.Lock()
_OWNED_ROOTS: set[str] = set()
_OWNED_CLONES: set[str] = set()


def _key(p: Any) -> str:
    return os.path.normcase(os.path.realpath(os.fspath(p)))


def _strictly_under(k: str, root: str) -> bool:
    if k == root:
        return False
    try:
        return os.path.commonpath([k, root]) == root
    except ValueError:  # different drives / mixed absolute-relative
        return False


def _under_owned_root(k: str) -> bool:
    with _LOCK:
        roots = tuple(_OWNED_ROOTS)
    return any(_strictly_under(k, r) for r in roots)


def require_opt_in(step: str, allow_effects: object) -> None:
    if allow_effects is not True:
        raise EffectRefused(f"{step}: effectful step refused; allow_effects must be the literal True (got {allow_effects!r})")


def owned_tempdir(prefix: str) -> Path:
    p = Path(tempfile.mkdtemp(prefix=prefix))
    with _LOCK:
        _OWNED_ROOTS.add(_key(p))
    return p


def assert_owned_root(path: Any, step: str) -> None:
    if path is None or os.path.islink(os.fspath(path)):
        raise EffectRefused(f"{step}: {path!r} is not a directory created by this process")
    with _LOCK:
        ok = _key(path) in _OWNED_ROOTS
    if not ok:
        raise EffectRefused(f"{step}: {path!r} is not a directory created by this process (owned_tempdir)")


def assert_clone_slot(dest: Any, step: str) -> None:
    """dest must lie strictly inside an owned root; if it already exists it must be our own clone."""
    s = os.fspath(dest)
    k = _key(s)
    if os.path.islink(s) or not _under_owned_root(k):
        raise EffectRefused(f"{step}: clone destination {s!r} is not inside a directory created by this process")
    if os.path.lexists(s):
        with _LOCK:
            ours = k in _OWNED_CLONES
        if not ours:
            raise EffectRefused(f"{step}: {s!r} exists and was not cloned by this process; refusing to delete it")


def register_clone(dest: Any) -> None:
    k = _key(dest)
    if not _under_owned_root(k):
        raise EffectRefused(f"register_clone: {os.fspath(dest)!r} is outside every owned root")
    with _LOCK:
        _OWNED_CLONES.add(k)


def assert_owned_clone(repo: Any, step: str) -> None:
    s = os.fspath(repo)
    if os.path.islink(s):
        raise EffectRefused(f"{step}: {s!r} is a link")
    k = _key(s)
    with _LOCK:
        ours = k in _OWNED_CLONES
    if not (ours and _under_owned_root(k) and os.path.isdir(os.path.join(k, ".git"))):
        raise EffectRefused(f"{step}: {s!r} is not a temp clone created by this process")


def guarded_git_clean(run: Callable[..., dict[str, Any]], git: str, repo: Any, allow_effects: object, timeout: int = 300) -> dict[str, Any]:
    """`git clean -xdfq` only on a clone this process created; fsmonitor disabled for the call."""
    require_opt_in("git clean -xdfq", allow_effects)
    assert_owned_clone(repo, "git clean -xdfq")
    return run([git, "-c", "core.fsmonitor=false", "-C", _key(repo), "clean", "-xdfq"], timeout=timeout)
