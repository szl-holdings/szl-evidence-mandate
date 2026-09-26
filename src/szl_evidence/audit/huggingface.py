"""Hugging Face estate audit (Phase 3): enumeration, card scorecards, functional tests.

Read-only. Spaces are never restarted: a Space that is not RUNNING is not requested over
HTTP (a request would wake it). Large weights are never downloaded; their headers are
validated with HTTP range requests instead.
"""

from __future__ import annotations

import ast
import io
import json
import re
import struct
import zipfile
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import quote

from ..adapters.http import CachedClient, paginate
from ..models import NOT_TESTED, UNAVAILABLE, UNKNOWN, utcnow
from .common import Axis, hf_token

HF = "https://huggingface.co"
DSS = "https://datasets-server.huggingface.co"
KINDS = {"model": "models", "dataset": "datasets", "space": "spaces"}
WEIGHT_EXT = (".safetensors", ".bin", ".gguf", ".onnx", ".pt", ".pth", ".h5", ".msgpack", ".npz", ".npy", ".ckpt", ".tflite")
NN_WEIGHT_EXT = (".safetensors", ".gguf", ".onnx", ".pt", ".pth", ".h5", ".msgpack", ".ckpt", ".tflite")
TOKENIZER_FILES = {"tokenizer.json", "tokenizer.model", "vocab.json", "vocab.txt", "spiece.model", "tokenizer_config.json"}
TASK_TAGS = {"text-generation", "text2text-generation", "text-classification", "token-classification", "question-answering", "summarization", "translation", "feature-extraction", "fill-mask", "image-classification", "conversational", "sentence-similarity"}

SECTIONS = {
    "intended_use": re.compile(r"(?im)^#+.*\b(intended use|uses|use cases?|how to use|usage)\b|intended (use|for)"),
    "out_of_scope": re.compile(r"(?i)out[- ]of[- ]scope|not intended (for|to)|should not be used|do not use"),
    "limitations": re.compile(r"(?i)\blimitations?\b|\bbias(es)?\b|\brisks?\b|caveats?"),
    "evaluation": re.compile(r"(?im)^#+.*\b(evaluation|results|benchmarks?|metrics)\b"),
    "training_data": re.compile(r"(?i)training data|trained on|fine-?tuned on|training set|data (is )?withheld|no training"),
    "reproduction": re.compile(r"(?i)reproduc|```(bash|sh|python|shell)?\s*\n[^`]*(python|pip|git clone|huggingface-cli|hf download|from_pretrained|load_dataset)"),
    "contact": re.compile(r"(?i)\bcontact\b|mailto:|github\.com/[^\s/]+/[^\s/]+/issues|discussions|security@|@[a-z0-9-]+\.[a-z]{2,}"),
    "non_establishment": re.compile(r"(?i)(does not (prove|establish|claim|guarantee|certify|demonstrate)|not (a|an) (proof|guarantee)|what (this|it) (is not|does not)|non-?claims?|not established|does not imply)"),
}
METRIC = re.compile(r"(?i)(accuracy|f1|exact match|pass@\d|bleu|rouge|perplexity|auc|precision|recall|win rate|score)\W{0,20}\d")
CAPABILITY = re.compile(r"(?i)(state[- ]of[- ]the[- ]art|\bSOTA\b|outperforms?|achieves? \d|beats|production[- ]ready|guarantee[sd]?|provabl[ey]|formally verified|\d+(\.\d+)?\s?% (accuracy|better|improvement|reduction)|best[- ]in[- ]class|world'?s first)")
GH_LINK = re.compile(r"https?://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)")
PII = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\+?\b\d{1,3}[\s.-]?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b"),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "credit_card_like": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}


def _url(kind: str, rid: str, path: str) -> str:
    prefix = "" if kind == "model" else f"{KINDS[kind]}/"
    return f"{HF}/{prefix}{rid}/resolve/main/{quote(path)}"


