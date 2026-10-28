"""Find up to TARGET YouTube guide videos per track layout and store them in the guide catalog.

For each layout it searches YouTube with the official iRacing track name and the venue's
aliases (config/track_aliases.json), scores every video it finds, and writes the selection to
generated/guide_catalog/<track_id>.json (the input of build_transcript_queue). The
acquisition manifest is updated to match.

Names and titles are compared after normalising case, accents, punctuation and spacing
(src/shared/track_names.py), and the venue match is a confidence, not an exact match: the
full name or an alias counts fully, some of the venue's distinctive words count partly.

A video is identified only by its YouTube id. Refresh rules, per layout:
    previously selected  kept selected (its transcript stays linked); metadata and score updated
    previously seen      re-evaluated with the current rules (generated/guide_candidates/<id>.json
                         remembers every candidate, its verdict and the queries that found it)
    new                  scored normally; fills the selection up to TARGET
Before searching, the catalog, candidate ledger, manifest and transcript queue are copied to
generated/discovery_snapshots/<timestamp>/ (report_discovery_refresh compares against it).

Usage:
    python -m src.pipelines.run_guide_discovery              layouts not yet searched by this version
    python -m src.pipelines.run_guide_discovery --limit 20   the next 20 of them
    python -m src.pipelines.run_guide_discovery --track 8    one layout (always re-searched)
    python -m src.pipelines.run_guide_discovery --all        re-search every layout
    add --debug to write every query, candidate, score and rejection reason to
    generated/guide_discovery_debug/<track_id>.json

Layouts with aliases or repaired names go first, then those with the fewest guides. Layouts
already searched by this version are skipped unless --track or --all is given, so the script
can be stopped and restarted. Then run build_transcript_queue.
"""
import argparse
import json
import os
import random
import shutil
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED
from src.shared.track_names import aliases, contains_phrase, fold, normalize, squash

TARGET = 10
RESULTS_PER_QUERY = 20
DISCOVERY_VERSION = 3
MIN_SECONDS, MAX_SECONDS = 90, 40 * 60
MIN_SCORE = 60
# Below this the title is not taken to be about the venue
MIN_VENUE_CONFIDENCE = 0.5

CATALOG = GENERATED / "guide_catalog"
LEDGER = GENERATED / "guide_candidates"
DEBUG_DIR = GENERATED / "guide_discovery_debug"
SNAPSHOTS = GENERATED / "discovery_snapshots"
MANIFEST = GENERATED / "track_acquisition_manifest.json"
TRANSCRIPT_QUEUE = GENERATED / "transcript_queue.json"

# Words that do not identify a venue on their own
GENERIC = {
    "raceway", "speedway", "circuit", "international", "motor", "motorsport", "motorsports", "park",
    "street", "the", "of", "de", "del", "di", "la", "le", "grand", "prix", "gp", "course", "road",
    "track", "racing", "race", "full", "short", "long", "oval", "club", "national", "west", "east",
    "north", "south", "fairgrounds", "county", "center", "centre", "and", "at", "complex", "ring",
    "autodromo", "autodrome", "circuito", "dirt", "legends", "inner", "outer", "loop", "night",
}
# A title must contain one of these: videos that talk through the lap. Hotlaps and onboards
# without commentary are not wanted. verify_lap_guide_transcripts checks the transcript later.
LAP_GUIDE_WORDS = ("track guide", "lap guide", "circuit guide", "guide", "tutorial", "walkthrough",
                   "walk through", "breakdown", "how to drive", "learn to drive", "corner by corner",
                   "turn by turn", "track walk", "lap explained", "track explained", "coaching lap")
STRONG_WORDS = ("track guide", "lap guide", "circuit guide", "walkthrough", "walk through",
                "corner by corner", "turn by turn", "how to drive", "learn to drive")
NOT_A_LAP_GUIDE = ("setup guide", "buyer", "buying guide", "beginner's guide to iracing",
                   "beginners guide to iracing", "pedal", "wheel review", "rig ", "settings guide",
                   "ffb", "license", "series guide", "season guide")
JUNK_WORDS = ("crash", "highlights", "reaction", "funny", "fails", "#shorts", "compilation", "wreck",
              "full race", "live stream", "livestream", "championship race", "race recap")
SILENT_LAP_WORDS = ("hotlap", "hot lap", "telemetry", "onboard")


def has(text, phrases):
    """Whether normalized text contains any phrase. Phrases match inside words ('guide' in
    'guides') unless written with a leading or trailing space, which then requires a word edge."""
    padded = f" {text} "
    for phrase in phrases:
        core = normalize(phrase)
        if core and f"{' ' if phrase[:1] == ' ' else ''}{core}{' ' if phrase[-1:] == ' ' else ''}" in padded:
            return True
    return False


