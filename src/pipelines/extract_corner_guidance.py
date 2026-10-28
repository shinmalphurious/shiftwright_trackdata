"""Extract per-corner driving instructions from lap-guide transcripts with a local Ollama model.

Reads the transcripts that verify_lap_guide_transcripts passed and works through each one in
passages of about PASSAGE_SECONDS. For every passage the model is given the layout's corners
in lap order (T1, T2 "Remus", ...) and asked what the speaker says about each corner: braking,
gear, line, exit, mistakes. Small passages keep a local model accurate and tie each note to
the moment it was said, which allows two checks in code:
- a corner label is kept only when the speaker says that turn's number or name in or just
  before the passage (models otherwise number corners by counting braking zones);
- a note is kept only when most of its words were said in that passage, so the model cannot
  add its own track knowledge.
Unlabelled notes keep their order in the lap (sequence), so they can be matched to corners
later.

Writes generated/corner_guidance/raw/<video_id>.json, one per video. Resumable: videos already
extracted with the current PROMPT_VERSION are skipped.

Usage:
    python -m src.pipelines.extract_corner_guidance                 all passed transcripts
    python -m src.pipelines.extract_corner_guidance --limit 5
    python -m src.pipelines.extract_corner_guidance --video=11eXzdFgZYU --force
    python -m src.pipelines.extract_corner_guidance --include-likely --model qwen3:8b
Then run build_corner_guidance.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import ollama
from src.shared import transcript_queue as tq
from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED

PROMPT_VERSION = 3
OUT = GENERATED / "corner_guidance" / "raw"
VERIFICATION = GENERATED / "transcript_verification.json"

PASSAGE_SECONDS = 75     # transcript is sent in passages of about this length
MIN_GROUNDING = 0.5      # share of a note's content words that must be said in its passage
FIELDS = ("braking", "gear", "line", "exit", "mistakes")
MAIN_LAYOUT_WORDS = ("grand prix", "gp", "full", "road course", "international")

SYSTEM = """You read one passage of a sim racing track guide transcript and extract the driving \
instructions the speaker gives for each corner in that passage.
Rules:
- Report only what the speaker says in this passage. Never add your own knowledge of the track.
- Leave a field null when the speaker does not say it. Return no corners if the passage has no \
driving instructions (intros, setup talk, sponsor messages).
- Write each field as one short instruction (at most 20 words) using the speaker's own words and \
numbers: gears, brake pressure, marker boards, kerbs, reference points.
- braking: where and how hard to brake, trail braking. gear: gear for the corner. \
line: turn-in, apex, line through the corner. exit: throttle and track use on exit. \
mistakes: what the speaker warns against.
- label: the corner's label from the list, only when the speaker says its turn number or name \
in this passage, or the passage clearly continues the corner named just before. Braking markers \
are not turn numbers: never count them to guess a label. Otherwise null.
- spoken_as: how the speaker refers to the corner ("turn 3", "the hairpin", "next braking marker")."""

SCHEMA = {
    "type": "object",
    "required": ["car", "corners", "general_tips"],
    "properties": {
        "car": {"type": ["string", "null"]},
        "corners": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["label", "spoken_as", "braking", "gear", "line", "exit", "mistakes"],
                "properties": {
                    "label": {"type": ["string", "null"]},
                    "spoken_as": {"type": "string"},
                    "braking": {"type": ["string", "null"]},
                    "gear": {"type": ["string", "null"]},
                    "line": {"type": ["string", "null"]},
                    "exit": {"type": ["string", "null"]},
                    "mistakes": {"type": ["string", "null"]},
                },
            },
        },
        "general_tips": {"type": "array", "items": {"type": "string"}},
    },
}

STOPWORDS = set("""a an the and or but to of in on at for with into onto from by as is are be it this that
you your we our i my me so then just get got go going really very bit little try want need make
there here up down out over off not no don't do does can will well also more less when where""".split())
NUMBER_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty".split())}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6}


