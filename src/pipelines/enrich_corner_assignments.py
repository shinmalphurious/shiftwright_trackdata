"""Place corner notes that the extractor could not tie to a turn, using evidence only.

Input: generated/corner_guidance/raw/<video_id>.json (extract_corner_guidance), the transcripts,
the knowledge packs (turn order and lap position), config/corner_aliases.json,
config/enrichment.json and, where it exists, telemetry (src/shared/telemetry_landmarks.py).
No language model is used and the model's own label guesses (label_guess) are ignored.

Locating. Every note is first found back in its transcript, which gives it a time and a
snippet for review (its provenance):
  whole_note      3 transcript lines share enough of the note's words;
  normalised      the same after evening out caption spelling ("breaking" = "braking",
                  "kerb" = "curb") and word endings;
  per_field       single fields (braking, line, ...) are found separately, close together in
                  time; notes combining several fields come from speech spread over a passage;
  context_window  found only in the lines just before the passage, which the extractor was
                  shown as context.
All searches stay inside the note's passage (plus that context), so a note can never be tied
to a different part of the video.

Placing, in order (confidence before decay):
  explicit 1.00         the extractor's label (the speaker said the turn number or name);
                        never changed here. Pass 0.
  alias_match 0.98      a corner alias (config or pack names) is said near the note and no
                        other corner's is. Pass 1.
  telemetry_match 0.95  between two fixed points (placed notes or a start/finish mention) in
  / sequence_match 0.93 the same lap: notes about braking matched in order to the corners
                        where real laps brake, when the counts agree; without telemetry, a
                        single note with exactly one corner between.
  lap_position <= 0.90  between two fixed points, the note's time becomes a lap position and
                        goes to the nearest corner (0.90 at the corner, 0.45 halfway).
Passes. Placements from one pass are fixed points for the next, up to max_passes. A placement's
confidence is the method's confidence times the weakest fixed point it relied on, minus
confidence_decay_per_pass for each pass after the first, so it can never exceed what it rests
on and never rises from pass to pass. Below minimum_confidence a note stays unassigned.

Writes:
    generated/corner_guidance/enriched/<video_id>.json      every note with corner_id,
        confidence, assignment_method, enrichment_pass, status, provenance and evidence
    generated/corner_guidance/enrichment_report.json        before/after, per method, per pass,
                                                            confidence distribution, per track
    generated/corner_guidance/enrichment_review.csv         one row per placed or candidate note
    generated/corner_guidance/provenance_report.json        notes the plain match could not
                                                            find, why, and whether recovered
    generated/corner_guidance/confidence_analysis.json      per threshold: notes recovered and
                                                            accuracy on hidden explicit notes

Usage:
    python -m src.pipelines.enrich_corner_assignments [--min-confidence 0.75] [--max-passes 3]
                                                       [--decay 0.02] [--no-analysis]
Then run build_corner_guidance.
"""
import argparse
import copy
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.pipelines.extract_corner_guidance import FIELDS, content_words, passages, stamp
from src.shared import transcript_queue as tq
from src.shared.paths import GENERATED, REPO_ROOT
from src.shared.telemetry_landmarks import landmarks, time_to_pct

GUIDANCE = GENERATED / "corner_guidance"
RAW = GUIDANCE / "raw"
OUT = GUIDANCE / "enriched"
REPORT = GUIDANCE / "enrichment_report.json"
REVIEW = GUIDANCE / "enrichment_review.csv"
PROVENANCE = GUIDANCE / "provenance_report.json"
ANALYSIS = GUIDANCE / "confidence_analysis.json"
ALIASES = REPO_ROOT / "config" / "corner_aliases.json"
SETTINGS = REPO_ROOT / "config" / "enrichment.json"

DEFAULTS = {
    "minimum_confidence": 0.75, "max_passes": 3, "confidence_decay_per_pass": 0.02,
    "method_confidence": {"explicit": 1.0, "alias_match": 0.98, "telemetry_match": 0.95,
                          "sequence_match": 0.93, "lap_position": 0.90},
    "locate": {"window_lines": 3, "min_note_share": 0.35, "min_field_words": 3, "min_field_share": 0.6,
               "max_field_spread_seconds": 30, "context_seconds": 25},
}
METHODS = ("explicit", "alias_match", "telemetry_match", "sequence_match", "lap_position")
ANALYSIS_THRESHOLDS = (0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.5)
ALIAS_BEFORE, ALIAS_AFTER = 2, 5   # transcript lines around the note searched for aliases
MAX_BRACKET_SECONDS = 100          # fixed points further apart than this do not bracket a note
MAX_BRACKET_PCT = 0.5
NAME_SUFFIXES = r"\b(bocht|corner|bend|curve|turn|kurve|virage|curva)\b"
# The start/finish line is a fixed point speakers announce: lap position 0 for what follows,
# 1 for what came before
START_FINISH = re.compile(r"\b(start[ /-]?finish|across the line|cross the line|crossing the line|"
                          r"main straight|front straight|start of the lap|start the lap)\b", re.I)