def venue_profile(info):
    """Everything a title can name the venue by."""
    strong, weak = aliases(info["venue"])
    names = list(dict.fromkeys(normalize(n) for n in [info["venue"], *strong] if normalize(n)))
    return {
        "names": names,
        "joined": [n.replace(" ", "") for n in names if len(n.replace(" ", "")) >= 6],
        "distinctive": [w for w in normalize(info["venue"]).split() if w not in GENERIC and len(w) >= 3],
        "slug": [w for w in (info["layout"] or "").split("-")[1:2]
                 if w and not w.isdigit() and w not in GENERIC],
        "weak": [normalize(w) for w in weak if normalize(w)],
    }


def venue_match(title, profile):
    """(confidence 0..1, what matched) for how sure we are that a title is about the venue."""
    t = normalize(title)
    joined = t.replace(" ", "")
    tokens = t.split()
    for name in profile["names"]:
        if contains_phrase(t, name):
            return 1.0, f"name '{name}'"
    for name in profile["joined"]:
        if name in joined:
            return 0.9, f"name '{name}'"
    best = (0.0, None)
    words = profile["distinctive"]
    if words:
        # Inside a joined word too ('Autoclub'), except 3-letter words, which must stand alone
        exact = [w for w in words if w in tokens or (len(w) >= 4 and w in joined)]
        # Misspellings such as 'Hermanez Rodriguez'
        fuzzy = [w for w in words if w not in exact and len(w) >= 7 and any(
            SequenceMatcher(None, w, tok).ratio() >= 0.75 for tok in tokens if len(tok) >= 5)]
        if exact or fuzzy:
            share = (len(exact) + 0.5 * len(fuzzy)) / len(words)
            best = max(best, (round(0.5 + 0.4 * share, 2), f"words {exact + [f'~{w}' for w in fuzzy]}"))
    for slug in profile["slug"]:
        if slug in tokens or (len(slug) >= 4 and slug in joined):
            best = max(best, (0.8, f"layout '{slug}'"))
    for weak in profile["weak"]:
        if contains_phrase(t, weak):
            best = max(best, (0.5, f"weak alias '{weak}'"))
    return best


def planned_queries(info):
    """[(query, kind)]. kind is 'alias', 'repaired' (the official name, which the metadata stored
    double-encoded, so earlier versions searched it garbled) or 'name'."""
    venue, name = fold(info["venue"]), fold(info["name"])
    strong, _ = aliases(info["venue"])
    name_kind = "repaired" if info.get("name_repaired") else "name"
    out = [(f"iracing {name} track guide", name_kind)]
    if name != venue:
        out.append((f"iracing {venue} track guide", name_kind))
    # Aliases early: for venues known by another name they find most of the guides
    out += [(f"iracing {fold(alias)} track guide", "alias") for alias in strong]
    out += [(q, name_kind) for q in (f"iracing {venue} lap guide", f"iracing {venue} guide",
                                     f"{name} track guide", f"how to drive {venue} iracing",
                                     f"{venue} track guide sim racing")]
    unique = {}
    for query, kind in out:
        unique.setdefault(normalize(query), (" ".join(query.split()), kind))
    return list(unique.values())


def queries(info):
    return [query for query, _ in planned_queries(info)]


def judge(video, info, profile, vehicles):
    """Score one candidate: {"score", "car", "venue_confidence", "venue_match", "reason"}.
    reason is None when the video is accepted, else why it was rejected."""
    title = video.get("title") or ""
    t = normalize(title)
    text = normalize(f"{title} {video.get('description') or ''}")
    confidence, matched = venue_match(title, profile)
    verdict = {"score": None, "car": None, "venue_confidence": confidence, "venue_match": matched,
               "reason": None}
    # The venue must be in the title: descriptions often list other tracks
    duration = video.get("duration")
    if confidence < MIN_VENUE_CONFIDENCE:
        verdict["reason"] = "venue not in title"
    elif duration and not MIN_SECONDS <= duration <= MAX_SECONDS:
        verdict["reason"] = "too short" if duration < MIN_SECONDS else "too long"
    elif video.get("live_status") in ("is_live", "is_upcoming", "was_live"):
        verdict["reason"] = "live stream"
    elif not has(t, LAP_GUIDE_WORDS):
        verdict["reason"] = "no guide words in title"
    elif has(t, NOT_A_LAP_GUIDE):
        verdict["reason"] = "setup or hardware video"
    if verdict["reason"]:
        return verdict

    # 60..100 for the venue match, so a full name match scores as the old exact match did
    points = 60 + round(40 * confidence)
    points += 30 if has(t, STRONG_WORDS) else 0
    points += 80 if "iracing" in text.replace(" ", "") else 0
    config_words = [w for w in normalize(info["config"]).split() if w not in GENERIC]
    points += 30 if info["config"] and all(w in text for w in config_words) else 0
    points -= 150 if has(text, JUNK_WORDS) else 0
    # "Track Guide (Hotlap + Telemetry)" is usually a silent lap: keep only when nothing better
    points -= 70 if has(t, SILENT_LAP_WORDS) else 0
    raw = fold(f"{title} {video.get('description') or ''}").lower()
    car = next((canonical for alias, canonical in vehicles.items() if alias in raw), None)
    points += 20 if car else 0
    verdict.update(score=points, car=car)
    if points < MIN_SCORE:
        verdict["reason"] = f"score below {MIN_SCORE}"
    return verdict