class HFCollector:
    def __init__(self, client: CachedClient, org: str):
        self.c = client
        self.org = org

    def list_kind(self, kind: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return paginate(self.c, f"{HF}/api/{KINDS[kind]}", {"author": self.org, "limit": 100, "full": "true", "cardData": "true"})

    def detail(self, kind: str, rid: str) -> dict[str, Any]:
        r = self.c.get(f"{HF}/api/{KINDS[kind]}/{rid}", params={"blobs": "true"})
        if not r.ok:
            return {"state": "SOURCE_UNAVAILABLE" if r.unavailable else UNAVAILABLE, "http": r.status}
        return r.json()

    def readme(self, kind: str, rid: str) -> dict[str, Any]:
        r = self.c.get(_url(kind, rid, "README.md"), max_bytes=400_000)
        if r.ok:
            return {"state": "PRESENT", "text": r.text(), "sha256": r.body_sha256, "retrieved_at": r.retrieved_at}
        if r.status == 404:
            return {"state": "ABSENT", "text": ""}
        return {"state": "SOURCE_UNAVAILABLE" if r.unavailable else UNAVAILABLE, "http": r.status, "text": ""}


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :]
    return text


def card_scorecard(kind: str, info: dict[str, Any], readme: dict[str, Any]) -> dict[str, Any]:
    body = strip_front_matter(readme.get("text", ""))
    card = info.get("cardData") or {}
    sib = [s.get("rfilename", "") for s in info.get("siblings", []) or []]
    lic = card.get("license") or next((t.split(":", 1)[1] for t in info.get("tags", []) if t.startswith("license:")), None)
    lic_file = [s for s in sib if re.match(r"(?i)^(license|licence|copying)(\.(md|txt))?$", s)]
    ax: dict[str, Axis] = {}
    if readme.get("state") != "PRESENT":
        ax["card_exists"] = Axis("FAIL" if readme.get("state") == "ABSENT" else "NOT_TESTED", f"README {readme.get('state')}")
    else:
        ax["card_exists"] = Axis("PASS", f"README.md {len(readme['text'])} chars")
    words = len(re.findall(r"\w+", body))
    ax["not_a_stub"] = Axis("PASS" if words >= 150 else ("PARTIAL" if words >= 40 else "FAIL"), f"{words} words in card body")
    if lic and lic_file:
        ax["license"] = Axis("PASS", f"declared {lic}; file {lic_file[0]}")
    elif lic:
        spdx_like = str(lic).lower() in {"mit", "apache-2.0", "cc-by-4.0", "cc-by-sa-4.0", "bsd-3-clause", "openrail", "cc0-1.0", "llama3", "gpl-3.0"}
        ax["license"] = Axis("PARTIAL" if spdx_like else "FAIL", f"declared {lic}; no LICENSE file in repo" + ("" if spdx_like else " (custom/other licence without text = unresolvable terms)"))
    else:
        ax["license"] = Axis("FAIL", "no licence declared")
    for key, rx in SECTIONS.items():
        m = rx.search(body)
        ax[key] = Axis("PASS" if m else "FAIL", f"matched {m.group(0)[:60]!r}" if m else "not found", "MEDIUM")
    if ax["evaluation"].state == "PASS" and not METRIC.search(body):
        ax["evaluation"] = Axis("PARTIAL", "evaluation heading present but no metric with a value", "MEDIUM")
    gh = sorted({f"{o}/{n.removesuffix('.git')}" for o, n in GH_LINK.findall(body)})
    ax["provenance"] = Axis("PASS" if any(g.lower().startswith("szl-holdings/") for g in gh) else ("PARTIAL" if gh else "FAIL"), f"github links: {gh[:5] or 'none'}", "MEDIUM")
    caps = [m.group(0) for m in CAPABILITY.finditer(body)][:5]
    unevidenced = bool(caps) and ax["evaluation"].state != "PASS"
    return {
        "axes": {k: v.to_dict() for k, v in ax.items()},
        "license_declared": lic or "NONE",
        "license_files": lic_file,
        "card_words": words,
        "github_links": gh,
        "capability_assertions": caps,
        "capability_without_evidence": unevidenced,
    }