# Auto-captions spell some driving words differently from the model's notes
SPELLING = {"breaking": "brake", "braking": "brake", "break": "brake", "breaks": "brake", "brakes": "brake",
            "braked": "brake", "broke": "brake", "kerb": "curb", "kerbs": "curb", "kerbing": "curb",
            "curbs": "curb", "curbing": "curb", "tyre": "tire", "tyres": "tire", "tires": "tire"}


def load_settings(overrides=None):
    settings = copy.deepcopy(DEFAULTS)
    if SETTINGS.exists():
        stored = json.loads(SETTINGS.read_text(encoding="utf-8"))
        for key, value in stored.items():
            if isinstance(value, dict) and isinstance(settings.get(key), dict):
                settings[key].update({k: v for k, v in value.items() if not k.startswith("_")})
            elif not key.startswith("_"):
                settings[key] = value
    for key, value in (overrides or {}).items():
        if value is not None:
            settings[key] = value
    return settings


# --- words ------------------------------------------------------------------------------------

def norm_words(text):
    """Content words with caption spellings and simple word endings evened out."""
    out = set()
    for w in content_words(text):
        w = SPELLING.get(w, w)
        if len(w) > 4 and not w[0].isdigit():
            for suffix in ("ing", "ed", "es", "s"):
                if w.endswith(suffix) and len(w) - len(suffix) >= 4:
                    w = w[:-len(suffix)]
                    break
        out.add(SPELLING.get(w, w))
    return out


# --- track data -------------------------------------------------------------------------------

def clean_turns(pack):
    """[(label, pct)] in lap order, one marker per label. A label with several markers keeps
    the one that fits between its neighbours; markers that fit nowhere are dropped."""
    by_label = defaultdict(list)
    for t in pack.get("turns", []):
        by_label[t["label"]].append(t["lap_pct"])
    number = lambda label: int(re.sub(r"\D", "", label) or 0)
    labels = sorted(by_label, key=number)
    single = {l: p[0] for l, p in by_label.items() if len(p) == 1}
    out, dropped = [], []
    for i, label in enumerate(labels):
        options = by_label[label]
        if len(options) == 1:
            out.append((label, options[0]))
            continue
        lower = max((single[l] for l in labels[:i] if l in single), default=0.0)
        upper = min((single[l] for l in labels[i + 1:] if l in single), default=1.0)
        fitting = [p for p in options if lower < p < upper]
        if len(fitting) == 1:
            out.append((label, fitting[0]))
            dropped += [(label, p) for p in options if p != fitting[0]]
        else:
            dropped += [(label, p) for p in options]
    return out, dropped


def alias_claims(track_id, pack, config, turn_labels):
    """phrase -> ({labels claiming it}, confidence, source). Several labels = a collision."""
    claims = defaultdict(lambda: [set(), 1.0, set()])
    default = config.get("default_confidence", DEFAULTS["method_confidence"]["alias_match"])

    def add(phrase, label, conf, source):
        phrase = re.sub(r"\s+", " ", phrase.lower()).strip()
        if len(phrase) >= 4:
            entry = claims[phrase]
            entry[0].add(label)
            entry[1] = min(entry[1], conf)
            entry[2].add(source)

    for corner in pack.get("named_corners", []):
        labels = [l for l in dict.fromkeys(corner.get("labels", [])) if l in turn_labels]
        if len(labels) != 1:
            continue  # a name covering several turns cannot place a note on one of them
        if not corner.get("name"):
            continue  # an unnamed geometry region
        name = corner["name"].lower()
        if re.fullmatch(r"(turn|t|bocht)\s*\d+", name):
            continue
        # "Arie Luyendijk Bocht" and the fused Dutch form "Tarzanbocht" both lose the suffix
        base = re.sub(r"(?<=[a-z])bocht\b", "", re.sub(NAME_SUFFIXES, "", name)).strip(" -")
        for variant in {name, base, base.replace("ij", "y"), name.replace("ij", "y")}:
            if variant and not re.fullmatch(r"\d+", variant):
                add(variant, labels[0], default, "pack")
    for label, phrases in config.get("layouts", {}).get(str(track_id), {}).items():
        if not label.startswith("_"):
            for phrase in phrases:
                add(phrase, label, default, "config")
    for position, spec in config.get("global", {}).items():
        label = turn_labels[0] if position == "first" and turn_labels else \
            turn_labels[-1] if position == "last" and turn_labels else None
        for phrase in spec.get("aliases", []):
            if label:
                add(phrase, label, spec.get("confidence", default), "global")
    return {phrase: (labels, conf, sources) for phrase, (labels, conf, sources) in claims.items()}


def alias_table(track_id, pack, config, turn_labels):
    """phrase -> (label, confidence), leaving out phrases claimed by two corners."""
    return {phrase: (next(iter(labels)), conf)
            for phrase, (labels, conf, _) in alias_claims(track_id, pack, config, turn_labels).items()
            if len(labels) == 1 and next(iter(labels)) in turn_labels}


