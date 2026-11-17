"""The canonical SBOM profile cannot silently lose hashed tooling or triggers."""
import re
from pathlib import Path

import yaml
from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]


def test_release_tooling_lock_has_hashed_transitive_pins_and_required_roots():
    ci = ROOT / 'requirements/ci'
    text = (ci / 'pypi-release.txt').read_text(encoding='utf-8')
    pins = {}
    for block in re.split(r'\n(?=\S)', text):
        first = block.splitlines()[0] if block else ''
        if not first or first.startswith('#'):
            continue
        match = re.match(r'([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)', first)
        assert match, f'Unpinned requirement: {first}'
        assert '--hash=sha256:' in block, first
        pins.setdefault(match[1].lower().replace('_', '-'), []).append(match[2])
    assert pins
    requirements = [Requirement(line) for line in (ci / 'pypi-release.in').read_text(encoding='utf-8').splitlines()
                    if line.strip() and not line.startswith('#')]
    assert {r.name for r in requirements} == {'build', 'twine', 'cyclonedx-bom', 'jsonschema', 'packaging'}
    for req in requirements:
        assert req.name in pins
        assert all(req.specifier.contains(Version(v), prereleases=True) for v in pins[req.name])
    assert '--universal' in text and '--generate-hashes' in text


def test_canonical_release_installs_only_hashed_build_tooling():
    text = (ROOT / '.github/workflows/publish-pypi.yml').read_text(encoding='utf-8')
    installs = re.findall(r'pip\s+install[^\n]*', text)
    assert len(installs) == 1
    assert '--require-hashes -r requirements/ci/pypi-release.txt' in installs[0]
    for name in ('pypi-release.in', 'pypi-release.txt'):
        assert text.count(f'      - "requirements/ci/{name}"') == 2
    assert text.count('      - ".github/scripts/szl_pypi_sbom.py"') == 2


def test_sbom_build_has_no_publishing_credentials_or_failure_bypass():
    workflow = yaml.safe_load((ROOT / '.github/workflows/publish-pypi.yml').read_text(encoding='utf-8'))
    assert workflow['permissions'] == {}
    build = workflow['jobs']['build']
    assert build['permissions'] == {'contents': 'read'}
    for name in ('Generate CycloneDX SBOM', 'Upload CycloneDX SBOM'):
        step = next(s for s in build['steps'] if s.get('name') == name)
        assert 'if' not in step
        assert not step.get('continue-on-error', False)
    publish = workflow['jobs']['publish']
    assert publish['if'] == "github.event_name == 'release'"
    assert publish['needs'] == 'build'
