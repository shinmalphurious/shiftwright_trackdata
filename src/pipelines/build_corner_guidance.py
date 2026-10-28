"""Merge the per-video corner notes into one guide per layout.

Reads generated/corner_guidance/raw/*.json (from extract_corner_guidance). For each layout and
turn label it groups notes that say the same thing (by shared words) and counts how many
videos back each statement. With Ollama available it also writes one short coaching tip per
corner, from those statements only.

Writes generated/corner_guidance/<track_id>.json:
    {track_id, track_name, videos, corners: {"T3": {name, videos, cars,
        braking|gear|line|exit|mistakes: [{text, videos, cars}], tip}}, unplaced_notes}
Statements are ordered by how many videos agree. Notes the extractor could not place on a turn
are counted in unplaced_notes. build_track_knowledge_pack copies corners into the packs.

Usage:
    python -m src.pipelines.build_corner_guidance              summaries with the default model
    python -m src.pipelines.build_corner_guidance --no-tips    statements only, no model
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared import ollama
from src.shared.paths import GENERATED

RAW = GENERATED / "corner_guidance" / "raw"
ENRICHED = GENERATED / "corner_guidance" / "enriched"
OUT = GENERATED / "corner_guidance"
TIP_CACHE = OUT / "tip_cache.json"
FIELDS = ("braking", "gear", "line", "exit", "mistakes")
SAME_STATEMENT = 0.5     # word overlap (Jaccard) at which two notes count as the same statement
MAX_STATEMENTS = 4       # per field and corner

TIP_SYSTEM = """You write one coaching tip for one corner of a race track, for a sim racing \
driver. Use only the statements given; never add your own knowledge of the track. Keep the \
numbers (gears, brake pressure, marker boards). Lead with what the statements agree on. When a \
statement names its car in brackets, keep that car next to its gear or brake numbers. Never name a \
car the statements do not name. At most 40 words, plain instructions, no preamble."""
TIP_SCHEMA = {"type": "object", "required": ["tip"], "properties": {"tip": {"type": "string"}}}

STOPWORDS = set("""a an the and or but to of in on at for with into from by as is are be it this that
you your we so then just get go going really very bit up down out over off not no do can""".split())


def words(text):
    return {w for w in re.findall(r"[a-z0-9%]+", text.lower()) if w not in STOPWORDS}


def cluster(entries):
    """entries: [(text, video_id, car, confidence, method)] -> [{text, videos, cars, confidence,
    methods}] grouping similar statements. The representative text is the longest note in the
    group; confidence is the best placement among its notes. Ordered by how many videos agree,
    then by confidence."""
    groups = []
    for text, video, car, confidence, method in entries:
        w = words(text)
        for group in groups:
            union = w | group["words"]
            if union and len(w & group["words"]) / len(union) >= SAME_STATEMENT:
                group["videos"].add(video)
                if car:
                    group["cars"].add(car)
                if len(text) > len(group["text"]):
                    group["text"] = text
                group["words"] |= w
                group["confidence"] = max(group["confidence"], confidence)
                group["methods"].add(method)
                break
        else:
            groups.append({"text": text, "words": w, "videos": {video}, "cars": {car} if car else set(),
                           "confidence": confidence, "methods": {method}})
    groups.sort(key=lambda g: (-len(g["videos"]), -g["confidence"], -len(g["text"])))
    return [{"text": g["text"], "videos": len(g["videos"]), "cars": sorted(g["cars"]),
             "confidence": g["confidence"], "methods": sorted(g["methods"])}
            for g in groups[:MAX_STATEMENTS]]


def placed_notes(raw):
    """[(corner label, note, confidence, method)] for a video, and how many notes are unplaced.
    Uses enrich_corner_assignments' output when it exists, else the extractor's explicit labels."""
    enriched_path = ENRICHED / f"{raw['video_id']}.json"
    if enriched_path.exists():
        enriched = json.loads(enriched_path.read_text(encoding="utf-8"))
        placed = [(n["corner_id"], n, n["confidence"], n["assignment_method"])
                  for n in enriched["notes"] if n.get("status") == "assigned"]
        return placed, len(enriched["notes"]) - len(placed)
    placed = [(n["label"], n, 1.0, "explicit") for n in raw["corners"] if n.get("label")]
    return placed, len(raw["corners"]) - len(placed)


VEHICLES = json.loads((GENERATED / "vehicle_lookup.json").read_text(encoding="utf-8"))


def car_of(raw):
    """One name per car: the vehicle lookup's canonical name when the model's car or the video
    title matches an alias, else the discovery hint, else what the model said."""
    for text in (raw.get("car"), raw.get("title")):
        lower = (text or "").lower()
        for alias, canonical in sorted(VEHICLES.items(), key=lambda kv: -len(kv[0])):
            if alias in lower:
                return canonical
    hint = raw.get("car_hint")
    return hint if hint and hint != "general" else raw.get("car")


def tip_for(corner, label, track_name, model, cache):
    lines = []
    for field in FIELDS:
        for s in corner.get(field, []):
            cars = f" ({', '.join(s['cars'])})" if s["cars"] else ""
            lines.append(f"- {field}: {s['text']}{cars} [{s['videos']} video(s)]")
    if not lines:
        return None
    prompt = f"Track: {track_name}\nCorner: {label}" + (f" ({corner['name']})" if corner.get("name") else "") \
        + "\nStatements from track guide videos:\n" + "\n".join(lines)
    key = hashlib.sha1(f"{model}\n{prompt}".encode()).hexdigest()
    if key not in cache:
        cache[key] = ollama.chat_json(TIP_SYSTEM, prompt, TIP_SCHEMA, model=model, num_ctx=4096)["tip"].strip()
    return without_unknown_cars(cache[key], corner.get("cars", []))


def without_unknown_cars(tip, cars):
    """Remove bracketed car names the statements never gave (the model sometimes invents one)."""
    known = {c.lower() for c in cars}
    known_cars = {c.lower() for c in VEHICLES.values()} | set(VEHICLES)

    def keep(match):
        inner = match.group(1).strip().lower()
        if inner in known_cars and inner not in known:
            return ""
        return match.group(0)
    return re.sub(r"\s*\(([^()]{1,40})\)", keep, tip).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tips", action="store_true")
    parser.add_argument("--model", default=ollama.MODEL)
    args = parser.parse_args()

    by_track = defaultdict(list)
    for path in sorted(RAW.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        by_track[raw["track_id"]].append(raw)

    cache = json.loads(TIP_CACHE.read_text(encoding="utf-8")) if TIP_CACHE.exists() else {}
    use_tips = not args.no_tips
    if use_tips:
        try:
            if args.model not in ollama.available_models():
                raise SystemExit(f"Ollama has no model {args.model}; run: ollama pull {args.model}")
        except ollama.OllamaError as ex:
            print(f"{ex} - building without tips")
            use_tips = False

    built = corners_total = 0
    for track_id, raws in sorted(by_track.items()):
        pack_path = GENERATED / "knowledge_packs" / f"{track_id}.json"
        pack = json.loads(pack_path.read_text(encoding="utf-8")) if pack_path.exists() else {}
        names = {l: c["name"] for c in pack.get("named_corners", []) if c.get("name") for l in c.get("labels", [])}
        order = [t["label"] for t in pack.get("turns", [])]
        track_name = raws[0].get("track_name", "")

        notes = defaultdict(lambda: defaultdict(list))
        videos_at = defaultdict(set)
        cars_at = defaultdict(set)
        unplaced = 0
        methods_at = defaultdict(Counter)
        for raw in raws:
            car = car_of(raw)
            placed, unplaced_here = placed_notes(raw)
            unplaced += unplaced_here
            for label, note, confidence, method in placed:
                videos_at[label].add(raw["video_id"])
                methods_at[label][method] += 1
                if car:
                    cars_at[label].add(car)
                for field in FIELDS:
                    if note.get(field):
                        notes[label][field].append((note[field], raw["video_id"], car, confidence, method))

        corners = {}
        for label in sorted(notes, key=lambda l: order.index(l) if l in order else 999):
            corner = {"name": names.get(label), "videos": len(videos_at[label]),
                      "cars": sorted(cars_at[label]), "notes_by_method": dict(methods_at[label])}
            for field in FIELDS:
                if notes[label][field]:
                    corner[field] = cluster(notes[label][field])
            if use_tips:
                try:
                    corner["tip"] = tip_for(corner, label, track_name, args.model, cache)
                except ollama.OllamaError as ex:
                    print(f"  tip failed for {track_id} {label}: {ex}")
            corners[label] = corner

        (OUT / f"{track_id}.json").write_text(json.dumps({
            "track_id": track_id, "track_name": track_name, "videos": len(raws),
            "corners": corners, "unplaced_notes": unplaced,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        TIP_CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding="utf-8")
        built += 1
        corners_total += len(corners)
        print(f"{track_id} {track_name}: {len(corners)} corners from {len(raws)} videos "
              f"({unplaced} notes not placed on a turn)", flush=True)

    print(f"corner guidance: {built} layouts, {corners_total} corners")


if __name__ == "__main__":
    main()
