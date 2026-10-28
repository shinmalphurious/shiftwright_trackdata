"""Return items to ready_for_download before the next claim.

Runs at the start of every pipeline cycle, when no download is in progress, so:
- claimed items are left over from an interrupted run and are released straight away;
- rate_limited and failed items are released once their next_attempt has passed.
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import transcript_queue as tq


def due(item):
    next_attempt = item.get("next_attempt")
    return not next_attempt or datetime.fromisoformat(next_attempt) <= tq.now()


def main():
    queue = tq.load()
    released = 0
    for item in queue:
        stale_claim = item["status"] == "claimed"
        retry = item["status"] in ("rate_limited", "failed") and due(item)
        if stale_claim or retry:
            item["status"] = "ready_for_download"
            released += 1
    tq.save(queue)
    tq.clear_task()
    print("released:", released)


if __name__ == "__main__":
    main()
