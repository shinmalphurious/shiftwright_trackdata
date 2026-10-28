"""Check that each downloaded transcript is a lap walkthrough: the speaker goes through the
track's corners in order.

For every transcript in research/youtube/transcripts it collects corner mentions in time order,
either numbered ("turn 3", "turn three", "T3") or named from the track's knowledge pack
("Abbey", "Bus Stop", placed by where they are on the lap). A drop back to the first corners
counts as a new lap, not as out of order.

Writes generated/transcript_verification.json:
    {video_id: {track_id, verdict, reason, corners, in_order, distinct, words_per_minute, ...}}
Verdicts:
    lap_walkthrough     corners are named or numbered in lap order (proven)
    likely_walkthrough  narrated driving (brakes, gears, apexes) but too few corners identified
                        to prove the order; worth a second look by a person or a model
    rejected            not a spoken lap
Later knowledge steps should read lap_walkthrough transcripts.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import transcript_queue as tq
from src.shared.paths import GENERATED

OUT = GENERATED / "transcript_verification.json"

MIN_DISTINCT = 4           # different corners mentioned (ovals: 3)
MIN_IN_ORDER = 0.65        # share of steps between mentions that move forward
MIN_WORDS_PER_MINUTE = 60  # less is music over a silent lap
MIN_CUES_PER_MINUTE = 6    # driving instructions per minute for a likely walkthrough
MIN_CUES_FOR_PROOF = 3     # ...and the least a proven walkthrough needs

NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}
NUMBER = r"(\d{1,2}|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + r")"
TURN = re.compile(r"\b(?:turns?|corners?)\s+(?:number\s+)?" + NUMBER + r"\b|\bt(\d{1,2})\b")

# Corner names too common in ordinary speech to place a corner
GENERIC_NAMES = {"loop", "the loop", "esses", "the esses", "kink", "the kink", "straight", "final",
                 "last", "first", "pit", "pits", "bridge", "carousel", "the carousel", "hairpin",
                 "chicane", "back", "front"}
CUES = re.compile(r"\b(brak\w*|brakes?|apex\w*|turn[- ]in|throttle|gas|lift\w*|downshift\w*|gears?|"
                  r"curbs?|kerbs?|left[- ]hander|right[- ]hander|exit|entry|marker|trail\w*)\b")
ORDINAL = re.compile(r"\b(first corner|next corner|final corner|last corner|first turn|next turn|"
                     r"final turn|last turn|the next one|start[- ]finish|braking zone)\b")


def segments(data):
    """[(start_seconds, text)] from youtube_transcript_api raw data or YouTube json3."""
    if isinstance(data, list):
        return [(s.get("start", 0), s.get("text", "")) for s in data]
    out = []
    for event in data.get("events", []):
        text = "".join(seg.get("utf8", "") for seg in event.get("segs", []))
        if text.strip():
            out.append((event.get("tStartMs", 0) / 1000, text))
    return out


def corner_names(track_id):
    """Named corner (lower case) -> its position on the lap (1 = first after the line)."""
    pack_path = GENERATED / "knowledge_packs" / f"{track_id}.json"
    if not pack_path.exists():
        return {}
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    corners = sorted(pack.get("named_corners", []), key=lambda c: c.get("start_pct") or 0)
    names = {}
    for position, corner in enumerate(corners, 1):
        for part in re.split(r"[/&]| and ", (corner.get("name") or "").lower()):
            name = re.sub(r"\b(corner|curve|turn)\b", "", part).strip(" -")
            if len(name) >= 4 and not re.fullmatch(r"t?\d+", name) and name not in GENERIC_NAMES:
                names.setdefault(name, position)
    return names


def mentions(segs, names):
    """(numbered, named): corner positions in the order spoken, repeats in a row collapsed.
    Numbers and names are kept apart because they count corners differently."""
    name_re = (re.compile(r"\b(" + "|".join(map(re.escape, sorted(names, key=len, reverse=True))) + r")\b")
               if names else None)
    numbered, named = [], []
    for _, text in segs:
        text = text.lower().replace("\n", " ")
        for m in TURN.finditer(text):
            raw = m.group(1) or m.group(2)
            number = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
            if 1 <= number <= 30 and (not numbered or numbered[-1] != number):
                numbered.append(number)
        if name_re:
            for m in name_re.finditer(text):
                position = names[m.group(1)]
                if not named or named[-1] != position:
                    named.append(position)
    return numbered, named


def in_order_share(sequence):
    if len(sequence) < 2:
        return 0.0
    forward = sum(1 for a, b in zip(sequence, sequence[1:])
                  if b > a or (b <= 2 and a >= 4))  # forward, or the start of the next lap
    return forward / (len(sequence) - 1)


def verify(data, track_id, names, oval):
    segs = segments(data)
    words = sum(len(t.split()) for _, t in segs)
    minutes = max((segs[-1][0] - segs[0][0]) / 60, 0.5) if segs else 1
    wpm = round(words / minutes)
    numbered, named = mentions(segs, names)
    # Judge on whichever way the speaker identifies corners more
    sequence, kind = max((numbered, "numbers"), (named, "names"), key=lambda s: len(set(s[0])))
    distinct = len(set(sequence))
    order = round(in_order_share(sequence), 2)
    need = 3 if oval else MIN_DISTINCT
    text = " ".join(t for _, t in segs).lower()
    cues = round(len(CUES.findall(text)) / minutes, 1)
    ordinals = len(ORDINAL.findall(text))

    if wpm < MIN_WORDS_PER_MINUTE:
        verdict, reason = "rejected", "too little speech"
    elif cues < MIN_CUES_FOR_PROOF:
        # Race broadcasts call out turns in order too, but say little about how to drive them
        verdict, reason = "rejected", "not a narrated lap"
    elif distinct >= need and order >= MIN_IN_ORDER:
        verdict, reason = "lap_walkthrough", f"corners in order by {kind}"
    elif distinct >= need:
        verdict, reason = "rejected", "corners not in lap order"
    elif cues >= MIN_CUES_PER_MINUTE and (ordinals >= 2 or distinct >= 2):
        verdict, reason = "likely_walkthrough", "narrated driving, corner order not provable"
    else:
        verdict, reason = "rejected", "not a narrated lap"
    return {"track_id": track_id, "verdict": verdict, "reason": reason, "corner_kind": kind,
            "corners": sequence[:80], "in_order": order, "distinct": distinct,
            "words_per_minute": wpm, "cues_per_minute": cues, "ordinal_phrases": ordinals}


def main():
    track_of = {item["video_id"]: item["track_id"] for item in tq.load()}
    ovals = set()
    catalog = GENERATED / "track_catalog.json"
    if catalog.exists():
        ovals = {t["track_id"] for t in json.loads(catalog.read_text(encoding="utf-8"))
                 if t.get("layout_path", "").lower().startswith("oval")}

    results = {}
    for path in sorted(tq.TRANSCRIPTS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            results[path.stem] = {"verdict": "rejected", "reason": "unreadable file"}
            continue
        track_id = track_of.get(path.stem)
        names = corner_names(track_id) if track_id else {}
        results[path.stem] = verify(data, track_id, names, track_id in ovals)

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    counts = {}
    for r in results.values():
        key = r["verdict"] if r["verdict"] != "rejected" else f"rejected: {r['reason']}"
        counts[key] = counts.get(key, 0) + 1
    print("transcripts:", len(results))
    for key, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {count:4}  {key}")


if __name__ == "__main__":
    main()
