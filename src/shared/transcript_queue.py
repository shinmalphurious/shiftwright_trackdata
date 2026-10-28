"""Shared state for the transcript download queue.

generated/transcript_queue.json holds one item per YouTube video. Statuses:
    ready_for_download  waiting to be claimed
    claimed             handed to attempt_transcript_download (written to current_transcript_task.json)
    downloaded          transcript saved under research/youtube/transcripts/<video_id>.json
    failed              a non rate-limit error; retried after next_attempt, up to MAX_ATTEMPTS
    unavailable         the video has no usable transcript (captions off, removed, no English)
    rate_limited        YouTube answered 429; released again after next_attempt
"""
import json
from datetime import datetime, timedelta, timezone

from src.shared.paths import GENERATED, REPO_ROOT

QUEUE = GENERATED / "transcript_queue.json"
CURRENT_TASK = GENERATED / "current_transcript_task.json"
TRANSCRIPTS = REPO_ROOT / "research" / "youtube" / "transcripts"

MAX_ATTEMPTS = 3


def load():
    return json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.exists() else []


def save(queue):
    QUEUE.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def downloaded_ids():
    return {p.stem for p in TRANSCRIPTS.glob("*.json")}


def now():
    return datetime.now(timezone.utc)


def later(minutes):
    return (now() + timedelta(minutes=minutes)).isoformat()


def load_task():
    return json.loads(CURRENT_TASK.read_text(encoding="utf-8")) if CURRENT_TASK.exists() else None


def save_task(item):
    CURRENT_TASK.write_text(json.dumps(item, indent=2), encoding="utf-8")


def clear_task():
    CURRENT_TASK.unlink(missing_ok=True)


def update(video_id, **fields):
    """Set fields on the queue item for video_id. Returns the item, or None if it is not queued."""
    queue = load()
    for item in queue:
        if item["video_id"] == video_id:
            item.update(fields)
            save(queue)
            return item
    return None
