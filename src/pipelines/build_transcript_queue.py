"""Build the transcript queue from every selected guide in generated/guide_catalog.

Safe to re-run: items already in the queue keep their status and attempt counts, videos
with a transcript on disk are marked downloaded, and each video is queued once even when
several layouts or cars select it. Waiting items the catalog no longer selects are dropped.
Run after run_guide_discovery.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import transcript_queue as tq
from src.shared.paths import GENERATED


def main():
    existing = {item["video_id"]: item for item in tq.load()}
    have = tq.downloaded_ids()
    queue, seen = [], set()

    for file in sorted((GENERATED / "guide_catalog").glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # being written by run_guide_discovery; picked up next time
        # Only layouts searched with the lap-guide rules (run_guide_discovery)
        if data.get("discovery_version", 1) < 2:
            continue
        for car, videos in data.get("selected_guides", {}).items():
            for video in videos:
                video_id = video["video_id"]
                if video_id in seen:
                    continue
                seen.add(video_id)
                item = existing.pop(video_id, None) or {
                    "track_id": data["track_id"],
                    "layout": data["layout"],
                    "car": car,
                    "video_id": video_id,
                    "title": video["title"],
                    "status": "ready_for_download",
                    "attempts": 0,
                    "last_attempt": None,
                    "next_attempt": None,
                    "caption_format": "json3",
                }
                queue.append(item)

    # Videos the catalog no longer selects: keep finished ones as history, drop the rest
    queue.extend(item for item in existing.values() if item["status"] in ("downloaded", "unavailable"))

    for item in queue:
        if item["video_id"] in have:
            item["status"] = "downloaded"
        elif item["status"] == "claimed":
            item["status"] = "ready_for_download"

    tq.save(queue)
    counts = {}
    for item in queue:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print("queued:", len(queue), counts)


if __name__ == "__main__":
    main()