# --- locating notes ---------------------------------------------------------------------------

def best_window(words, segments, lo, hi, size, normalised):
    """(line index, share of words found) for the best window of `size` lines starting in [lo, hi).
    The index is the window's line sharing the most words, so the time is where it was said."""
    if not words:
        return None, 0.0
    read = norm_words if normalised else content_words
    best, best_share = None, 0.0
    for i, (start, _) in enumerate(segments):
        if not lo <= start < hi:
            continue
        window = read(" ".join(t for _, t in segments[i:i + size]))
        share = len(words & window) / len(words)
        if share > best_share:
            best, best_share = i, share
    if best is None:
        return None, 0.0
    lines = range(best, min(best + size, len(segments)))
    return max(lines, key=lambda j: (len(words & read(segments[j][1])), -j)), best_share


def fields_located(source, segments, lo, hi, cfg):
    """Fields found separately: {field: (line, share)} for those found, when they lie close."""
    found = {}
    for field in FIELDS:
        words = norm_words(source.get(field) or "")
        if len(words) < cfg["min_field_words"]:
            continue
        line, share = best_window(words, segments, lo, hi, cfg["window_lines"], True)
        if line is not None and share >= cfg["min_field_share"]:
            found[field] = (line, round(share, 2))
    if not found:
        return None
    first = next(f for f in FIELDS if f in found)  # speakers usually start with the braking point
    t0 = segments[found[first][0]][0]
    close = {f: v for f, v in found.items() if abs(segments[v[0]][0] - t0) <= cfg["max_field_spread_seconds"]}
    return first, close


def locate(source, segments, passage_start, passage_end, cfg):
    """Provenance of a note: {line, share, how, issue, fields} or {line: None, issue, ...}."""
    whole = " ".join(source[f] for f in FIELDS if source.get(f))
    size, need = cfg["window_lines"], cfg["min_note_share"]
    lo, hi = passage_start - 1, passage_end
    context_lo = passage_start - cfg["context_seconds"]
    use = set(cfg.get("strategies", ("whole_note", "normalised", "per_field", "context_window")))

    line, share = best_window(content_words(whole), segments, lo, hi, size, False)
    if share >= need:
        return {"line": line, "share": round(share, 2), "how": "whole_note", "issue": None}
    if "normalised" in use:
        line, share = best_window(norm_words(whole), segments, lo, hi, size, True)
        if share >= need:
            return {"line": line, "share": round(share, 2), "how": "normalised", "issue": "spelling_variant"}
    hit = fields_located(source, segments, lo, hi, cfg) if "per_field" in use else None
    if hit:
        first, close = hit
        return {"line": close[first][0], "share": close[first][1], "how": "per_field",
                "issue": "multi_field_spread", "fields": {f: v[1] for f, v in close.items()}}
    if "context_window" in use:
        line, share = best_window(norm_words(whole), segments, context_lo, hi, size, True)
        if share >= need:
            return {"line": line, "share": round(share, 2), "how": "context_window", "issue": "context_window"}
        hit = fields_located(source, segments, context_lo, hi, cfg)
        if hit:
            first, close = hit
            return {"line": close[first][0], "share": close[first][1], "how": "context_window",
                    "issue": "context_window", "fields": {f: v[1] for f, v in close.items()}}
    passage_words = norm_words(" ".join(t for s, t in segments if lo <= s < hi))
    words = norm_words(whole)
    passage_share = len(words & passage_words) / len(words) if words else 0.0
    # The words are in the passage but never together: the model summarised several sentences.
    # Otherwise it reworded them. Neither can be traced to a moment, so the note stays unlocated.
    issue = "summarised_across_passage" if passage_share >= 0.5 else "paraphrased"
    return {"line": None, "share": round(share, 2), "how": None, "issue": issue,
            "passage_share": round(passage_share, 2)}


# --- stages -----------------------------------------------------------------------------------

def assign(note, label, confidence, method, evidence, enrichment_pass=0):
    note.update(corner_id=label, confidence=round(confidence, 3), assignment_method=method,
                enrichment_pass=enrichment_pass, status="assigned",
                evidence={**note.get("evidence", {}), **evidence})


def alias_stage(note, segments, aliases, require_spoken=False):
    """(label, confidence, evidence) when exactly one corner's alias is said near the note. With
    require_spoken the note must also refer to the corner by that name (its spoken_as)."""
    i = note["_line"]
    text = " ".join(t for _, t in segments[max(i - ALIAS_BEFORE, 0):i + ALIAS_AFTER]).lower()
    spoken = (note.get("spoken_as") or "").lower()
    hits = {}
    for phrase, (label, conf) in aliases.items():
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, text) and (not require_spoken or re.search(pattern, spoken)):
            hits.setdefault(label, (phrase, conf))
    if len(hits) != 1:
        return None
    label, (phrase, conf) = next(iter(hits.items()))
    return label, conf, {"alias": phrase}