# ------------------------------------------------------------------ models
def classify_model(info: dict[str, Any], body: str) -> dict[str, Any]:
    sib = info.get("siblings", []) or []
    names = [s.get("rfilename", "") for s in sib]
    sizes = {s.get("rfilename"): s.get("size") for s in sib}
    weights = [n for n in names if n.lower().endswith(WEIGHT_EXT)]
    weight_bytes = sum((sizes.get(n) or 0) for n in weights)
    lib = info.get("library_name") or (info.get("cardData") or {}).get("library_name")
    tags = set(info.get("tags", []))
    code = [n for n in names if n.endswith((".py", ".toml", ".cu", ".cpp", ".rs"))]
    if lib == "kernels" or "kernel" in tags or "kernels" in tags or (not weights and code and any("kernel" in n.lower() or "build" in n.lower() for n in names)):
        kind = "SOFTWARE_KERNEL"
    elif any(n.lower().endswith(NN_WEIGHT_EXT) for n in weights):
        kind = "TRAINED_ADAPTER" if "adapter_config.json" in [n.split("/")[-1] for n in names] else "TRAINED_WEIGHTS"
    elif weights:
        kind = "SMALL_ARRAYS"
    elif code:
        kind = "CODE_ONLY"
    else:
        kind = "DOCS_OR_CONFIG_ONLY"
    mistakable = []
    if kind in ("SOFTWARE_KERNEL", "SMALL_ARRAYS", "CODE_ONLY", "DOCS_OR_CONFIG_ONLY"):
        if info.get("pipeline_tag"):
            mistakable.append(f"pipeline_tag={info['pipeline_tag']}")
        if tags & TASK_TAGS:
            mistakable.append(f"task tags {sorted(tags & TASK_TAGS)}")
        if (info.get("cardData") or {}).get("model-index"):
            mistakable.append("model-index present")
        if re.search(r"(?i)\b(trained|fine-?tuned|parameters|\d+(\.\d+)?\s?[MB] params|checkpoint|inference)\b", body):
            mistakable.append("card uses trained-model language")
        if lib in ("transformers", "peft", "diffusers", "sentence-transformers", "gguf", "llama.cpp"):
            mistakable.append(f"library_name={lib}")
    coherence = []
    is_adapter = "adapter_config.json" in [n.split("/")[-1] for n in names]
    if lib == "transformers" and is_adapter:
        coherence.append("PEFT adapter declared with library_name=transformers (expected peft)")
    if lib == "transformers" and not is_adapter:
        if "config.json" not in names:
            coherence.append("transformers without config.json")
        if not any(n.endswith((".safetensors", ".bin")) for n in names) and "adapter_config.json" not in names:
            coherence.append("transformers without weights")
        if not (set(n.split("/")[-1] for n in names) & TOKENIZER_FILES):
            coherence.append("no tokenizer files")
    if lib == "peft" and "adapter_config.json" not in [n.split("/")[-1] for n in names]:
        coherence.append("peft without adapter_config.json")
    if lib in ("gguf", "llama.cpp") and not any(n.endswith(".gguf") for n in names):
        coherence.append(f"library {lib} without .gguf files")
    if any(n.endswith(".gguf") for n in names) and lib not in ("gguf", "llama.cpp", None):
        coherence.append(f"gguf files but library_name={lib}")
    return {"artifact_class": kind, "library": lib or "NONE", "weights": weights[:20], "weight_bytes": weight_bytes, "mistakable_for_trained_model": mistakable, "coherence_issues": coherence, "files": len(names)}


def _range(client: CachedClient, url: str, n: int) -> bytes | None:
    r = client.get(url, headers={"Range": f"bytes=0-{n - 1}"}, max_bytes=n, cache=False)
    if r.status in (200, 206):
        return r.body[:n]
    return None


def validate_weights_header(client: CachedClient, rid: str, info: dict[str, Any]) -> dict[str, Any]:
    names = [s.get("rfilename", "") for s in info.get("siblings", []) or []]
    out: dict[str, Any] = {}
    st = next((n for n in names if n.endswith(".safetensors")), None)
    if st:
        head = _range(client, _url("model", rid, st), 8)
        if head is None or len(head) < 8:
            out["safetensors"] = {"file": st, "state": "SOURCE_UNAVAILABLE"}
        else:
            hlen = struct.unpack("<Q", head)[0]
            if hlen > 50_000_000:
                out["safetensors"] = {"file": st, "state": "INVALID", "detail": f"implausible header length {hlen}"}
            else:
                hb = _range(client, _url("model", rid, st), 8 + hlen)
                try:
                    hdr = json.loads(hb[8:].decode("utf-8")) if hb else None
                    tensors = [k for k in (hdr or {}) if k != "__metadata__"]
                    out["safetensors"] = {"file": st, "state": "HEADER_VALID", "tensors": len(tensors), "dtypes": sorted({hdr[k].get("dtype") for k in tensors})[:5]}
                except (ValueError, UnicodeDecodeError, AttributeError):
                    out["safetensors"] = {"file": st, "state": "INVALID", "detail": "header JSON did not parse"}
    sizes = {s.get("rfilename"): s.get("size") for s in info.get("siblings", []) or []}
    for gg in [n for n in names if n.endswith(".gguf")][:8]:
        head = _range(client, _url("model", rid, gg), 8)
        key = f"gguf:{gg}"
        if head is None:
            out[key] = {"file": gg, "state": "SOURCE_UNAVAILABLE"}
        elif head[:4] == b"GGUF":
            out[key] = {"file": gg, "state": "HEADER_VALID", "version": struct.unpack("<I", head[4:8])[0]}
        else:
            out[key] = {"file": gg, "state": "INVALID", "bytes": sizes.get(gg), "detail": "file has .gguf extension but no GGUF magic"}
    return out


