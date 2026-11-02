"""One declared file cannot inflate input/row accounting via a path alias."""
import pytest
import yaml

from szl_evidence.manifest import ManifestError, load_manifest
from szl_evidence.verifier import verify


@pytest.mark.parametrize("alias", ["inputs/../inputs/records.csv", "link.csv", "linked/records.csv"])
def test_manifest_rejects_resolved_input_aliases(valid, alias):
    if alias == "link.csv":
        try:
            (valid / alias).symlink_to("inputs/records.csv")
        except OSError:
            pytest.skip("symlink creation not permitted")
    elif alias == "linked/records.csv":
        try:
            (valid / "linked").symlink_to("inputs", target_is_directory=True)
        except OSError:
            pytest.skip("symlink creation not permitted")
    path = valid / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["inputs"].append({**manifest["inputs"][0], "id": "alias", "path": alias})
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(ManifestError, match="duplicate manifest path"):
        load_manifest(path)
    receipt = verify(path)
    assert receipt["status"] == "ERROR"
    assert receipt["exit_code"] == 3
    assert receipt["invocation_count"] == 0


def test_loader_accepts_a_nonduplicate_contained_path(valid):
    path = valid / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["inputs"][0]["path"] = "inputs/../inputs/records.csv"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    assert load_manifest(path).inputs[0].path == "inputs/../inputs/records.csv"
