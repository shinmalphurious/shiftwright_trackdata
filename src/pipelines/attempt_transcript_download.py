"""Download the transcript for the claimed task (current_transcript_task.json).

Output markers read by run_transcript_master:
    NO_TASK               nothing was claimed; no request is sent
    NEW_TRANSCRIPT        a transcript was saved
    FAILED                followed by RATE_LIMIT_DETECTED, TRANSCRIPT_UNAVAILABLE,
                          VIDEO_UNAVAILABLE or NON_RATE_LIMIT_FAILURE
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.providers.provider_factory import get_provider
from src.shared import transcript_queue as tq
from src.shared.paths import GENERATED

PYTHON = sys.executable

UNAVAILABLE = ("subtitles are disabled", "transcriptsdisabled", "no transcripts were found",
               "notranscriptfound", "video unavailable", "videounavailable")


def main():
    task = tq.load_task()
    if not task or task.get("status") != "claimed":
        print("NO_TASK")
        return

    video_id = task["video_id"]
    config = json.loads((GENERATED / "transcript_provider.json").read_text(encoding="utf-8"))
    provider = get_provider(config["provider"])
    print("VIDEO:", video_id)
    print("PROVIDER:", type(provider).__name__)

    attempts = task.get("attempts", 0) + 1
    try:
        transcript = provider.fetch(video_id)
    except Exception as ex:
        message = f"{type(ex).__name__} {ex}".lower()
        print("\nFAILED\n")
        print(str(ex).strip().splitlines()[0] if str(ex).strip() else type(ex).__name__)
        fields = {"attempts": attempts, "last_attempt": tq.now().isoformat()}

        if "429" in message or "too many requests" in message or "ipblocked" in message \
                or "blocking requests from your ip" in message:
            print("\nRATE_LIMIT_DETECTED")
            tq.update(video_id, status="rate_limited", next_attempt=tq.later(6 * 60), **fields)
            subprocess.run([PYTHON, "-m", "src.pipelines.record_transcript_429"])
        elif any(marker in message for marker in UNAVAILABLE):
            print("\nTRANSCRIPT_UNAVAILABLE")
            tq.update(video_id, status="unavailable", next_attempt=None, **fields)
        else:
            print("\nNON_RATE_LIMIT_FAILURE")
            give_up = attempts >= tq.MAX_ATTEMPTS
            tq.update(video_id, status="unavailable" if give_up else "failed",
                      next_attempt=None if give_up else tq.later(30 * attempts), **fields)
        tq.clear_task()
        raise SystemExit(1)

    tq.TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    outfile = tq.TRANSCRIPTS / f"{video_id}.json"
    outfile.write_text(json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")
    tq.update(video_id, status="downloaded", attempts=attempts, last_attempt=tq.now().isoformat(),
              next_attempt=None)
    tq.clear_task()

    print("NEW_TRANSCRIPT")
    print("segments:", len(transcript))
    print("saved:", outfile.relative_to(tq.TRANSCRIPTS.parents[2]))
    # The manifest's transcript counts are refreshed by run_transcript_master when it finishes,
    # so this never writes the manifest while run_guide_discovery is updating it


if __name__ == "__main__":
    main()