def evaluate(entries, info, profile, vehicles, pinned=()):
    """{video_id: verdict} for every candidate. A re-upload under a title already accepted is
    rejected as a duplicate; a previously selected copy wins, else the better-scored one."""
    verdicts = {entry["id"]: judge(entry, info, profile, vehicles) for entry in entries}
    titles = set()
    for entry in sorted(entries, key=lambda e: (e["id"] not in pinned, -(verdicts[e["id"]]["score"] or 0))):
        verdict = verdicts[entry["id"]]
        if verdict["reason"]:
            continue
        key = squash(entry.get("title") or "")
        if key in titles:
            verdict["reason"] = "duplicate title"
        titles.add(key)
    return verdicts


def guide(entry, verdict, car):
    return {
        "video_id": entry["id"],
        "title": entry.get("title") or "",
        "description": (entry.get("description") or "")[:300],
        "channel": entry.get("channel"),
        "duration": entry.get("duration"),
        "video_type": "lap_walkthrough",
        "car": car,
        "quality_score": verdict["score"],
        "venue_confidence": verdict["venue_confidence"],
    }


def select(entries, verdicts, pinned):
    """Previously selected videos stay; the best other accepted ones fill up to TARGET."""
    by_id = {e["id"]: e for e in entries}
    chosen = [guide(by_id[vid], verdicts[vid], car) for vid, car in pinned.items() if vid in by_id]
    others = sorted((e for e in entries if e["id"] not in pinned and not verdicts[e["id"]]["reason"]),
                    key=lambda e: -verdicts[e["id"]]["score"])
    chosen += [guide(e, verdicts[e["id"]], verdicts[e["id"]]["car"] or "general")
               for e in others[:max(0, TARGET - len(chosen))]]
    chosen.sort(key=lambda v: -(v["quality_score"] or 0))
    return chosen


def search(ydl, query, cache):
    """(entries, error message or None, from cache). Sibling layouts share most queries."""
    if query in cache:
        return cache[query], None, True
    try:
        result = ydl.extract_info(f"ytsearch{RESULTS_PER_QUERY}:{query}", download=False)
    except Exception as ex:
        error = str(ex).splitlines()[0][:120]
        print("  search failed:", query, "-", error)
        return [], error, False
    entries = [e for e in (result or {}).get("entries") or [] if e and e.get("id")]
    cache[query] = entries
    return entries, None, False


def merge(old, new):
    """Fresh search metadata over stored metadata, keeping stored values the search lacks."""
    out = dict(old)
    out.update({k: v for k, v in new.items() if v not in (None, "")})
    return out


