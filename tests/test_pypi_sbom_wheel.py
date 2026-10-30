"""The SBOM step may install only the wheel the release gate accepted."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, SkipTest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SBOM = ROOT / ".github/scripts/szl_pypi_sbom.py"
WORKFLOW = ROOT / ".github/workflows/publish-pypi.yml"
PYPROJECT = ROOT / "pyproject.toml"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if sys.version_info < (3, 11):
    raise SkipTest("SBOM wheel selection runs on the Python 3.12 publish workflow.")

sbom = load("pypi_sbom_wheel", SBOM)


def write_wheel(directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    wheel = directory / filename
    wheel.write_bytes(b"wheel")
    return wheel


class GatedWheelSelectionTests(TestCase):
    def test_stage_directory_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            write_wheel(dist / "stage-szl-evidence-mandate", "staging.whl")
            gated = write_wheel(dist / "szl-evidence-mandate", "gated.whl")
            self.assertEqual(sbom.select_gated_wheel(dist), gated)

    def test_filename_prefix_alone_is_not_a_stage_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            gated = write_wheel(dist / "szl-evidence-mandate", "stage-copy.whl")
            self.assertEqual(sbom.select_gated_wheel(dist), gated)

    def test_zero_eligible_wheels_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            with self.assertRaises(sbom.SbomWheelSelectionError) as caught:
                sbom.select_gated_wheel(dist)
        self.assertEqual(caught.exception.eligible, [])
        self.assertEqual(caught.exception.excluded, [])
        self.assertIn("found 0 eligible", str(caught.exception))

    def test_only_stage_wheels_fail_without_selecting_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            staged = write_wheel(dist / "stage-szl-evidence-mandate", "staging.whl")
            with self.assertRaises(sbom.SbomWheelSelectionError) as caught:
                sbom.select_gated_wheel(dist)
        self.assertEqual(caught.exception.eligible, [])
        self.assertEqual(caught.exception.excluded, [staged])

    def test_multiple_eligible_wheels_fail_without_choosing(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            write_wheel(dist / "stage-szl-evidence-mandate", "ignored.whl")
            first = write_wheel(dist / "one", "first.whl")
            second = write_wheel(dist / "two", "second.whl")
            with self.assertRaises(sbom.SbomWheelSelectionError) as caught:
                sbom.select_gated_wheel(dist)
        self.assertEqual(caught.exception.eligible, [first, second])
        self.assertIn("found 2 eligible", str(caught.exception))
        self.assertIn("first.whl", str(caught.exception))
        self.assertIn("second.whl", str(caught.exception))
        self.assertNotIn("ignored.whl", str(caught.exception).split("eligible (", 1)[1].split(")", 1)[0])


class PublishWorkflowGuardTests(TestCase):
    def setUp(self):
        self.workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    def test_version_and_publish_guards_stay_in_place(self):
        import tomllib

        with PYPROJECT.open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project["name"], "szl-evidence-mandate")
        self.assertEqual(project["version"], "0.1.2")
        publish = self.workflow["jobs"]["publish"]
        self.assertEqual(publish["if"], "github.event_name == 'release'")
        self.assertEqual(publish["permissions"]["id-token"], "write")
        action = next(step for step in publish["steps"] if str(step.get("uses", "")).startswith("pypa/gh-action-pypi-publish@"))
        self.assertIs(action["with"]["attestations"], True)
        self.assertIs(action["with"]["skip-existing"], False)
        self.assertIs(action["with"]["verify-metadata"], True)
        self.assertEqual(action["with"]["packages-dir"], "dist/")
        self.assertEqual(action["uses"], "pypa/gh-action-pypi-publish@7245906fb61fa33a13554f9d5fb856fe61758086")

    def test_sbom_artifact_is_separate_and_fails_closed(self):
        build = self.workflow["jobs"]["build"]["steps"]
        dists = next(step for step in build if step.get("name") == "Upload distributions (release only)")
        self.assertEqual(dists["if"], "github.event_name == 'release'")
        self.assertIn("dist/*.whl", dists["with"]["path"])
        self.assertNotIn("sbom", dists["with"]["path"])
        upload = next(step for step in build if step.get("name") == "Upload CycloneDX SBOM")
        self.assertNotIn("if", upload)
        self.assertEqual(upload["with"]["name"], "cyclonedx-sbom")
        self.assertEqual(upload["with"]["path"], "sbom/")
        self.assertEqual(upload["with"]["if-no-files-found"], "error")
        self.assertEqual(upload["with"]["retention-days"], 90)
        self.assertEqual(upload["uses"], "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9")
        generate = next(step for step in build if step.get("name") == "Generate CycloneDX SBOM")
        self.assertIn(".github/scripts/szl_pypi_sbom.py generate", generate["run"])
        self.assertNotIn("if", generate)