def parse_npy_header(data: bytes) -> dict[str, Any]:
    if data[:6] != b"\x93NUMPY":
        raise ValueError("not an npy array")
    major = data[6]
    if major == 1:
        hlen = struct.unpack("<H", data[8:10])[0]
        start = 10
    else:
        hlen = struct.unpack("<I", data[8:12])[0]
        start = 12
    header = ast.literal_eval(data[start : start + hlen].decode("latin1"))
    if not isinstance(header, dict):
        raise ValueError("bad header")
    dtype = str(header.get("descr"))
    if "O" in dtype:
        raise ValueError("object dtype (would require pickle)")
    shape = tuple(header.get("shape", ()))
    itemsize = int(re.sub(r"\D", "", dtype) or 1)
    n = 1
    for s in shape:
        n *= int(s)
    payload = len(data) - start - hlen
    if payload < n * itemsize:
        raise ValueError(f"truncated array: {payload} < {n * itemsize}")
    return {"dtype": dtype, "shape": list(shape)}


def load_small_arrays(client: CachedClient, rid: str, info: dict[str, Any], limit: int = 10_000_000) -> dict[str, Any]:
    sib = info.get("siblings", []) or []
    arrs = [s for s in sib if s.get("rfilename", "").endswith((".npz", ".npy"))]
    if not arrs:
        return {"state": NOT_TESTED, "reason": "no numpy arrays"}
    results = []
    for s in arrs[:5]:
        if (s.get("size") or 0) > limit:
            results.append({"file": s["rfilename"], "state": "TOO_LARGE_NOT_TESTED"})
            continue
        r = client.get(_url("model", rid, s["rfilename"]), max_bytes=limit + 1, cache=False)
        if not r.ok:
            results.append({"file": s["rfilename"], "state": "SOURCE_UNAVAILABLE" if r.unavailable else f"HTTP_{r.status}"})
            continue
        try:
            if s["rfilename"].endswith(".npz"):
                z = zipfile.ZipFile(io.BytesIO(r.body))
                infos = z.infolist()
                if len(infos) > 1000 or any(i.file_size > 50 * limit or (i.compress_size and i.file_size / i.compress_size > 100) for i in infos):
                    raise ValueError("npz exceeds archive limits (member count, size or compression ratio)")
                members = {i.filename: parse_npy_header(z.open(i).read(min(i.file_size, 50 * limit))) for i in infos[:50]}
                results.append({"file": s["rfilename"], "state": "LOADED", "arrays": members, "method": "npz parsed without pickle"})
            else:
                results.append({"file": s["rfilename"], "state": "LOADED", "array": parse_npy_header(r.body), "method": "npy parsed without pickle"})
        except (ValueError, zipfile.BadZipFile, SyntaxError) as e:
            results.append({"file": s["rfilename"], "state": "LOAD_FAILED", "detail": str(e)[:200]})
    overall = "LOADED" if all(x["state"] == "LOADED" for x in results) else ("LOAD_FAILED" if any(x["state"] == "LOAD_FAILED" for x in results) else results[0]["state"])
    return {"state": overall, "files": results}