def fixed_points(notes, segments):
    """Placed notes (at their corner, with their confidence) and start/finish mentions."""
    points = [{"_t": n["_t"], "pct_after": n["_pct"], "pct_before": n["_pct"], "name": n["corner_id"],
               "confidence": n["confidence"]}
              for n in notes if n.get("corner_id") and n.get("_t") is not None]
    points += [{"_t": start, "pct_after": 0.0, "pct_before": 1.0, "name": "start/finish", "confidence": 1.0}
               for start, text in segments if START_FINISH.search(text)]
    return sorted(points, key=lambda p: p["_t"])


def brackets(notes, points):
    """For each unplaced, located note: the fixed points just before and after it, when they are
    close in time and in the same lap."""
    out = {}
    for n in notes:
        if n.get("corner_id") or n.get("_t") is None:
            continue
        before = [p for p in points if p["_t"] <= n["_t"]]
        after = [p for p in points if p["_t"] >= n["_t"]]
        if not before or not after:
            continue
        a, b = before[-1], after[0]
        a_pct, b_pct = a["pct_after"], b["pct_before"]
        if b["_t"] - a["_t"] > MAX_BRACKET_SECONDS or not 0 < b_pct - a_pct <= MAX_BRACKET_PCT:
            continue  # too far apart, or a new lap starts in between
        out[id(n)] = {"a_t": a["_t"], "b_t": b["_t"], "a_pct": a_pct, "b_pct": b_pct,
                      "after": a["name"], "before": b["name"],
                      "anchor_confidence": min(a["confidence"], b["confidence"])}
    return out


def derived(settings, method, anchor_confidence, enrichment_pass, factor=1.0):
    """Confidence of a placement that rests on fixed points: never above the weakest of them,
    lower again for each later pass."""
    base = settings["method_confidence"][method] * factor
    return base * anchor_confidence - settings["confidence_decay_per_pass"] * max(enrichment_pass - 1, 0)


def sequence_stage(notes, turns, lm, settings, enrichment_pass):
    """Stage 3 for all notes of a video (notes between the same two fixed points go together).
    Returns the number placed."""
    groups = defaultdict(list)
    for n in notes:
        if n.get("_bracket") and not n.get("corner_id"):
            br = n["_bracket"]
            groups[(br["a_t"], br["b_t"])].append(n)
    placed = 0
    for members in groups.values():
        br = members[0]["_bracket"]
        between = [l for l, p in turns if br["a_pct"] < p < br["b_pct"]]
        members.sort(key=lambda n: n["_t"])
        evidence = {"after": br["after"], "before": br["before"], "corners_between": between,
                    "anchor_confidence": br["anchor_confidence"]}
        if lm and between:
            braking_corners = [l for l in between if l in lm["braking_turns"]]
            braking_notes = [n for n in members if n.get("braking")]
            if braking_notes and len(braking_notes) == len(braking_corners):
                conf = derived(settings, "telemetry_match", br["anchor_confidence"], enrichment_pass)
                if conf >= settings["minimum_confidence"]:
                    for n, label in zip(braking_notes, braking_corners):
                        assign(n, label, conf, "telemetry_match",
                               {**evidence, "braking_corners_between": braking_corners,
                                "telemetry_laps": lm["laps"]}, enrichment_pass)
                        placed += 1
                continue
        if not lm and len(between) == 1 and len(members) == 1:
            conf = derived(settings, "sequence_match", br["anchor_confidence"], enrichment_pass)
            if conf >= settings["minimum_confidence"]:
                assign(members[0], between[0], conf, "sequence_match", evidence, enrichment_pass)
                placed += 1
            else:
                candidate(members[0], between[0], conf, "sequence_match", evidence, enrichment_pass)
    return placed


def candidate(note, label, confidence, method, evidence, enrichment_pass):
    """Keep the best rejected placement for review and the confidence report."""
    if confidence > (note.get("best_candidate") or {}).get("confidence", -1):
        note["best_candidate"] = {"corner_id": label, "confidence": round(confidence, 3),
                                  "assignment_method": method, "enrichment_pass": enrichment_pass, **evidence}


def lap_position_stage(n, turns, lm, settings, enrichment_pass):
    br = n["_bracket"]
    fraction = (n["_t"] - br["a_t"]) / (br["b_t"] - br["a_t"]) if br["b_t"] > br["a_t"] else 0.5
    if lm and lm.get("elapsed"):
        estimate, timing = time_to_pct(lm["elapsed"], br["a_pct"], br["b_pct"], fraction), "reference_lap"
    else:
        estimate, timing = br["a_pct"] + fraction * (br["b_pct"] - br["a_pct"]), "proportional"
    candidates = [(l, p) for l, p in turns if br["a_pct"] <= p <= br["b_pct"]]
    if not candidates:
        return None
    label, p = min(candidates, key=lambda c: abs(c[1] - estimate))
    index = [l for l, _ in turns].index(label)
    neighbours = [turns[j][1] for j in (index - 1, index + 1) if 0 <= j < len(turns)]
    half = min((abs(p - q) / 2 for q in neighbours), default=0.05) or 0.05
    closeness = 1 - 0.5 * min(abs(estimate - p) / half, 1.0)
    conf = derived(settings, "lap_position", br["anchor_confidence"], enrichment_pass, closeness)
    return label, conf, {"after": br["after"], "before": br["before"], "estimated_pct": round(estimate, 4),
                         "corner_pct": p, "timing": timing, "anchor_confidence": br["anchor_confidence"]}


