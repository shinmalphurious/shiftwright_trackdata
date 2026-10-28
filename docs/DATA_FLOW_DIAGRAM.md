# Data Flow Diagram

**How information actually moves through this repository**, traced
directly from the source code (not from other documentation — see
`DEPENDENCY_MAP.md` for several places where the code disagrees with
`docs/architecture.md`).

Everything in this repo communicates through **files on disk**, never
through function calls between scripts. Every arrow below is a real
"script A writes a file → script B reads that file" relationship,
confirmed by reading both scripts.

---

## 1. The core pipeline: from an SVG drawing to a knowledge pack

This is the one flow that runs cleanly end-to-end for all 424 tracks.

```text
$DATA_ROOT/racing-track-maps-vector/.../turns.svg   (one per track layout)
        │
        ▼
build_track_catalog.py
        │  writes
        ▼
generated/track_catalog.json                       (424 track records)


$DATA_ROOT/racing-track-maps-vector/.../active.svg
        │
        ▼
build_axis_library.py
  uses: src/geometry/skeleton_generator.py   (SVG → pixel skeleton)
        src/geometry/centreline_extractor.py (skeleton → ordered points)
        │  writes
        ▼
generated/axes/<id>_axis.csv                       (424 files, uneven point counts: ~900–4,300 rows)
        │
        ▼
normalize_axis_library.py
        │  writes
        ▼
generated/axes_normalized/<id>_axis.csv            (425 files*, uniform 2,048 points each)
        │
        ├──────────────────────────────────────────────┐
        ▼                                               ▼
build_axis_registry.py                        build_corner_candidate_library.py
        │  writes                               uses: src/corners/curvature_peak_detector.py
        ▼                                               │  writes
generated/axis_registry.json                           ▼
   (424 entries — not read by any            generated/corner_candidates/<id>.json
    CURRENT script, see note below)                    │
                                                         ▼
                                              build_corner_apex_library.py
                                                         │  writes
                                                         ▼
                                              generated/corner_apexes/<id>.json
                                                         │
                                                         ▼
                                              build_corner_region_library.py
                                                uses: src/corners/corner_region_detector.py
                                                      src/corners/region_deduplicator.py
                                                         │  writes
                                                         ▼
                                              generated/corner_regions/<id>.json   (424 files)
                                                         │
                     ┌───────────────────────────────────┼─────────────────────────┐
                     ▼                                   ▼                         ▼
          build_corner_metrics_library.py       build_knowledge_registry.py        │
            (also reads axes_normalized/)                 │  writes                │
                     │  writes                            ▼                        │
                     ▼                          generated/knowledge_registry.json  │
          generated/corner_metrics/<id>.json       (424 entries, direct/inherited/ │
                     │                               geometry_only — see note)     │
                     ▼                                                             │
          build_corner_characteristics_library.py                                  │
            uses: src/corners/characteristics.py                                   │
                     │  writes                                                     │
                     ▼                                                             │
          generated/corner_characteristics/<id>.json                               │
                                                                                    │
          generated/corner_regions/<id>.json  ────────────────────────────────┐   │
                     │                                                        ▼   │
                     ▼                                          build_corner_dependency_library.py
                                                                   uses: src/corners/corner_dependency.py
                                                                        │  writes
                                                                        ▼
                                                             generated/corner_dependencies/<id>.json
                     │                                                 │
                     └───────────────────┬─────────────────────────────┘
                                          ▼
                              build_enriched_tracks.py
                      reads: generated/<id>.json  (loose, legacy "named corner" files —
                                                     see Section 3: their generator was
                                                     archived, but its inputs still exist,
                                                     just relocated)
                             generated/corner_dependencies/<id>.json
                             generated/corner_characteristics/<id>.json
                                          │  writes
                                          ▼
                              generated/enriched_tracks/<id>.json     (424 files)


generated/<id>.json  (loose, legacy)  ──┐
generated/corner_regions/<id>.json  ────┼──►  build_track_knowledge_pack.py
generated/youtube_knowledge/<id>.json ──┘           │  writes
                                                     ▼
                                       generated/knowledge_packs/<id>.json   (424 files)
                                                                 ★ THE FINAL SHIPPED OUTPUT ★
```

