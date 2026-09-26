"""Input hardening: path containment, size/count limits, safe parsing, safe subprocess, redaction."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Sequence

import yaml

MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_FILES = 20_000
MAX_ARCHIVE_RATIO = 100
MAX_ARCHIVE_TOTAL = 500 * 1024 * 1024


class UnsafeInput(Exception):
    """Raised when an input violates a containment or size rule."""


def contained(root: Path, candidate: str | os.PathLike) -> Path:
    """Resolve ``candidate`` under ``root``; reject traversal and symlink escape."""
    root_r = Path(root).resolve()
    raw = str(candidate)
    if os.path.isabs(raw) or raw.startswith(("\\\\", "//")):
        raise UnsafeInput(f"absolute path not allowed: {raw!r}")
    p = (root_r / raw).resolve()
    if p != root_r and root_r not in p.parents:
        raise UnsafeInput(f"path escapes root: {raw!r}")
    # Walk each component: a symlink anywhere inside that points outside is an escape.
    cur = root_r
    for part in Path(raw).parts:
        cur = cur / part
        if cur.is_symlink():
            target = cur.resolve()
            if target != root_r and root_r not in target.parents:
                raise UnsafeInput(f"symlink escape: {raw!r}")
    return p


def check_size(path: Path, limit: int = MAX_FILE_BYTES) -> int:
    size = path.stat().st_size
    if size > limit:
        raise UnsafeInput(f"oversized input {path.name}: {size} > {limit}")
    return size


def safe_walk(root: Path, max_files: int = MAX_FILES) -> list[Path]:
    """List regular files under root without following symlinks; bounded count."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if not Path(dirpath, d).is_symlink()]
        for f in filenames:
            p = Path(dirpath, f)
            if p.is_symlink():
                continue
            out.append(p)
            if len(out) > max_files:
                raise UnsafeInput(f"unexpected file count > {max_files} under {root}")
    return sorted(out)


def load_yaml(path: Path) -> Any:
    check_size(path)
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as e:
        raise UnsafeInput(f"malformed YAML in {path.name}: {e.__class__.__name__}") from e


def load_json(path: Path) -> Any:
    check_size(path)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        raise UnsafeInput(f"malformed JSON in {path.name}: line {e.lineno}") from e


def check_archive(path: Path) -> None:
    """Reject archive bombs and traversal members before anything is extracted."""
    total = 0
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) > MAX_FILES:
                raise UnsafeInput("archive has too many members")
            for i in infos:
                if i.filename.startswith(("/", "\\")) or ".." in Path(i.filename).parts:
                    raise UnsafeInput(f"archive member traversal: {i.filename!r}")
                total += i.file_size
                if i.compress_size and i.file_size / max(i.compress_size, 1) > MAX_ARCHIVE_RATIO:
                    raise UnsafeInput(f"archive bomb ratio in {i.filename!r}")
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as t:
            for n, m in enumerate(t):
                if n > MAX_FILES:
                    raise UnsafeInput("archive has too many members")
                if m.name.startswith(("/", "\\")) or ".." in Path(m.name).parts or m.issym() or m.islnk():
                    raise UnsafeInput(f"unsafe tar member: {m.name!r}")
                total += m.size
    if total > MAX_ARCHIVE_TOTAL:
        raise UnsafeInput("archive expands beyond limit")


def run_argv(
    argv: Sequence[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float = 300,
    max_output: int = 4000,
) -> dict[str, Any]:
    """Run a command as an argv list (never shell=True); capture bounded, redacted output."""
    import time

    if isinstance(argv, str):
        raise UnsafeInput("argv must be a sequence, not a shell string")
    t0 = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603 - argv list, no shell
            list(argv),
            cwd=cwd,
            env=env,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        rc: int | str = proc.returncode
        out = proc.stdout.decode("utf-8", "replace") + proc.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired as e:
        rc = "TIMEOUT"
        out = ((e.stdout or b"") + (e.stderr or b"")).decode("utf-8", "replace")
    except FileNotFoundError as e:
        rc = "NOT_FOUND"
        out = str(e)
    dur = round(time.monotonic() - t0, 2)
    out = redact(out)
    if len(out) > max_output:
        out = out[: max_output // 2] + "\n...[truncated]...\n" + out[-max_output // 2 :]
    return {"argv": list(argv), "exit_code": rc, "duration_s": dur, "output": out}


_REDACT_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(authorization:\s*(?:bearer|token)\s+)\S+"),
]


def redact(text: str) -> str:
    for p in _REDACT_PATTERNS:
        text = p.sub(lambda m: (m.group(1) if m.groups() else "") + "[REDACTED]", text)
    return text


def isolated_env(home: Path) -> dict[str, str]:
    """Minimal environment for running untrusted repo code: no tokens, redirected home dirs."""
    keep = ["PATH", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC", "PATHEXT", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE"]
    env = {k: os.environ[k] for k in keep if k in os.environ}
    h = str(home)
    env.update(
        {
            "HOME": h,
            "USERPROFILE": h,
            "APPDATA": h,
            "LOCALAPPDATA": h,
            "TEMP": h,
            "TMP": h,
            "HF_HOME": h,
            "XDG_CONFIG_HOME": h,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_CACHE_DIR": str(home / "pip-cache"),
            "PIP_NO_CACHE_DIR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "never",
        }
    )
    return env


def rmtree_force(path: Path) -> bool:
    """Delete a tree, clearing read-only bits (git pack files on Windows). Returns success."""
    import shutil
    import stat

    def _onexc(func, p, exc):  # noqa: ANN001
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass

    if not Path(path).exists():
        return True
    try:
        shutil.rmtree(path, onexc=_onexc)
    except TypeError:  # Python < 3.12
        shutil.rmtree(path, onerror=_onexc)
    except OSError:
        pass
    return not Path(path).exists()


def ensure_within(output_root: Path, target: Path) -> Path:
    """Refuse to write outside the configured output directory."""
    root = output_root.resolve()
    t = target.resolve()
    if t != root and root not in t.parents:
        raise UnsafeInput(f"refusing to write outside output dir: {target}")
    return t