def discover(ydl, info, vehicles, previous, ledger, cache=None):
    """(selected guides, candidate ledger, diagnostics, debug detail).

    previous: the catalog's selected guides; ledger: {video_id: record} from earlier runs."""
    cache = {} if cache is None else cache
    profile = venue_profile(info)
    planned = planned_queries(info)
    now = datetime.now(timezone.utc).isoformat()
    pinned = {v["video_id"]: v.get("car") or "general" for v in previous}
    found, found_by = {}, {}
    # Every video seen before competes again under the current rules
    for vid, record in ledger.items():
        found[vid] = {"id": vid, **{k: record.get(k) for k in ("title", "description", "channel", "duration")}}
        found_by[vid] = list(record.get("found_by", []))
    for video in previous:
        found[video["video_id"]] = merge(found.get(video["video_id"], {"id": video["video_id"]}),
                                         {k: video.get(k) for k in ("title", "description", "channel", "duration")})
        found_by.setdefault(video["video_id"], [])
    known = set(found)

    query_log = []
    alias_queries_left = sum(1 for _, kind in planned if kind == "alias")
    for query, kind in planned:
        entries, error, cached = search(ydl, query, cache)
        new = 0
        for entry in entries:
            new += entry["id"] not in found
            found[entry["id"]] = merge(found.get(entry["id"], {}), entry)
            sources = found_by.setdefault(entry["id"], [])
            if not any(s["query"] == query for s in sources):
                sources.append({"query": query, "kind": kind})
        query_log.append({"query": query, "kind": kind, "results": len(entries), "new": new,
                          "error": error, "cached": cached, "video_ids": [e["id"] for e in entries]})
        alias_queries_left -= kind == "alias"
        if not cached:
            time.sleep(random.uniform(1.0, 2.5))
        # Always run alias queries: they are how venues known by another name get covered
        if alias_queries_left:
            continue
        verdicts = evaluate(list(found.values()), info, profile, vehicles, pinned)
        selected = select(list(found.values()), verdicts, pinned)
        if len(selected) >= TARGET and (selected[TARGET - 1]["quality_score"] or 0) >= 180:
            break

    entries = list(found.values())
    verdicts = evaluate(entries, info, profile, vehicles, pinned)
    selected = select(entries, verdicts, pinned)
    chosen = {v["video_id"] for v in selected}

    records = {}
    for entry in entries:
        vid, verdict = entry["id"], verdicts[entry["id"]]
        status = "selected" if vid in chosen else "rejected" if verdict["reason"] else "accepted"
        records[vid] = {
            "video_id": vid, "title": entry.get("title") or "", "channel": entry.get("channel"),
            "duration": entry.get("duration"), "description": (entry.get("description") or "")[:300],
            "status": status, "reason": verdict["reason"], "score": verdict["score"],
            "venue_confidence": verdict["venue_confidence"], "venue_match": verdict["venue_match"],
            "car": verdict["car"], "previously_selected": vid in pinned,
            "found_by": found_by.get(vid, []),
            "first_seen": ledger.get(vid, {}).get("first_seen") or now, "last_evaluated": now,
        }

    reasons = Counter(r["reason"] for r in records.values() if r["reason"] and r["status"] != "selected")
    diagnostics = {
        "queries_planned": len(planned),
        "queries_run": len(query_log),
        "queries_cached": sum(1 for q in query_log if q["cached"]),
        "search_failures": sum(1 for q in query_log if q["error"]),
        "candidates": len(records),
        "new_candidates": len(set(records) - known),
        "accepted": sum(1 for r in records.values() if not r["reason"]),
        "selected": len(selected),
        "kept_previous": len(pinned.keys() & chosen),
        # Kept because they were selected before, although the current rules reject them
        "kept_despite_rejection": sorted(vid for vid in pinned if vid in chosen and verdicts[vid]["reason"]),
        "new_selected": len(chosen - set(pinned)),
        "rejected": sum(reasons.values()),
        "rejection_reasons": dict(reasons.most_common()),
    }
    ordered = sorted(records.values(), key=lambda r: ({"selected": 0, "accepted": 1}.get(r["status"], 2),
                                                      -(r["score"] or 0), -r["venue_confidence"]))
    debug = {"venue_profile": profile, "queries": query_log, "candidates": ordered}
    return selected, records, diagnostics, debug


def summary(diagnostics):
    d = diagnostics
    reasons = ", ".join(f"{reason} {n}" for reason, n in d["rejection_reasons"].items()) or "none"
    extra = f", {d['search_failures']} failed" if d["search_failures"] else ""
    extra += f", {d['queries_cached']} cached" if d["queries_cached"] else ""
    return (f"{d['selected']} guides ({d['kept_previous']} kept, {d['new_selected']} new) from "
            f"{d['candidates']} candidates ({d['new_candidates']} new; queries {d['queries_run']}/"
            f"{d['queries_planned']}{extra}; accepted {d['accepted']}; rejected {d['rejected']}: {reasons})")