# --- per video --------------------------------------------------------------------------------

def enrich(raw, config, settings):
    transcript = json.loads((tq.TRANSCRIPTS / f"{raw['video_id']}.json").read_text(encoding="utf-8"))
    segments = [(s.get("start", 0), s.get("text", "").replace("\n", " ")) for s in transcript]
    bounds = [start for start, _ in passages(transcript)] + [float("inf")]
    pack_path = GENERATED / "knowledge_packs" / f"{raw['track_id']}.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8")) if pack_path.exists() else {}
    turns, dropped_markers = clean_turns(pack)
    pct = dict(turns)
    aliases = alias_table(raw["track_id"], pack, config, [l for l, _ in turns])
    lm = landmarks(raw["track_id"], tuple(turns)) if turns else None

    notes = []
    for index, source in enumerate(raw["corners"]):
        seq = source.get("sequence", 0)
        start = bounds[seq] if seq < len(bounds) else 0
        end = bounds[seq + 1] if seq + 1 < len(bounds) else float("inf")
        where = locate(source, segments, start, end, settings["locate"])
        n = {f: source[f] for f in FIELDS if source.get(f)}
        n.update(note_id=f"{raw['video_id']}:{index}", text="; ".join(f"{f}: {source[f]}" for f in FIELDS if source.get(f)),
                 spoken_as=source.get("spoken_as", ""), passage_time=source.get("start_time"),
                 corner_id=None, status="unassigned", evidence={},
                 provenance={k: v for k, v in where.items() if k != "line"})
        if where["line"] is not None:
            line = where["line"]
            n["time"] = stamp(segments[line][0])
            n["snippet"] = " ".join(t for _, t in segments[line:line + settings["locate"]["window_lines"]])
            n["_line"], n["_t"] = line, segments[line][0]
        else:
            n["_t"] = None
        if source.get("label") in pct:  # explicit: unchanged
            assign(n, source["label"], 1.0, "explicit", {}, 0)
        notes.append(n)

    for n in notes:  # alias, pass 1
        if not n["corner_id"] and n["_t"] is not None and aliases:
            hit = alias_stage(n, segments, aliases, settings.get("alias_requires_spoken_reference", False))
            if hit:
                # The alias's own confidence, capped by the method's (calibrated) confidence
                conf = min(hit[1], settings["method_confidence"]["alias_match"])
                if conf >= settings["minimum_confidence"]:
                    assign(n, hit[0], conf, "alias_match", hit[2], 1)
                else:
                    candidate(n, hit[0], conf, "alias_match", hit[2], 1)

    gained = []
    for enrichment_pass in range(1, settings["max_passes"] + 1):
        for n in notes:
            if n["corner_id"]:
                n["_pct"] = pct[n["corner_id"]]
        found = brackets(notes, fixed_points(notes, segments))  # fixed points as the pass starts
        for n in notes:
            n["_bracket"] = found.get(id(n))
        placed = sequence_stage(notes, turns, lm, settings, enrichment_pass)
        for n in notes:
            if n["corner_id"] or not n["_bracket"]:
                continue
            hit = lap_position_stage(n, turns, lm, settings, enrichment_pass)
            if not hit:
                continue
            label, conf, evidence = hit
            if conf >= settings["minimum_confidence"]:
                assign(n, label, conf, "lap_position", evidence, enrichment_pass)
                placed += 1
            else:
                candidate(n, label, conf, "lap_position", evidence, enrichment_pass)
        gained.append(placed)
        if not placed:
            break

    for n in notes:
        if not n["corner_id"] and n.get("_bracket"):
            br = n["_bracket"]
            # Telemetry could decide between these corners later
            n["unresolved"] = {"after": br["after"], "before": br["before"],
                               "corners_between": [l for l, p in turns if br["a_pct"] < p < br["b_pct"]]}
        for key in [k for k in n if k.startswith("_")]:
            del n[key]
    return {
        "video_id": raw["video_id"], "track_id": raw["track_id"], "track_name": raw.get("track_name"),
        "title": raw.get("title"), "car": raw.get("car"), "car_hint": raw.get("car_hint"),
        "settings": {k: settings[k] for k in ("minimum_confidence", "max_passes", "confidence_decay_per_pass")},
        "telemetry_laps": lm["laps"] if lm else 0, "dropped_turn_markers": dropped_markers,
        "placed_per_pass": gained, "notes": notes,
    }


# --- analysis ---------------------------------------------------------------------------------

def counts(results):
    methods, passes = Counter(), Counter()
    for result in results:
        for n in result["notes"]:
            methods[n.get("assignment_method") or "unassigned"] += 1
            if n.get("assignment_method") not in (None, "explicit"):
                passes[n["enrichment_pass"]] += 1
    return methods, passes