\* `generated/axes_normalized/` has **425** files, not 424 — one extra
file, `403_axis_aligned.csv`, uses a different naming pattern and has no
matching entry anywhere else downstream. See `DEPENDENCY_MAP.md`.

### Important: `axis_registry.json` and `knowledge_registry.json` used to flow into the packs — and don't anymore

Both files are dead ends in the *current* pipeline. But an earlier,
larger version of this codebase — preserved at
`archive/legacy/src_legacy/pipelines/` — had two extra steps,
`apply_axis_registry_to_packs.py` and `apply_knowledge_registry_to_packs.py`,
that merged exactly these two files into every knowledge pack (adding a
`pack["axis"]` field and a `pack["knowledge_registry"]` field
respectively). When the repository was pruned down to today's smaller
"core architecture" (see the git history around
`ff2b82de`/`aa2bf1bb`/`a8cad080`), those two merge steps were not carried
forward. This reads as a dropped integration, not an unfinished one —
worth deciding deliberately whether to restore it rather than leaving
these two generators quietly producing output nothing uses.

### Important: `build_enriched_tracks.py` and `build_track_knowledge_pack.py` are two separate, parallel endings

Both scripts take the same raw ingredients (named corners + corner data)
and merge them — but into two **different, independent output files**
that nothing else connects back together:

- `build_enriched_tracks.py` → `generated/enriched_tracks/<id>.json`
  (named corners + exit-importance + corner-type classification)
- `build_track_knowledge_pack.py` → `generated/knowledge_packs/<id>.json`
  (named corners + raw corner regions + YouTube summary — does **not**
  include the exit-importance or corner-type fields that
  `enriched_tracks` computes)

`docs/next steps.md` and `docs/Cleanup_plan.md` both describe
`knowledge_packs/` as "the single source of truth" that all enrichment
should flow into — but as of this analysis, `enriched_tracks/`'s richer
per-corner data (`exit_importance`, `dependency_reason`, `corner_type`)
is **not** merged into the knowledge packs. They are sibling outputs,
not a chain.

---

## 2. The YouTube knowledge pipeline (manual, console-based, lightly used)

```text
research/youtube/transcripts/<video_id>.json   (43 cached transcripts)
        │
        ▼
src/youtube/segment_turn_ranges.py        (prints to terminal — must be redirected by hand)
        │  human runs:  python -m src.youtube.segment_turn_ranges > research/youtube/turn_ranges.csv
        ▼
research/youtube/turn_ranges.csv          (UTF-16 text, because of PowerShell redirection)
        │
        ▼
src/youtube/extract_turn_facts_v2.py      (prints to terminal — must be redirected by hand)
        │  human runs:  python -m src.youtube.extract_turn_facts_v2 > research/youtube/turn_facts_v2.csv
        ▼
research/youtube/turn_facts_v2.csv
        │
        ├──────────────────────────────────┐
        ▼                                   ▼
build_track_fact_summary.py        build_track_turn_consensus.py
  (writes a real file)                (prints to terminal — redirected by hand)
        │  writes                          │  human runs: ... > research/youtube/track_fact_summary.txt
        ▼                                  ▼
research/youtube/                  research/youtube/
  track_fact_summary.json            track_fact_summary.txt   (UTF-16, legacy format)
        │                                  │
        │                                  ▼
        │                    build_youtube_knowledge_library.py
        │                      also reads: research/youtube/track_map.json
        │                                  │  writes
        │                                  ▼
        │                    generated/youtube_knowledge/<id>.json   (only 3 files exist)
        │                                  │
        └──────────────────────────────────┴───►  consumed by build_track_knowledge_pack.py
                                                     (see Section 1)
```

Only **3 of 424** tracks currently have a file in
`generated/youtube_knowledge/`, which is why only 3 knowledge packs have
non-empty `youtube_summary`/`turn_consensus` fields. This matches what
`docs/next steps.md` flags as the top development priority.

---

## 3. Where the "named corners" actually come from (and how to regenerate them)