def write_json(path, data, **kwargs):
    """Write through a temp file so readers (build_transcript_queue) never see half a file."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, **kwargs), encoding="utf-8")
    for attempt in range(10):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: another process has the file open for a moment
            time.sleep(0.2 * (attempt + 1))
    os.replace(tmp, path)


def save(track_id, info, guides, records, diagnostics):
    selected = {}
    for video in guides:
        selected.setdefault(video["car"], []).append(video)
    now = datetime.now(timezone.utc).isoformat()
    LEDGER.mkdir(parents=True, exist_ok=True)
    write_json(LEDGER / f"{track_id}.json", {
        "track_id": track_id, "name": info["name"], "discovery_version": DISCOVERY_VERSION,
        "updated_at": now, "candidates": records,
    }, ensure_ascii=False)
    write_json(CATALOG / f"{track_id}.json", {
        "track_id": track_id, "layout": info["layout"] or f"{track_id}", "name": info["name"],
        "discovery_version": DISCOVERY_VERSION, "searched_at": now,
        "candidates_seen": diagnostics["candidates"], "diagnostics": diagnostics,
        "selected_guides": selected,
    }, ensure_ascii=False)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for track in manifest:
        if track["track_id"] == track_id:
            youtube = track.setdefault("youtube", {})
            youtube["selected_guides"] = selected
            youtube["video_ids"] = sorted(v["video_id"] for v in guides)
            youtube["videos_found"] = len(guides)
            track["state"] = "guides_catalogued"
            track.setdefault("knowledge", {})["transcript_pending"] = True
            break
    write_json(MANIFEST, manifest)


def save_debug(track_id, info, diagnostics, debug):
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    path = DEBUG_DIR / f"{track_id}.json"
    write_json(path, {
        "track_id": track_id, "name": info["name"], "searched_at": datetime.now(timezone.utc).isoformat(),
        "diagnostics": diagnostics, **debug,
    }, ensure_ascii=False)
    return path


def snapshot():
    """Copy every piece of discovery state before changing it."""
    target = SNAPSHOTS / datetime.now().strftime("%Y%m%d-%H%M%S")
    target.mkdir(parents=True)
    for folder in (CATALOG, LEDGER):
        if folder.exists():
            shutil.copytree(folder, target / folder.name, ignore=shutil.ignore_patterns("*.tmp"))
    for file in (MANIFEST, TRANSCRIPT_QUEUE):
        if file.exists():
            shutil.copy2(file, target / file.name)
    return target


def previous_guides(track_id):
    """(selected guides, discovery version) from the catalog."""
    path = CATALOG / f"{track_id}.json"
    if not path.exists():
        return [], 0
    data = json.loads(path.read_text(encoding="utf-8"))
    guides = [dict(v, car=car) for car, videos in data.get("selected_guides", {}).items() for v in videos]
    return guides, data.get("discovery_version", 1)


def previous_ledger(track_id):
    path = LEDGER / f"{track_id}.json"
    return json.loads(path.read_text(encoding="utf-8")).get("candidates", {}) if path.exists() else {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--debug", action="store_true",
                        help="write queries, candidates, scores and rejection reasons per layout")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import yt_dlp
    from src.shared.ytdlp_config import YT_DLP_OPTIONS

    CATALOG.mkdir(parents=True, exist_ok=True)
    layouts = load_layouts()
    manifest_ids = [t["track_id"] for t in json.loads(MANIFEST.read_text(encoding="utf-8"))]
    vehicles = json.loads((GENERATED / "vehicle_lookup.json").read_text(encoding="utf-8"))

    todo = []
    for track_id in ([args.track] if args.track else manifest_ids):
        if track_id not in layouts:
            print(f"{track_id}: not in iRacing track metadata, skipped")
            continue
        previous, version = previous_guides(track_id)
        if args.track or args.all or version < DISCOVERY_VERSION:
            todo.append((track_id, previous))

    def priority(item):
        info = layouts[item[0]]
        return (0 if aliases(info["venue"])[0] else 1 if info["name_repaired"] else 2, len(item[1]))
    todo.sort(key=priority)
    if args.limit:
        todo = todo[:args.limit]
    print(f"layouts to search: {len(todo)}")
    if not todo:
        return
    print(f"snapshot: {snapshot()}", flush=True)

    opts = dict(YT_DLP_OPTIONS)
    opts.update({"quiet": True, "extract_flat": True, "socket_timeout": 15, "extractor_retries": 1})
    cache = {}
    with yt_dlp.YoutubeDL(opts) as ydl:
        for n, (track_id, previous) in enumerate(todo, 1):
            info = layouts[track_id]
            guides, records, diagnostics, debug = discover(ydl, info, vehicles, previous,
                                                           previous_ledger(track_id), cache)
            save(track_id, info, guides, records, diagnostics)
            print(f"[{n}/{len(todo)}] {track_id} {info['name']}: {summary(diagnostics)}", flush=True)
            if args.debug:
                print(f"  debug: {save_debug(track_id, info, diagnostics, debug)}", flush=True)


if __name__ == "__main__":
    main()
