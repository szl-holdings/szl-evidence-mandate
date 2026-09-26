# Security

## Reporting

Report vulnerabilities privately via GitHub Security Advisories on the hosting repository
(or the organisation's published security contact). Do not open public issues for
suspected credential exposure.

## Defences implemented (Phase 7)

| Threat | Defence | Test |
|---|---|---|
| Path traversal / absolute paths in manifests | `safety.contained` resolves under root; manifest load refuses | `test_path_traversal_rejected`, `test_manifest_with_traversal_input_is_refused` |
| Symlink escape | component-wise symlink resolution; `safe_walk` never follows links | `test_symlink_escape_rejected` (skipped where the OS forbids symlink creation) |
| Archive bombs / member traversal | ratio, total-size, member-count and path checks before extraction | `test_archive_bomb_and_traversal_rejected` |
| Unexpected file counts / oversized inputs | bounded walks and per-file size limits | `test_oversized_and_unexpected_file_counts` |
| Duplicate manifest paths | refused at load | `test_duplicate_manifest_paths_refused` |
| Hash mismatch | registry/output hashes and invocation input hashes verified | `test_hash_mismatch_detected` |
| Malformed YAML/JSON | `yaml.safe_load` only; malformed input => ERROR/failed, never PASS | `test_malformed_*` |
| Shell injection | argv lists only; `run_argv` rejects strings; no `shell=True` anywhere (ruff S602/S604/S605) | `test_no_shell_strings_and_injection_inert` |
| Secret leakage | scanner stores type/location/fingerprint only; output and cache redaction; Authorization headers never cached | `test_29_*`, `test_secrets_redacted_from_output` |
| Writing outside output dir | `ReportWriter` refuses | `test_writer_refuses_outside_output_dir` |
| Running cloned code with credentials | fresh venv per repo; environment stripped to a PATH/system allow-list; HOME/APPDATA/HF_HOME redirected | `test_isolated_env_carries_no_credentials` |

## Residual risk (honest limitations)

- Clean-environment smoke tests execute repository code. Isolation is process-level
  (fresh venv, stripped environment), **not** a sandbox: code can still use the network
  and could reach the OS credential store (e.g. Windows Credential Manager). Run audits on
  a disposable machine or container when auditing untrusted organisations.
- Secret scanning covers the checked-out HEAD only; git history, CI logs and HF repo
  history are not scanned.
- Partial clones skip blobs larger than 2 MB; those files are not scanned.
- Receipts are `UNSIGNED` by default. An UNSIGNED receipt can be fully re-sealed by anyone
  who can edit it (published blind spot P03). Integrity hashes alone do not authenticate.