def model_functional(client: CachedClient, rid: str, info: dict[str, Any], cls: dict[str, Any]) -> dict[str, Any]:
    names = [s.get("rfilename", "") for s in info.get("siblings", []) or []]
    out: dict[str, Any] = {}
    if "config.json" in names:
        r = client.get(_url("model", rid, "config.json"), max_bytes=2_000_000)
        if r.ok:
            try:
                cfg = r.json()
                out["config"] = {"state": "LOADED", "model_type": cfg.get("model_type", UNKNOWN), "architectures": cfg.get("architectures", UNKNOWN)}
            except ValueError:
                out["config"] = {"state": "LOAD_FAILED", "detail": "config.json is not valid JSON"}
        else:
            out["config"] = {"state": "SOURCE_UNAVAILABLE" if r.unavailable else f"HTTP_{r.status}"}
    else:
        out["config"] = {"state": "ABSENT"}
    if cls["artifact_class"] == "SOFTWARE_KERNEL":
        out["load"] = {"state": "NOT_A_MODEL_REPO", "reason": "software kernel (code), not trained weights"}
    elif cls["artifact_class"] in ("CODE_ONLY", "DOCS_OR_CONFIG_ONLY"):
        out["load"] = {"state": "NOT_A_MODEL_REPO", "reason": cls["artifact_class"]}
    elif cls["artifact_class"] == "SMALL_ARRAYS":
        out["load"] = load_small_arrays(client, rid, info)
    else:
        out["headers"] = validate_weights_header(client, rid, info)
        out["load"] = {"state": "TOO_LARGE_NOT_TESTED", "reason": f"{cls['weight_bytes'] / 1e9:.2f} GB of weights; no torch runtime in audit env; headers validated by range request instead"}
    return out


# ------------------------------------------------------------------ datasets
def pii_scan(rows: list[Any]) -> dict[str, int]:
    text = json.dumps(rows, default=str)[:500_000]
    hits = {}
    for k, rx in PII.items():
        n = len(rx.findall(text))
        if n:
            hits[k] = n
    return hits


