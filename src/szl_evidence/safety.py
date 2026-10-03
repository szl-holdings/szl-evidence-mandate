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


# The scanner and every output boundary share these credential formats. Group 1
# is the sensitive value; surrounding assignment context is not a credential.
# Keep detection thresholds/confidence unchanged when extending output defense.
CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("github_token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{36,})\b"), "HIGH"),
    ("github_fine_grained_pat", re.compile(r"\b(github_pat_[A-Za-z0-9_]{60,})\b"), "HIGH"),
    ("huggingface_token", re.compile(r"\b(hf_[A-Za-z]{34,})\b"), "HIGH"),
    ("aws_access_key_id", re.compile(r"\b((?:AKIA|ASIA)[0-9A-Z]{16})\b"), "HIGH"),
    ("openai_key", re.compile(r"\b(sk-(?:proj-)?[A-Za-z0-9_\-]{32,})\b"), "HIGH"),
    ("anthropic_key", re.compile(r"\b(sk-ant-[A-Za-z0-9_\-]{32,})\b"), "HIGH"),
    ("slack_token", re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b"), "HIGH"),
    ("stripe_live_key", re.compile(r"\b((?:sk|rk)_live_[A-Za-z0-9]{20,})\b"), "HIGH"),
    ("google_api_key", re.compile(r"\b(AIza[0-9A-Za-z_\-]{35})\b"), "HIGH"),
    ("cloudflare_api_token", re.compile(r"(?i)cloudflare[^\n]{0,40}?[=:]\s*['\"]?([A-Za-z0-9_\-]{40})\b"), "MEDIUM"),
    ("private_key_block", re.compile(r"(-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----)"), "HIGH"),
    ("jwt", re.compile(r"\b(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,})\b"), "MEDIUM"),
    ("generic_secret_assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|private[_-]?key)\b\s*[=:]\s*['\"]([A-Za-z0-9+/=_\-]{24,})['\"]"), "LOW"),
]

# A header-only replacement would leave key material behind. Delimiters are
# scanned once, including nested blocks; malformed/unclosed spans fail closed.
_PRIVATE_KEY_DELIMITER = re.compile(
    r"-----(?P<boundary>BEGIN|END) "
    r"(?P<kind>(?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY)-----"
)

# Retain the existing deliberately broader short-prefix and Authorization
# defenses as well as the canonical scanner's stricter matching thresholds.
_REDACT_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(authorization:\s*(?:bearer|token)\s+)\S+"),
]


def _redact_private_keys(text: str) -> str:
    parts: list[str] = []
    kinds: list[str] = []
    cursor = 0
    span_start = 0
    for match in _PRIVATE_KEY_DELIMITER.finditer(text):
        kind = match.group("kind")
        if match.group("boundary") == "BEGIN":
            if not kinds:
                span_start = match.start()
            kinds.append(kind)
        elif kinds:
            if kinds[-1] != kind:
                # A mismatched footer cannot establish where sensitive bytes end.
                break
            kinds.pop()
            if not kinds:
                parts.extend((text[cursor:span_start], "[REDACTED]"))
                cursor = match.end()
    if kinds:
        parts.extend((text[cursor:span_start], "[REDACTED]"))
        cursor = len(text)
    parts.append(text[cursor:])
    return "".join(parts)


def redact(text: str) -> str:
    text = _redact_private_keys(text)

    def replace_value(match: re.Match[str]) -> str:
        start, end = match.span(1)
        whole = match.group(0)
        return whole[:start - match.start()] + "[REDACTED]" + whole[end - match.start():]

    for _kind, pattern, _confidence in CREDENTIAL_PATTERNS:
        text = pattern.sub(replace_value, text)
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
