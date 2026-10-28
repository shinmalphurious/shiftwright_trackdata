"""The three knowledge repositories, one JSON file per layout under generated/knowledge/:

    candidates/<track_id>.json  every research hypothesis with its current status
    validated/<track_id>.json   the source of truth: consensus-approved and inherited records only
    rejected/<track_id>.json    hypotheses the evidence turned down, kept for review

Each file: {"track_id", "track", "records": {record_id: record}}; record_id is
"<track_id>:<turn label>:<claim>". Records keep their research sources, evidence, confidence
history and the reason for their status.
"""
import json
from datetime import datetime, timezone

from src.shared.paths import GENERATED

ROOT = GENERATED / "knowledge"
KINDS = ("candidates", "validated", "rejected")


def record_id(track_id, label, claim):
    return f"{track_id}:{label}:{claim}"


def path(kind, track_id):
    return ROOT / kind / f"{track_id}.json"


def load(kind, track_id):
    p = path(kind, track_id)
    return json.loads(p.read_text(encoding="utf-8")).get("records", {}) if p.exists() else {}


def save(kind, track_id, track_name, records):
    p = path(kind, track_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        p.unlink(missing_ok=True)
        return
    p.write_text(json.dumps({"track_id": track_id, "track": track_name, "records": records},
                            indent=2, ensure_ascii=False), encoding="utf-8")


def track_ids(kind):
    folder = ROOT / kind
    return sorted(int(p.stem) for p in folder.glob("*.json")) if folder.exists() else []


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