def dataset_functional(client: CachedClient, rid: str, info: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    sp = client.get(f"{DSS}/splits", params={"dataset": rid})
    if not sp.ok:
        out["splits"] = {"state": classify_dss_error(sp), "http": sp.status, "detail": sp.text()[:300]}
        out["direct_files"] = direct_file_parse(client, rid, info)
        return out
    splits = sp.json().get("splits", [])
    out["splits"] = {"state": "PRESENT" if splits else "ABSENT", "items": [{"config": s["config"], "split": s["split"]} for s in splits][:20]}
    if not splits:
        return out
    first = splits[0]
    fr = client.get(f"{DSS}/first-rows", params={"dataset": rid, "config": first["config"], "split": first["split"]})
    if fr.ok:
        d = fr.json()
        feats = [f["name"] for f in d.get("features", [])]
        rows = [r.get("row") for r in d.get("rows", [])]
        out["slice"] = {"state": "LOADED", "config": first["config"], "split": first["split"], "features": feats, "rows_loaded": len(rows)}
        out["pii_patterns"] = pii_scan(rows)
    else:
        out["slice"] = {"state": classify_dss_error(fr), "http": fr.status, "detail": fr.text()[:300]}
        out["direct_files"] = direct_file_parse(client, rid, info)
    sz = client.get(f"{DSS}/size", params={"dataset": rid})
    if sz.ok:
        s = sz.json().get("size", {})
        out["size"] = {"state": "OBSERVED", "num_rows": (s.get("dataset") or {}).get("num_rows"), "splits": [{"config": x.get("config"), "split": x.get("split"), "num_rows": x.get("num_rows")} for x in s.get("splits", [])][:20], "partial": sz.json().get("partial")}
    else:
        out["size"] = {"state": UNAVAILABLE, "http": sz.status}
    # Card-declared schema and counts
    di = (info.get("cardData") or {}).get("dataset_info")
    if isinstance(di, list):
        di = di[0] if di else None
    if isinstance(di, dict):
        declared_feats = [f.get("name") for f in di.get("features", []) if isinstance(f, dict)]
        declared_rows = {s.get("name"): s.get("num_examples") for s in di.get("splits", []) if isinstance(s, dict)}
        obs_feats = (out.get("slice") or {}).get("features") or []
        schema_match = (sorted(declared_feats) == sorted(obs_feats)) if declared_feats and obs_feats else UNKNOWN
        obs_rows = {x["split"]: x["num_rows"] for x in (out.get("size") or {}).get("splits", [])}
        rows_match = {k: {"declared": v, "observed": obs_rows.get(k, UNKNOWN), "match": obs_rows.get(k) == v if k in obs_rows else UNKNOWN} for k, v in declared_rows.items()}
        out["card_schema"] = {"declared_features": declared_feats, "schema_match": schema_match, "row_counts": rows_match}
    else:
        out["card_schema"] = {"state": "NOT_DECLARED"}
    return out


def classify_dss_error(r: Any) -> str:
    t = r.text().lower() if not r.unavailable else ""
    if r.unavailable or "busier than usual" in t or "retry later" in t or "not ready" in t:
        return "SOURCE_UNAVAILABLE"
    if "no (supported) data files" in t:
        return "NO_TABULAR_DATA_FILES"
    if "dataset is empty" in t or "emptydataseterror" in t:
        return "EMPTY"
    if "casterror" in t or "couldn't cast" in t or "datasetgenerationerror" in t:
        return "LOAD_FAILED_SCHEMA_INCONSISTENT"
    return "LOAD_FAILED"


def direct_file_parse(client: CachedClient, rid: str, info: dict[str, Any], limit: int = 3_000_000) -> dict[str, Any]:
    """Fallback: fetch up to 3 small data files and parse them directly (json/jsonl/csv)."""
    import csv as _csv

    sib = [s for s in info.get("siblings", []) or [] if s.get("rfilename", "").lower().endswith((".jsonl", ".json", ".csv", ".ndjson")) and s.get("rfilename") not in ("README.md",)]
    sib = [s for s in sib if (s.get("size") or 0) <= limit][:3]
    if not sib:
        return {"state": NOT_TESTED, "reason": "no small json/jsonl/csv files to parse directly"}
    res = []
    for s in sib:
        r = client.get(_url("dataset", rid, s["rfilename"]), max_bytes=limit + 1)
        if not r.ok:
            res.append({"file": s["rfilename"], "state": "SOURCE_UNAVAILABLE" if r.unavailable else f"HTTP_{r.status}"})
            continue
        name = s["rfilename"].lower()
        try:
            if name.endswith((".jsonl", ".ndjson")):
                rows = [json.loads(x) for x in r.text().splitlines() if x.strip()]
            elif name.endswith(".json"):
                d = json.loads(r.text())
                rows = d if isinstance(d, list) else [d]
            else:
                rows = list(_csv.DictReader(io.StringIO(r.text())))
            keysets = {tuple(sorted(x.keys())) for x in rows if isinstance(x, dict)}
            res.append({"file": s["rfilename"], "state": "PARSED", "rows": len(rows), "distinct_key_sets": len(keysets)})
        except (ValueError, _csv.Error) as e:
            res.append({"file": s["rfilename"], "state": "PARSE_FAILED", "detail": str(e)[:160]})
    return {"state": "PARSED" if all(x["state"] == "PARSED" for x in res) else "MIXED", "files": res}


# ------------------------------------------------------------------ spaces
def space_functional(client: CachedClient, rid: str, info: dict[str, Any]) -> dict[str, Any]:
    """``client`` must be unauthenticated: credentials are never sent to Space apps."""
    rt = info.get("runtime") or {}
    stage = rt.get("stage") or UNKNOWN
    mapped = {"RUNNING": "RUNNING", "SLEEPING": "SLEEPING", "BUILD_ERROR": "BUILD_ERROR", "RUNTIME_ERROR": "RUNTIME_ERROR", "PAUSED": "PAUSED", "STOPPED": "PAUSED", "CONFIG_ERROR": "BUILD_ERROR", "NO_APP_FILE": "BUILD_ERROR", "BUILDING": "UNKNOWN", "RUNNING_BUILDING": "RUNNING"}.get(stage, "UNKNOWN")
    out: dict[str, Any] = {"runtime_stage_raw": stage, "runtime_state": mapped, "hardware": (rt.get("hardware") or {}).get("current") or UNKNOWN, "sdk": info.get("sdk") or UNKNOWN}
    domains = [d.get("domain") for d in rt.get("domains", []) if d.get("stage") == "READY"] or ([info.get("host", "").replace("https://", "")] if info.get("host") else [])
    if mapped != "RUNNING":
        out["http"] = {"state": NOT_TESTED, "reason": f"runtime {stage}; not requested (would wake/restart the Space)"}
        return out
    if info.get("private"):
        out["http"] = {"state": NOT_TESTED, "reason": "private Space; credentials are not sent to Space apps"}
        return out
    if not domains:
        out["http"] = {"state": NOT_TESTED, "reason": "no ready domain reported"}
        return out
    host = domains[0]
    probes = []
    paths = ["/"] + (["/config", "/gradio_api/info"] if info.get("sdk") == "gradio" else ["/health", "/api/health"])
    for p in paths:
        r = client.get(f"https://{host}{p}", max_bytes=65_536)
        title = ""
        if r.ok and b"<title" in r.body[:20000].lower():
            m = re.search(rb"(?is)<title[^>]*>(.*?)</title>", r.body)
            title = m.group(1).decode("utf-8", "replace").strip()[:120] if m else ""
        probes.append({"path": p, "status": r.status, "latency_ms": r.elapsed_ms, "title": title, "body_excerpt": re.sub(r"\s+", " ", r.text()[:240]) if not title else ""})
    ok_root = probes[0]["status"] == 200
    out["http"] = {"state": "RESPONDED" if ok_root else "DID_NOT_LOAD", "host": host, "probes": probes}
    return out


# ------------------------------------------------------------------ orchestration
def collect(org: str, cache_dir: Any, functional: bool, workers: int = 6, dry_run: bool = False) -> dict[str, Any]:
    token, src = hf_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    client = CachedClient(cache_dir, headers=headers, surface="huggingface", min_interval=0.05)
    col = HFCollector(client, org)
    anon = CachedClient(cache_dir, surface="huggingface-spaces", min_interval=0.05)
    started = utcnow()
    out: dict[str, Any] = {"org": org, "started_at": started, "auth": {"authenticated": bool(token), "source": src}, "listing": {}, "artifacts": []}
    listed: list[tuple[str, dict[str, Any]]] = []
    for kind in ("model", "dataset", "space"):
        items, meta = col.list_kind(kind)
        out["listing"][kind] = {**meta, "count": len(items)}
        listed += [(kind, x) for x in items]
    if dry_run:
        out["dry_run"] = True
        out["artifacts"] = [{"kind": k, "id": x["id"]} for k, x in listed]
        return out

    def work(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
        kind, lite = item
        rid = lite["id"]
        info = col.detail(kind, rid)
        if "state" in info and "id" not in info:
            return {"kind": kind, "id": rid, "state": info["state"], "listing": {k: lite.get(k) for k in ("private", "lastModified", "downloads", "likes")}}
        rd = col.readme(kind, rid)
        sib = info.get("siblings", []) or []
        rec: dict[str, Any] = {
            "kind": kind,
            "id": rid,
            "sha": info.get("sha"),
            "created_at": info.get("createdAt"),
            "last_modified": info.get("lastModified"),
            "private": info.get("private"),
            "gated": info.get("gated"),
            "disabled": info.get("disabled"),
            "downloads_30d": info.get("downloads", UNAVAILABLE) if kind != "space" else "NOT_APPLICABLE",
            "downloads_all_time": info.get("downloadsAllTime", UNAVAILABLE) if kind != "space" else "NOT_APPLICABLE",
            "likes": info.get("likes", UNAVAILABLE),
            "tags": info.get("tags", []),
            "pipeline_tag": info.get("pipeline_tag") or "NONE",
            "library": info.get("library_name") or "NONE",
            "sdk": info.get("sdk") if kind == "space" else None,
            "files": [{"path": s.get("rfilename"), "size": s.get("size", UNKNOWN)} for s in sib][:400],
            "file_count": len(sib),
            "total_bytes": sum((s.get("size") or 0) for s in sib) if sib and all("size" in s for s in sib) else UNKNOWN,
            "card": card_scorecard(kind, info, rd),
            "readme_sha256": rd.get("sha256"),
            "readme_text": rd.get("text", ""),
            "retrieved_at": utcnow(),
        }
        if kind == "model":
            rec["model_class"] = classify_model(info, strip_front_matter(rd.get("text", "")))
        if functional:
            try:
                if kind == "space":
                    rec["functional"] = space_functional(anon, rid, info)
                elif kind == "model":
                    rec["functional"] = model_functional(client, rid, info, rec["model_class"])
                else:
                    rec["functional"] = dataset_functional(client, rid, info)
            except Exception as e:  # noqa: BLE001 - an audit crash is recorded, never hidden
                rec["functional"] = {"state": "ERROR", "detail": f"{e.__class__.__name__}: {str(e)[:200]}"}
        else:
            rec["functional"] = {"state": NOT_TESTED, "reason": "--functional not requested"}
        return rec

    with ThreadPoolExecutor(max_workers=workers) as ex:
        out["artifacts"] = list(ex.map(work, listed))
    out["http"] = {"requests": client.requests + anon.requests, "unavailable": client.unavailable + anon.unavailable}
    out["completed_at"] = utcnow()
    client.close()
    anon.close()
    return out