def stamp(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def passages(transcript):
    """[(start_seconds, text)] passages of about PASSAGE_SECONDS."""
    out, start, parts = [], None, []
    for seg in transcript:
        t = seg.get("start", 0)
        if start is None:
            start = t
        parts.append(seg.get("text", "").replace("\n", " "))
        if t - start >= PASSAGE_SECONDS:
            out.append((start, " ".join(parts)))
            start, parts = None, []
    if parts:
        out.append((start or 0, " ".join(parts)))
    return out


def content_words(text):
    words = set()
    for w in re.findall(r"[a-z0-9%]+", text.lower()):
        if w in STOPWORDS or len(w) < 2:
            continue
        words.add(w)
        # "4th" and "fourth", "3" and "three" are the same thing said or written differently
        number = re.match(r"(\d+)(st|nd|rd|th)?$", w)
        if number:
            words.add(number.group(1))
        elif w in NUMBER_WORDS:
            words.add(str(NUMBER_WORDS[w]))
        elif w in ORDINALS:
            words.add(str(ORDINALS[w]))
    return words


def grounded(text, said):
    words = content_words(text)
    return not words or len(words & said) / len(words) >= MIN_GROUNDING


def turns_said(text):
    """Turn numbers spoken in text: "turn 3", "T3", "turns four, five and six"."""
    text = text.lower()
    found = {int(n) for n in re.findall(r"\bt(\d{1,2})\b", text)}
    for m in re.finditer(r"\b(?:turns?|corners?)\b((?:[\s,]+(?:and\s+)?(?:\d{1,2}|[a-z]+)){1,5})", text):
        for word in re.findall(r"\d{1,2}|[a-z]+", m.group(1)):
            if word.isdigit():
                found.add(int(word))
            elif word in NUMBER_WORDS:
                found.add(NUMBER_WORDS[word])
            elif word != "and":
                break
    return found


def names_said(text, names):
    """Labels whose corner name is spoken in text."""
    text = text.lower()
    found = set()
    for label, name in names.items():
        for part in re.split(r"[/&]| and ", name.lower()):
            part = part.strip()
            if len(part) >= 4 and re.search(r"\b" + re.escape(part) + r"\b", text):
                found.add(label)
    return found


def normalise_label(raw, labels):
    m = re.search(r"(\d{1,2})", str(raw or ""))
    label = f"T{int(m.group(1))}" if m else None
    return label if label in labels else None


def corner_list(pack, names):
    return [turn["label"] + (f" ({names[turn['label']]})" if turn["label"] in names else "")
            for turn in pack.get("turns", [])]


def layout_for(title, default_track):
    """The layout a video is about, among the venue's layouts that have a knowledge pack: the one
    whose config name is in the title; else the current (not legacy) layout it was found for;
    else the venue's main layout (Grand Prix, full course)."""
    layouts = load_layouts()
    venue = layouts.get(default_track, {}).get("venue")
    candidates = [tid for tid, info in layouts.items() if venue and info["venue"] == venue]
    if not candidates:
        return default_track
    t = re.sub(r"[^a-z0-9]", "", (title or "").lower())

    def rank(track_id):
        info = layouts[track_id]
        config = info["config"].lower()
        squashed = re.sub(r"[^a-z0-9]", "", config)
        return ((GENERATED / "knowledge_packs" / f"{track_id}.json").exists(),
                bool(squashed) and squashed in t,
                not info["legacy"],
                track_id == default_track,
                not config or config == info["venue"].lower() or any(w in config for w in MAIN_LAYOUT_WORDS))
    return max(candidates, key=rank)


def extract(video_id, item, model):
    transcript = json.loads((tq.TRANSCRIPTS / f"{video_id}.json").read_text(encoding="utf-8"))
    track_id = layout_for(item.get("title"), item["track_id"])
    pack_path = GENERATED / "knowledge_packs" / f"{track_id}.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8")) if pack_path.exists() else {}
    labels = {t["label"] for t in pack.get("turns", [])}
    names = {label: c["name"] for c in pack.get("named_corners", []) if c.get("name")
             for label in c.get("labels", [])}
    track_name = load_layouts().get(track_id, {}).get("name") or pack.get("metadata", {}).get("name", "")
    corners_text = ", ".join(corner_list(pack, names)) or "unknown (use null labels)"

    notes, tips, car, dropped = [], [], None, 0
    last_label, previous = None, ""
    parts = passages(transcript)
    for index, (start, text) in enumerate(parts):
        user = (f"Track: {track_name}\nVideo title: {item.get('title', '')}\n"
                f"Corners on this layout in lap order: {corners_text}\n"
                f"Last corner the speaker named before this passage: {last_label or 'none yet'}\n"
                f"Just before this passage (context only, do not extract): ...{previous[-300:]}\n\n"
                f"Passage [{stamp(start)}]:\n{text}")
        reply = ollama.chat_json(SYSTEM, user, SCHEMA, model=model, num_ctx=8192)
        car = car or reply.get("car")
        context = f"{previous[-300:]} {text}"
        said = content_words(text)
        allowed = {f"T{n}" for n in turns_said(context)} | names_said(context, names)
        if last_label:
            allowed.add(last_label)  # the passage may continue the corner named just before
        tips += [tip for tip in reply.get("general_tips", []) if grounded(tip, said)]

        for corner in reply.get("corners", []):
            note = {"label": normalise_label(corner.get("label"), labels),
                    "spoken_as": corner.get("spoken_as", ""), "start_time": stamp(start),
                    "sequence": index}
            if note["label"] and note["label"] not in allowed:
                note["label_guess"], note["label"] = note["label"], None
            for field in FIELDS:
                value = (corner.get(field) or "").strip()
                if not value or value.lower() in ("null", "none", "n/a"):
                    continue
                if grounded(value, said):
                    note[field] = value
                else:
                    dropped += 1
            if any(note.get(f) for f in FIELDS):
                notes.append(note)

        spoken_labels = ({f"T{n}" for n in turns_said(text)} | names_said(text, names)) & labels
        if spoken_labels:
            last_label = max(spoken_labels, key=lambda l: text.lower().rfind(str(int(l[1:]))))
        previous = text

    return {
        "video_id": video_id, "track_id": track_id, "track_name": track_name,
        "title": item.get("title"), "car_hint": item.get("car"), "car": car,
        "model": model, "prompt_version": PROMPT_VERSION,
        "extracted_at": datetime.now(timezone.utc).isoformat(), "passages": len(parts),
        "corners": notes, "general_tips": tips, "dropped_ungrounded": dropped,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--model", default=ollama.MODEL)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--include-likely", action="store_true")
    args = parser.parse_args()

    if args.model not in ollama.available_models():
        raise SystemExit(f"Ollama has no model {args.model}; run: ollama pull {args.model}")
    OUT.mkdir(parents=True, exist_ok=True)
    verdicts = json.loads(VERIFICATION.read_text(encoding="utf-8")) if VERIFICATION.exists() else {}
    wanted = {"lap_walkthrough"} | ({"likely_walkthrough"} if args.include_likely else set())
    queue = {item["video_id"]: item for item in tq.load()}

    todo = []
    for video_id, verdict in verdicts.items():
        if args.video and video_id != args.video:
            continue
        if not args.video and verdict.get("verdict") not in wanted:
            continue
        if video_id not in queue:
            continue
        out = OUT / f"{video_id}.json"
        if out.exists() and not args.force:
            if json.loads(out.read_text(encoding="utf-8")).get("prompt_version") == PROMPT_VERSION:
                continue
        todo.append(video_id)
    if args.limit:
        todo = todo[:args.limit]
    print(f"transcripts to extract: {len(todo)}  model: {args.model}", flush=True)

    for n, video_id in enumerate(todo, 1):
        started = time.monotonic()
        try:
            result = extract(video_id, queue[video_id], args.model)
        except ollama.OllamaError as ex:
            print(f"[{n}/{len(todo)}] {video_id}: FAILED {ex}", flush=True)
            continue
        (OUT / f"{video_id}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                              encoding="utf-8")
        labelled = sum(1 for c in result["corners"] if c["label"])
        print(f"[{n}/{len(todo)}] {video_id} {result['track_name']}: {len(result['corners'])} notes "
              f"({labelled} on a named or numbered turn), {result['dropped_ungrounded']} dropped, "
              f"{time.monotonic() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
