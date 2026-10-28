"""Compare guide discovery now with a snapshot taken by run_guide_discovery, and validate it.

Usage:
    python -m src.pipelines.report_discovery_refresh                 against the oldest snapshot
    python -m src.pipelines.report_discovery_refresh --before <dir>  against a given snapshot

Writes generated/discovery_refresh_report.json and .md. A video is identified only by its
YouTube id. One video may be selected for several layouts of a venue; that is one video, one
queue item and one transcript, and is not a duplicate. Duplicates are the same id twice in one
layout's selection, or twice in the transcript queue.

Before the ledger existed (discovery version 2) only selections and a candidate count were
stored, so "new" means not previously selected for any layout and not in the transcript queue.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.pipelines.run_guide_discovery import CATALOG, LEDGER, MANIFEST, SNAPSHOTS, TRANSCRIPT_QUEUE
from src.shared.iracing_tracks import load_layouts
from src.shared.paths import GENERATED
from src.shared.transcript_queue import downloaded_ids

OUT = GENERATED / "discovery_refresh_report"
FOCUS_VENUES = ("Autódromo Hermanos Rodríguez", "Autódromo José Carlos Pace")


def read_dir(folder):
    out, broken = {}, []
    for path in sorted(Path(folder).glob("*.json")) if Path(folder).exists() else []:
        try:
            out[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as ex:
            broken.append(f"{path.name}: {ex}")
    return out, broken


def selections(catalogs):
    """{track_id: [video ids in selection order]}."""
    return {int(d["track_id"]): [v["video_id"] for vs in d.get("selected_guides", {}).values() for v in vs]
            for d in catalogs.values()}


def state(folder):
    catalogs, broken = read_dir(Path(folder) / CATALOG.name)
    ledgers, broken_ledgers = read_dir(Path(folder) / LEDGER.name)
    queue_path = Path(folder) / TRANSCRIPT_QUEUE.name
    queue = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.exists() else []
    manifest_path = Path(folder) / MANIFEST.name
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    return {"catalogs": catalogs, "ledgers": {int(k): v.get("candidates", {}) for k, v in ledgers.items()},
            "queue": queue, "manifest": manifest, "broken": broken + broken_ledgers}


def totals(s):
    sel = selections(s["catalogs"])
    ledger_pairs = {(t, vid) for t, c in s["ledgers"].items() for vid in c}
    accepted = {(t, vid) for t, c in s["ledgers"].items() for vid, r in c.items() if not r.get("reason")}
    selected_pairs = {(t, vid) for t, ids in sel.items() for vid in ids}
    unique = {vid for _, vid in ledger_pairs | selected_pairs}
    return {
        "layouts": len(sel),
        "layouts_with_guides": sum(1 for ids in sel.values() if ids),
        "unique_videos": len(unique),
        "candidates": sum(len(c) for c in s["ledgers"].values()) if s["ledgers"]
        else sum(d.get("candidates_seen", 0) for d in s["catalogs"].values()),
        "candidates_recorded": bool(s["ledgers"]),
        "unique_candidates": len({vid for _, vid in ledger_pairs}) if s["ledgers"] else None,
        "accepted": len(accepted | selected_pairs) if s["ledgers"] else None,
        "unique_accepted": len({vid for _, vid in accepted | selected_pairs}) if s["ledgers"] else None,
        "selected": len(selected_pairs),
        "unique_selected": len({vid for _, vid in selected_pairs}),
    }


def kinds(record):
    return {source.get("kind") for source in record.get("found_by", [])}


def delta(before, after, layouts):
    sel_before, sel_after = selections(before["catalogs"]), selections(after["catalogs"])
    known = ({vid for ids in sel_before.values() for vid in ids}
             | {vid for c in before["ledgers"].values() for vid in c}
             | {item["video_id"] for item in before["queue"]})
    before_pairs = ({(t, vid) for t, ids in sel_before.items() for vid in ids}
                    | {(t, vid) for t, c in before["ledgers"].items() for vid in c})
    out = Counter()
    new_ids, alias_ids, repair_ids = set(), set(), set()
    for t, candidates in after["ledgers"].items():
        for vid, r in candidates.items():
            if (t, vid) in before_pairs:
                continue
            k = kinds(r)
            accepted = not r.get("reason")
            out["new_layout_candidates"] += 1
            out["new_layout_accepted"] += accepted
            if vid not in known:
                new_ids.add(vid)
            # Found by an alias search and by no search on the official name
            if "alias" in k and not k & {"name", "repaired"}:
                out["alias_candidates"] += 1
                out["alias_accepted"] += accepted
                out["alias_selected"] += r.get("status") == "selected"
                alias_ids.add(vid)
            # Found by a search on a name the metadata stored garbled, by no alias search
            if "repaired" in k and "alias" not in k:
                out["repair_candidates"] += 1
                out["repair_accepted"] += accepted
                out["repair_selected"] += r.get("status") == "selected"
                repair_ids.add(vid)
    new_selected = {(t, vid) for t, ids in sel_after.items() for vid in ids} - \
                   {(t, vid) for t, ids in sel_before.items() for vid in ids}
    accepted_new_ids = {vid for c in after["ledgers"].values() for vid, r in c.items()
                        if vid in new_ids and not r.get("reason")}
    return {
        "new_unique_videos": len(new_ids),
        "new_unique_accepted": len(accepted_new_ids),
        "new_layout_candidates": out["new_layout_candidates"],
        "new_layout_accepted": out["new_layout_accepted"],
        "new_selected": len(new_selected),
        "new_selected_new_videos": sum(1 for _, vid in new_selected if vid not in known),
        "new_selected_known_videos": sum(1 for _, vid in new_selected if vid in known),
        "alias_candidates": out["alias_candidates"], "alias_accepted": out["alias_accepted"],
        "alias_selected": out["alias_selected"], "alias_unique_videos": len(alias_ids),
        "repair_candidates": out["repair_candidates"], "repair_accepted": out["repair_accepted"],
        "repair_selected": out["repair_selected"], "repair_unique_videos": len(repair_ids),
    }


def validate(before, after, layouts):
    sel_before, sel_after = selections(before["catalogs"]), selections(after["catalogs"])
    issues = {"broken_files": after["broken"], "catalog_problems": [], "duplicate_in_selection": [],
              "duplicate_in_queue": [], "lost_selections": [], "manifest_mismatch": [],
              "unlinked_transcripts": [], "lost_queue_items": [], "leftover_tmp_files": []}
    for stem, d in after["catalogs"].items():
        if str(d.get("track_id")) != stem or not isinstance(d.get("selected_guides"), dict) \
                or "layout" not in d or not all(v.get("video_id") for vs in d["selected_guides"].values() for v in vs):
            issues["catalog_problems"].append(stem)
    for t, ids in sel_after.items():
        for vid, n in Counter(ids).items():
            if n > 1:
                issues["duplicate_in_selection"].append(f"{t}:{vid}")
    for vid, n in Counter(item["video_id"] for item in after["queue"]).items():
        if n > 1:
            issues["duplicate_in_queue"].append(vid)
    for t, ids in sel_before.items():
        missing = set(ids) - set(sel_after.get(t, []))
        issues["lost_selections"] += [f"{t}:{vid}" for vid in sorted(missing)]
    manifest = {m["track_id"]: m for m in after["manifest"]}
    for t, ids in sel_after.items():
        listed = (manifest.get(t, {}).get("youtube") or {}).get("video_ids")
        if t in manifest and sorted(listed or []) != sorted(set(ids)):
            issues["manifest_mismatch"].append(t)
    selected_now = {vid for ids in sel_after.values() for vid in ids}
    queued_now = {item["video_id"]: item for item in after["queue"]}
    was_linked = {vid for ids in sel_before.values() for vid in ids}
    for vid in sorted(downloaded_ids() & was_linked):
        if vid not in selected_now:
            issues["unlinked_transcripts"].append(vid)
    for item in before["queue"]:
        if item["video_id"] not in queued_now and item["video_id"] not in selected_now:
            issues["lost_queue_items"].append(item["video_id"])
    issues["leftover_tmp_files"] = [p.name for folder in (CATALOG, LEDGER) if folder.exists()
                                    for p in folder.glob("*.tmp")]
    kept_rejected = sorted({vid for d in after["catalogs"].values()
                            for vid in (d.get("diagnostics") or {}).get("kept_despite_rejection", [])})
    return issues, kept_rejected


def focus(before, after, layouts):
    rows = []
    sel_before, sel_after = selections(before["catalogs"]), selections(after["catalogs"])
    for t, info in sorted(layouts.items()):
        if info["venue"] not in FOCUS_VENUES:
            continue
        ledger = after["ledgers"].get(t, {})
        diag = (after["catalogs"].get(str(t)) or {}).get("diagnostics") or {}
        rows.append({
            "track_id": t, "name": info["name"],
            "candidates_before": (before["catalogs"].get(str(t)) or {}).get("candidates_seen", 0),
            "selected_before": len(sel_before.get(t, [])),
            "candidates_after": len(ledger),
            "accepted_after": sum(1 for r in ledger.values() if not r.get("reason")),
            "selected_after": len(sel_after.get(t, [])),
            "queries": f"{diag.get('queries_run', 0)}/{diag.get('queries_planned', 0)}",
            "rejection_reasons": diag.get("rejection_reasons", {}),
        })
    return rows


def markdown(report):
    b, a, d, v = report["before"], report["after"], report["delta"], report["validation"]

    def cell(x):
        return "not recorded" if x is None else f"{x:,}" if isinstance(x, int) else str(x)
    lines = [f"# Guide discovery refresh", "", f"Before: snapshot `{report['snapshot']}`. After: current data.", "",
             "| Metric | Before | After |", "|---|---:|---:|"]
    for key, label in (("layouts_with_guides", "Layouts with guides"), ("unique_videos", "Unique videos"),
                       ("candidates", "Candidates (per layout)"), ("unique_candidates", "Unique candidate videos"),
                       ("accepted", "Accepted guides (per layout)"), ("unique_accepted", "Unique accepted videos"),
                       ("selected", "Selected guides (per layout)"), ("unique_selected", "Unique selected videos")):
        lines.append(f"| {label} | {cell(b[key])} | {cell(a[key])} |")
    lines += ["", "| Discovery delta | Count |", "|---|---:|"]
    for key, label in (("new_unique_videos", "New videos (never seen before)"),
                       ("new_layout_candidates", "New candidates (per layout)"),
                       ("new_unique_accepted", "New accepted videos"),
                       ("new_layout_accepted", "New accepted guides (per layout)"),
                       ("new_selected", "New selections (per layout)"),
                       ("new_selected_new_videos", "… of videos new to the system"),
                       ("new_selected_known_videos", "… of videos already known (linked to another layout)"),
                       ("alias_candidates", "Candidates found only via aliases"),
                       ("alias_accepted", "… accepted"), ("alias_selected", "… selected"),
                       ("repair_candidates", "Candidates found due to metadata repair"),
                       ("repair_accepted", "… accepted"), ("repair_selected", "… selected")):
        lines.append(f"| {label} | {d[key]:,} |")
    lines += ["", "## Mexico and Interlagos", "", "| Layout | Before (cand / sel) | After (cand / acc / sel) | Queries |",
              "|---|---:|---:|---:|"]
    for r in report["focus"]:
        lines.append(f"| {r['track_id']} {r['name']} | {r['candidates_before']} / {r['selected_before']} | "
                     f"{r['candidates_after']} / {r['accepted_after']} / {r['selected_after']} | {r['queries']} |")
    lines += ["", "## Validation", "", "| Check | Result |", "|---|---|"]
    for key, label in (("broken_files", "Unreadable catalog or ledger files"), ("catalog_problems", "Catalog structure problems"),
                       ("duplicate_in_selection", "Duplicate video ids within a layout's selection"),
                       ("duplicate_in_queue", "Duplicate video ids in the transcript queue"),
                       ("lost_selections", "Previous selections no longer selected"),
                       ("manifest_mismatch", "Manifest out of step with catalog"),
                       ("unlinked_transcripts", "Downloaded transcripts no longer linked to a layout"),
                       ("lost_queue_items", "Transcript queue items lost"), ("leftover_tmp_files", "Half-written files")):
        items = v[key]
        lines.append(f"| {label} | {'OK (0)' if not items else f'**{len(items)}**: ' + ', '.join(map(str, items[:10]))} |")
    lines.append(f"| Previous selections the v3 rules would reject (kept) | {len(report['kept_despite_rejection'])} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    snapshot = args.before or min(SNAPSHOTS.iterdir())
    layouts = load_layouts()
    before, after = state(snapshot), state(GENERATED)
    issues, kept_rejected = validate(before, after, layouts)
    report = {"snapshot": str(snapshot), "before": totals(before), "after": totals(after),
              "delta": delta(before, after, layouts), "validation": issues,
              "kept_despite_rejection": kept_rejected, "focus": focus(before, after, layouts)}
    OUT.with_suffix(".json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    text = markdown(report)
    OUT.with_suffix(".md").write_text(text, encoding="utf-8")
    print(text)
    print(f"written: {OUT.with_suffix('.md')}")
    return 0 if not any(issues.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
