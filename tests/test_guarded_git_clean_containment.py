"""guarded_git_clean must make git target only the registered clone.

Inherited GIT_* variables (e.g. exported by a git hook) and a .git that is a link must not redirect
`git clean` to another work tree or index. Dry-run only: the `run` callable rewrites `clean -xdfq` to
`clean -xdn` and refuses any other git call except rev-parse, so these tests never delete a file.
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from szl_evidence.audit import effect_gate as eg

GIT = shutil.which("git")
pytestmark = pytest.mark.skipif(GIT is None, reason="git is not installed")
SETUP_ENV = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
SETUP_ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")


def _git(args, cwd):
    subprocess.run([GIT, *args], cwd=cwd, env=SETUP_ENV, check=True, capture_output=True)


def _repo(path, untracked, ignored=None):
    path.mkdir(parents=True)
    _git(["init", "-q"], path)
    _git(["config", "user.email", "t@example.invalid"], path)
    _git(["config", "user.name", "t"], path)
    (path / "tracked.txt").write_text("tracked", encoding="utf-8")
    if ignored:
        (path / ".gitignore").write_text(ignored + "\n", encoding="utf-8")
    _git(["add", "-A"], path)
    _git(["commit", "-qm", "init"], path)
    for name in untracked:
        (path / name).write_text("sentinel", encoding="utf-8")
    if ignored:
        (path / ignored).write_text("ignored sentinel", encoding="utf-8")
    return path


def _dry_run(argv, timeout=60, env=None, **_):
    argv = [str(a) for a in argv]
    if "clean" in argv:
        i = argv.index("clean")
        assert argv[i + 1:] == ["-xdfq"], argv
        argv = argv[: i + 1] + ["-xdn"]
    elif "rev-parse" not in argv:
        raise AssertionError(f"unexpected git call: {argv}")
    r = subprocess.run(argv, env=dict(os.environ if env is None else env), capture_output=True, text=True, timeout=timeout)
    return {"exit_code": r.returncode, "output": r.stdout + r.stderr}


def _would_remove(res):
    return sorted(line[len("Would remove "):].strip() for line in res["output"].splitlines() if line.startswith("Would remove "))


@pytest.fixture
def repos(tmp_path):
    victim = _repo(tmp_path / "victim", ["VICTIM_UNTRACKED.txt"], ".env.sentinel")
    root = eg.owned_tempdir("szl-gc-test-")
    clone = _repo(root / "clone", ["CLONE_UNTRACKED.txt"])
    yield tmp_path, victim, clone
    shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize("case", ["control", "git_dir_and_work_tree", "git_dir_only", "index_file", "config_worktree", "ceiling"])
def test_clean_targets_only_the_registered_clone(repos, monkeypatch, case):
    tmp, victim, clone = repos
    env = {
        "control": {},
        "git_dir_and_work_tree": {"GIT_DIR": str(victim / ".git"), "GIT_WORK_TREE": str(victim)},
        "git_dir_only": {"GIT_DIR": str(victim / ".git")},
        "index_file": {"GIT_INDEX_FILE": str(tmp / "empty.index")},
        "config_worktree": {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.worktree", "GIT_CONFIG_VALUE_0": str(victim)},
        "ceiling": {"GIT_CEILING_DIRECTORIES": str(tmp), "GIT_DISCOVERY_ACROSS_FILESYSTEM": "1"},
    }[case]
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    eg.register_clone(clone)
    res = eg.guarded_git_clean(_dry_run, GIT, clone, True)
    assert _would_remove(res) == ["CLONE_UNTRACKED.txt"]
    assert (victim / ".env.sentinel").exists() and (victim / "VICTIM_UNTRACKED.txt").exists()


def test_linked_git_dir_is_refused(repos):
    tmp, victim, clone = repos
    foreign = _repo(tmp / "foreign", [])
    _git(["config", "core.worktree", str(victim)], foreign)
    shutil.rmtree(clone / ".git")
    try:
        os.symlink(foreign / ".git", clone / ".git", target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"cannot create a directory symlink here: {exc}")
    eg.register_clone(clone)
    with pytest.raises(eg.EffectRefused):
        eg.guarded_git_clean(_dry_run, GIT, clone, True)