def holdout(raws, config, settings, folds=3):
    """Hide every third explicit label in turn, enrich, and compare with what the speaker said.
    Returns [(true label, placed label or None, method)] for the hidden notes."""
    outcome = []
    for fold in range(folds):
        for raw in raws:
            hidden = copy.deepcopy(raw)
            positions = []
            for i, note in enumerate(hidden["corners"]):
                if note.get("label") and i % folds == fold:
                    note["label"] = None
                    positions.append(i)
            if not positions:
                continue
            result = enrich(hidden, config, settings)
            for i in positions:
                n = result["notes"][i]
                outcome.append((raw["corners"][i]["label"], n.get("corner_id"), n.get("assignment_method")))
    return outcome


BANDS = ((0.95, "0.95-1.00"), (0.90, "0.90-0.95"), (0.85, "0.85-0.90"), (0.80, "0.80-0.85"),
         (0.75, "0.75-0.80"), (0.70, "0.70-0.75"), (0.60, "0.60-0.70"), (0.50, "0.50-0.60"), (0.0, "below 0.50"))


def band(confidence):
    return next(name for low, name in BANDS if confidence >= low)


def histogram(results):
    """Accepted placements and rejected best candidates per confidence band."""
    accepted, rejected = Counter(), Counter()
    for result in results:
        for n in result["notes"]:
            if n.get("assignment_method") not in (None, "explicit"):
                accepted[band(n["confidence"])] += 1
            elif not n.get("corner_id") and n.get("best_candidate"):
                rejected[band(n["best_candidate"]["confidence"])] += 1
    return [{"band": name, "accepted": accepted[name], "rejected": rejected[name]} for _, name in BANDS
            if accepted[name] or rejected[name]]


def calibration(raws, config, settings):
    """Hidden explicit notes placed with any confidence down to 0.5: how often each band and
    method is right. A well-scored band is right about as often as its confidence says."""
    s = dict(settings, minimum_confidence=0.5)
    bands, methods = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for fold in range(3):
        for raw in raws:
            hidden = copy.deepcopy(raw)
            positions = [i for i, n in enumerate(hidden["corners"]) if n.get("label") and i % 3 == fold]
            for i in positions:
                hidden["corners"][i]["label"] = None
            if not positions:
                continue
            result = enrich(hidden, config, s)
            for i in positions:
                n = result["notes"][i]
                if n.get("corner_id"):
                    right = n["corner_id"] == raw["corners"][i]["label"]
                    for table, key in ((bands, band(n["confidence"])), (methods, n["assignment_method"])):
                        table[key][0] += 1
                        table[key][1] += right
    fmt = lambda table: {k: {"placed": v[0], "correct": v[1], "accuracy": round(v[1] / v[0], 2)}
                         for k, v in sorted(table.items(), reverse=True)}
    return {"by_band": fmt(bands), "by_method": fmt(methods)}


def calibrate(raws, config, settings):
    """Method confidences capped at their measured accuracy on hidden explicit notes."""
    measured = calibration(raws, config, settings)["by_method"]
    calibrated = copy.deepcopy(settings)
    applied = {}
    for method, v in measured.items():
        if method in calibrated["method_confidence"] and v["placed"] >= settings["calibration_min_samples"]:
            accuracy = round((v["correct"] + 1) / (v["placed"] + 2), 3)
            calibrated["method_confidence"][method] = min(settings["method_confidence"][method], accuracy)
            applied[method] = {"configured": settings["method_confidence"][method], "measured_accuracy": accuracy,
                               "placed": v["placed"], "correct": v["correct"],
                               "used": calibrated["method_confidence"][method]}
    return calibrated, applied


def ablation(raws, config, settings, uncalibrated):
    """Each enhancement added in turn, measured on the same notes."""
    first = {"strategies": ["whole_note"]}
    steps = [
        ("first rollout: plain location, 1 pass", uncalibrated, first, 1, False),
        ("+ provenance fixes (spelling, per field, context)", uncalibrated, {}, 1, False),
        ("+ multi-pass", uncalibrated, {}, settings["max_passes"], False),
        ("+ alias needs the note's own spoken reference", uncalibrated, {}, settings["max_passes"], True),
        ("+ calibrated method confidence", settings, {}, settings["max_passes"], True),
    ]
    rows = []
    for name, base, locate_change, passes, spoken in steps:
        s = copy.deepcopy(base)
        s["locate"].update(locate_change)
        s["max_passes"] = passes
        s["alias_requires_spoken_reference"] = spoken
        results = [enrich(raw, config, s) for raw in raws]
        methods, _ = counts(results)
        total = sum(methods.values())
        located = sum(1 for r in results for n in r["notes"] if n.get("time"))
        hidden = holdout(raws, config, s)
        placed = [(t, p) for t, p, _ in hidden if p]
        rows.append({"step": name, "notes_located": located, "notes": total,
                     "recovered": total - methods["explicit"] - methods["unassigned"],
                     "unassigned": methods["unassigned"],
                     "coverage_pct": round(100 * (total - methods["unassigned"]) / total, 1) if total else 0,
                     "holdout_placed": len(placed), "holdout_hidden": len(hidden),
                     "holdout_accuracy": round(sum(t == p for t, p in placed) / len(placed), 3) if placed else None})
        print(f"  {name:52} located {located}/{total}  recovered {rows[-1]['recovered']:3}  "
              f"coverage {rows[-1]['coverage_pct']}%  hidden re-placed {len(placed)}/{len(hidden)}"
              + (f" ({100 * rows[-1]['holdout_accuracy']:.0f}% right)" if placed else ""), flush=True)
    return rows


