"""Claim the next ready video and write it to current_transcript_task.json.

Prints GLOBAL_TRANSCRIPT_PAUSE during a rate-limit pause and QUEUE_EMPTY when nothing is
left; in both cases no task file exists afterwards, so the download step does nothing.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import transcript_queue as tq
from src.shared.paths import GENERATED


def main():
    tq.clear_task()

    rate_limit_path = GENERATED / "transcript_rate_limit.json"
    rate_limit = json.loads(rate_limit_path.read_text(encoding="utf-8")) if rate_limit_path.exists() else {}
    pause_until = rate_limit.get("global_pause_until")
    if pause_until and datetime.fromisoformat(pause_until) > tq.now():
        print("GLOBAL_TRANSCRIPT_PAUSE until", pause_until)
        return

    queue = tq.load()
    have = tq.downloaded_ids()
    claimed = None
    for item in queue:
        if item["status"] != "ready_for_download":
            continue
        if item["video_id"] in have:
            item["status"] = "downloaded"
            continue
        item["status"] = "claimed"
        claimed = item
        break
    tq.save(queue)

    if claimed is None:
        print("QUEUE_EMPTY")
        return
    tq.save_task(claimed)
    print("claimed:", claimed["video_id"])


if __name__ == "__main__":
    main()