Every knowledge pack's `named_corners` field — the thing that makes a
pack richer than bare geometry — comes from a loose file like
`generated/101.json` sitting directly in `generated/` (480 of these
exist). Tracing where *those* came from leads outside the current
`src/` pipeline into `archive/`:

```text
archive/legacy/registry/tracks.json  ──┐
archive/legacy/registry/lovely_coverage.json
        │
        ▼
(archived) archive/builders/build_source_coverage.py
        │  writes
        ▼
archive/legacy/registry/source_coverage.json   (already present — this step
                                                  doesn't even need re-running)
        │
        ▼
(archived) archive/builders/build_track_knowledge.py
   reads: archive/legacy/imports/lovely/<id>.json   (129 cars' worth of Lovely data)
        │  writes
        ▼
generated/<id>.json   ★ still present today, still used by the pipeline ★
```

The script and its two input folders (`registry/`, `imports/lovely/`)
are no longer at the repository root where `build_track_knowledge.py`'s
hard-coded `Path("registry/source_coverage.json")` and
`Path("imports/lovely")` expect them — they were moved to
`archive/legacy/registry/` and `archive/legacy/imports/lovely/` when the
project was cleaned up. **The data was not lost, only relocated.** To
regenerate these files today, someone would need to either copy
`archive/legacy/registry/` and `archive/legacy/imports/` back to the
repository root, or (cleaner) edit the three path constants at the top
of `archive/builders/build_track_knowledge.py` to point at their new
location and run it from there.

---

## 4. The acquisition / discovery subsystem (feeds Section 2, loosely)

This is a queue-driven loop, not a straight-line pipeline. Simplified:

```text
generated/track_acquisition_manifest.json  (which tracks need video research)
        │
        ▼
claim_next_track.py  ──►  marks one track as "claimed"
        │
        ▼
build_search_payload.py  ──►  build_discovery_task.py
        │
        ▼
run_discovery_provider.py
   uses: src/providers/provider_factory.py
            → youtube_transcript_provider.py   (YouTube Data API)
            → ytdlp_caption_provider.py        (yt-dlp fallback)
        │
        ▼
select_best_guides.py  ──►  store_selected_guides.py  ──►  archive_discovery_selection.py
        │
        ▼
 (new video found)  ──►  claim_next_transcript_task.py  ──►  attempt_transcript_download.py
        │                                                        │
        │                                       success ─────────┤───────── failure
        │                                                         ▼                ▼
        │                                          research/youtube/transcripts/   record_transcript_429.py
        │                                            <video_id>.json                      │
        │                                                         │               src/shared/transcript_backoff.py
        │                                                         ▼                        │
        │                                          (feeds Section 2's input)   schedule_transcript_retry.py
        ▼
build_vehicle_index.py / build_vehicle_lookup.py
   reads: $DATA_ROOT/lovely-car-data/data/iracing/*.json
        │
        ▼
(tags which sim-racing car a video is about — used by audit_vehicle_classification.py etc.)
```

Orchestrator scripts (`run_track_discovery.py`, `run_acquisition_cycle.py`,
`run_discovery_batch.py`, `run_transcript_master.py`) just run the steps
above in sequence or in a loop via `subprocess`, rather than being called
as functions. `run_transcript_master.py` literally loops forever
(`while True:`), logging to `generated/transcript_master.log`, until
someone stops it manually.

---

## 5. One-paragraph summary

Geometry (SVG) flows cleanly and completely into corner data for all 424
tracks. Separately, a large automation system tries to discover and
download YouTube coaching videos, which *can* flow into a small,
mostly-manual text-mining pipeline that extracts keyword "facts" from
transcripts — but today that pipeline has only produced output for 3
tracks. The final knowledge pack for each track is assembled from three
sources — legacy "named corner" data (regenerable, but only via an
archived script whose paths need updating), fresh geometry data (fully
regenerable), and sparse YouTube data (barely populated) — and two
enrichment steps that a previous version of this pipeline used to merge
in (`knowledge_registry.json`, `axis_registry.json`), plus a third
parallel analysis (`enriched_tracks/`'s richer per-corner scores), no
longer make it into the final shipped file.
