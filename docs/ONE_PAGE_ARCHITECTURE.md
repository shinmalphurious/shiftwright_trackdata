# One-Page Architecture

`[A]` active · `[D]` dead/orphaned · `[X]` experimental/archived · `★` required to rebuild current `generated/` data

```text
┌─ $SHIFTWRIGHT_DATA_ROOT (shared) ────┐   ┌─ ARCHIVED (not required at runtime, kept for history) ─────┐
│ racing-track-maps-vector/ SVGs  [A]★ │   │ archive/builders/*.py                                 [X] │
│ lovely-car-data/ (car specs)    [A]  │   │  ├─ build_source_coverage.py      ★ (path fix needed)      │
│ lovely-track-data/ (unused)     [D]  │   │  └─ build_track_knowledge.py      ★ (path fix needed)      │
└───────────────────────────────────────┘   │ archive/legacy/registry/, imports/lovely/        [X]★    │
                                             │  (inputs the two scripts above actually need)             │
                                             │ archive/legacy/src_legacy/ (144-file previous gen)   [X]  │
                                             │  ├─ apply_axis_registry_to_packs.py      (merge dropped)  │
                                             │  ├─ apply_knowledge_registry_to_packs.py (merge dropped)  │
                                             │  └─ build_{critical_corner,inherited_tracks,              │
                                             │        lovely_alignment,mapped_tracks,                    │
                                             │        corner_classification}_library.py                  │
                                             │        → ONLY generator for 5 generated/ folders that     │
                                             │          now have no producer in current src/        [D]  │
                                             │ archive/experiments/** (superseded prototypes)       [X]  │
                                             └─────────────────────────────────────────────────────────┘

┌─ CORE GEOMETRY → CORNER → KNOWLEDGE PACK PIPELINE — the required spine, all [A]★ ─────────────────────┐
│                                                                                                        │
│  build_track_catalog.py ────────────────────────────────────────────► track_catalog.json              │
│                                                                                                        │
│  build_axis_library.py                                                                                │
│    (src/geometry/skeleton_generator.py + centreline_extractor.py)                                    │
│         └► axes/*.csv ─► normalize_axis_library.py ─► axes_normalized/*.csv                           │
│                              ├─► build_axis_registry.py ─► axis_registry.json         [output: D]     │
│                              └─► build_corner_candidate_library.py (curvature_peak_detector.py)       │
│                                       └► corner_candidates/ ─► build_corner_apex_library.py            │
│                                              └► corner_apexes/ ─► build_corner_region_library.py       │
│                                                     (corner_region_detector.py, region_deduplicator.py)│
│                                                        └► corner_regions/*.json                        │
│                                                              ├► build_corner_metrics_library.py        │
│                                                              │     └► corner_metrics/                  │
│                                                              │          └► build_corner_characteristics│
│                                                              │               _library.py                │
│                                                              │               (characteristics.py)       │
│                                                              │               └► corner_characteristics/ │
│                                                              ├► build_corner_dependency_library.py     │
│                                                              │     (corner_dependency.py)               │
│                                                              │     └► corner_dependencies/              │
│                                                              └► build_knowledge_registry.py             │
│                                                                    └► knowledge_registry.json [output:D]│
│                                                                                                        │
│  generated/<id>.json  (480 loose "named corner" files — regen via the two archived★ scripts, left)    │
│        ├──────────────────────┬─────────────────────────────┐                                        │
│        ▼                      ▼                             ▼                                        │
│  build_enriched_tracks.py          build_track_knowledge_pack.py ★ ◄── corner_regions/, youtube_know/ │
│   └► enriched_tracks/ [output:D]         └► knowledge_packs/*.json   ★★★ FINAL SHIPPED OUTPUT ★★★     │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ YOUTUBE ENRICHMENT — all [A], manual console-redirect steps, sparse (3 of 424 tracks) ──────────────┐
│ research/youtube/transcripts/*.json ★ (43 cached, already in git — no network needed to rebuild)     │
│   └► segment_turn_ranges.py ─► extract_turn_facts_v2.py                                              │
│        ├► build_track_fact_summary.py ─► track_fact_summary.json                                     │
│        └► build_track_turn_consensus.py ─► track_fact_summary.txt                                     │
│               └► build_youtube_knowledge_library.py ★ ─► youtube_knowledge/*.json                    │
│                     (feeds build_track_knowledge_pack.py above)                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ DEAD CODE — excluded from rebuild, imported by nothing ─────────────────────────────────────────────┐
│ src/models/track_knowledge.py   [D]  TrackFact/TrackKnowledge, never imported                         │
│ src/corners/track_insights.py   [D]  never imported, AND has a SyntaxError — won't even parse         │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ ACQUISITION / DISCOVERY AUTOMATION — ~110 files, all [A], NOT required to rebuild existing data ────┐
│ run_track_discovery / run_acquisition_cycle / run_scheduler_cycle / run_transcript_master              │
│   └► claim_next_track ─► build_search_payload ─► build_discovery_task ─► run_discovery_provider        │
│        (src/providers/: youtube_transcript_provider.py, ytdlp_caption_provider.py)                     │
│        └► select_best_guides ─► attempt_transcript_download ─► research/youtube/transcripts/*.json     │
│   + build_vehicle_index.py / build_vehicle_lookup.py  (reads $DATA_ROOT/lovely-car-data)                 │
│   + ~40 audit_*/report_*/test_*/preview_* diagnostic & manual-debug scripts                            │
│   Purpose: finds MORE videos/transcripts to feed the YouTube box above — not on the critical path      │
│   for reproducing what is already sitting in generated/ today.                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

See `SYSTEM_OVERVIEW.md`, `COMPONENT_CATALOG.md`, `DATA_FLOW_DIAGRAM.md`, and
`DEPENDENCY_MAP.md` for the full detail and evidence behind every claim on
this page.