def confidence_analysis(raws, config, settings):
    rows = []
    for threshold in ANALYSIS_THRESHOLDS:
        s = dict(settings, minimum_confidence=threshold)
        methods, _ = counts([enrich(raw, config, s) for raw in raws])
        hidden = holdout(raws, config, s)
        placed = [(t, p, m) for t, p, m in hidden if p]
        correct = sum(1 for t, p, _ in placed if t == p)
        by_method = defaultdict(lambda: [0, 0])
        for t, p, m in placed:
            by_method[m][0] += 1
            by_method[m][1] += t == p
        rows.append({
            "threshold": threshold,
            "recovered": sum(methods[m] for m in METHODS if m != "explicit"),
            "still_unassigned": methods["unassigned"],
            "holdout_hidden": len(hidden), "holdout_placed": len(placed),
            "holdout_accuracy": round(correct / len(placed), 3) if placed else None,
            "holdout_by_method": {m: {"placed": v[0], "correct": v[1]} for m, v in sorted(by_method.items())},
        })
        print(f"  threshold {threshold:.2f}: recovered {rows[-1]['recovered']:3}   hidden explicit notes "
              f"re-placed {len(placed):3}/{len(hidden)}, correct {correct:3}"
              + (f" ({100 * correct / len(placed):.0f}%)" if placed else ""), flush=True)
    return rows


# --- main -------------------------------------------------------------------------------------

def _seconds(time_text):
    m = re.match(r"(\d+):(\d+)", time_text or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-confidence", "--threshold", type=float, dest="minimum_confidence")
    parser.add_argument("--max-passes", type=int, dest="max_passes")
    parser.add_argument("--decay", type=float, dest="confidence_decay_per_pass")
    parser.add_argument("--no-analysis", action="store_true")
    parser.add_argument("--no-calibrate", action="store_true")
    args = parser.parse_args()
    settings = load_settings({"minimum_confidence": args.minimum_confidence, "max_passes": args.max_passes,
                              "confidence_decay_per_pass": args.confidence_decay_per_pass})

    config = json.loads(ALIASES.read_text(encoding="utf-8")) if ALIASES.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    raws = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(RAW.glob("*.json"))]
    uncalibrated, applied = settings, {}
    if settings.get("calibrate") and not args.no_calibrate:
        settings, applied = calibrate(raws, config, uncalibrated)
        print("Method confidence calibrated on hidden explicit notes:")
        for method, v in applied.items():
            print(f"  {method:16} configured {v['configured']:.2f}, right {v['correct']}/{v['placed']} "
                  f"-> using {v['used']:.2f}")
        print()
    results = [enrich(raw, config, settings) for raw in raws]
    for result in results:
        (OUT / f"{result['video_id']}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                                         encoding="utf-8")

    methods, passes = counts(results)
    total = sum(methods.values())
    explicit = methods["explicit"]
    recovered = total - explicit - methods["unassigned"]
    unassigned_before = total - explicit
    bins = Counter()
    per_track = defaultdict(Counter)
    review, provenance, bad_markers = [], [], {}
    issues = Counter()
    for result in results:
        if result["dropped_turn_markers"]:
            bad_markers[result["track_id"]] = result["dropped_turn_markers"]
        for n in result["notes"]:
            method = n.get("assignment_method") or "unassigned"
            per_track[f"{result['track_id']} {result['track_name']}"][method] += 1
            if method not in ("explicit", "unassigned"):
                c = n["confidence"]
                bins["0.95-1.00" if c >= 0.95 else "0.90-0.95" if c >= 0.9 else "0.85-0.90" if c >= 0.85
                     else "0.80-0.85" if c >= 0.8 else "0.75-0.80" if c >= 0.75 else "below 0.75"] += 1
            if n["provenance"].get("issue"):
                issues[n["provenance"]["issue"]] += 1
                provenance.append({
                    "note_id": n["note_id"], "track": f"{result['track_id']} {result['track_name']}",
                    "video": f"https://www.youtube.com/watch?v={result['video_id']}",
                    "issue_type": n["provenance"]["issue"], "original_text": n["text"],
                    "recovery_possible": n["provenance"]["how"] is not None,
                    "recovered_at": n.get("time"), "located_by": n["provenance"]["how"],
                    "assignment": method,
                })
            if method != "explicit":
                candidate = n if method != "unassigned" else n.get("best_candidate") or {}
                review.append({
                    "track_id": result["track_id"], "track": result["track_name"],
                    "corner": candidate.get("corner_id") or "", "confidence": candidate.get("confidence") or "",
                    "assignment_method": method if method != "unassigned" else
                    f"unassigned (best: {candidate.get('assignment_method', 'none')})",
                    "enrichment_pass": candidate.get("enrichment_pass", ""),
                    "time": n.get("time", ""), "located_by": n["provenance"].get("how") or "not located",
                    "note": n["text"], "transcript_snippet": n.get("snippet", ""), "video_id": result["video_id"],
                    "source_video": f"https://www.youtube.com/watch?v={result['video_id']}&t={_seconds(n.get('time'))}s",
                })

    cumulative, running = [], explicit  # alias placements count in pass 1
    for p in sorted(passes):
        running += passes[p]
        cumulative.append({"pass": p, "placed": passes[p], "assigned_total": running,
                           "coverage_pct": round(100 * running / total, 1) if total else 0})
    report = {
        "videos_processed": len(results), "notes": total, "settings": {
            k: settings[k] for k in ("minimum_confidence", "max_passes", "confidence_decay_per_pass",
                                     "alias_requires_spoken_reference", "method_confidence")},
        "calibration": applied,
        "before": {"assigned": explicit, "unassigned": unassigned_before,
                   "coverage_pct": round(100 * explicit / total, 1) if total else 0},
        "after": {"assigned": explicit + recovered, "unassigned": methods["unassigned"],
                  "coverage_pct": round(100 * (explicit + recovered) / total, 1) if total else 0},
        "recovered": recovered,
        "recovered_pct_of_unassigned": round(100 * recovered / unassigned_before, 1) if unassigned_before else 0,
        "by_method": {m: methods[m] for m in METHODS + ("unassigned",)},
        "by_pass": cumulative,
        "confidence_distribution": dict(sorted(bins.items(), reverse=True)),
        "provenance_issues": dict(issues),
        "by_track": {t: dict(c) for t, c in sorted(per_track.items())},
        "turn_markers_dropped": bad_markers,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    PROVENANCE.write_text(json.dumps({
        "summary": {issue: {"notes": count, "recovered": sum(1 for p in provenance
                                                             if p["issue_type"] == issue and p["recovery_possible"])}
                    for issue, count in issues.items()},
        "notes": provenance}, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(REVIEW, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(review[0]) if review else ["track_id"])
        writer.writeheader()
        writer.writerows(sorted(review, key=lambda r: (r["track_id"], r["video_id"], r["time"])))

    print(f"Videos Processed: {len(results)}   notes: {total}   min confidence: {settings['minimum_confidence']}"
          f"   passes: {settings['max_passes']}   decay: {settings['confidence_decay_per_pass']}\n")
    print(f"Explicit Assignments:       {methods['explicit']}")
    print(f"Alias Assignments:          {methods['alias_match']}")
    print(f"Telemetry Assignments:      {methods['telemetry_match']}")
    print(f"Sequence Assignments:       {methods['sequence_match']}")
    print(f"Lap Position Assignments:   {methods['lap_position']}")
    print(f"Remaining Unassigned:       {methods['unassigned']}\n")
    for row in cumulative:
        print(f"  pass {row['pass']}: +{row['placed']}  (coverage {row['coverage_pct']}%)")
    print(f"\nCoverage: {report['before']['coverage_pct']}% -> {report['after']['coverage_pct']}% "
          f"({recovered} of {unassigned_before} unassigned notes recovered, {report['recovered_pct_of_unassigned']}%)")
    print(f"Provenance issues: {dict(issues)}")
    if bad_markers:
        print(f"Turn markers dropped (duplicate labels out of lap order): {bad_markers}")

    if not args.no_analysis:
        print("\nBefore/after per enhancement:")
        steps = ablation(raws, config, settings, uncalibrated)
        print("\nRecovery by threshold (hidden explicit notes show how often each threshold places correctly):")
        thresholds = confidence_analysis(raws, config, settings)
        hist = histogram(results)
        cal = calibration(raws, config, settings)
        print("\nConfidence histogram at the configured threshold (accepted / rejected best candidates):")
        for row in hist:
            print(f"  {row['band']:>10}: accepted {row['accepted']:3}   rejected {row['rejected']:3}")
        print("\nAccuracy on hidden explicit notes with the confidences in use (placed / correct):")
        for key, v in cal["by_band"].items():
            print(f"  {key:>10}: {v['placed']:3} placed, {v['correct']:3} correct ({100 * v['accuracy']:.0f}%)")
        for key, v in cal["by_method"].items():
            print(f"  {key:>16}: {v['placed']:3} placed, {v['correct']:3} correct ({100 * v['accuracy']:.0f}%)")
        ANALYSIS.write_text(json.dumps({"settings": report["settings"], "enhancements": steps,
                                        "thresholds": thresholds, "histogram": hist, "calibration": cal},
                                       indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
