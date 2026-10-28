# Component Catalog

**Every meaningful code module and data area in the repository, explained
in plain language.** Grouped by folder, in the order a newcomer should
read them. Each entry says what it does, and — where it matters — whether
anything else in the repo actually uses it.

Status tags used below:

- `ACTIVE` — part of a pipeline that still runs and is still consumed
- `ORPHAN` — exists and runs fine, but nothing downstream reads its output
- `DEAD CODE` — not imported or run by anything else in the repository
- `BROKEN` — contains an error that would stop it from running
- `ARCHIVED` — intentionally retired, kept for history only

---

## 1. `src/geometry/` — turning a picture of a track into numbers

| File | What it does (plain language) | Status |
|---|---|---|
| `skeleton_generator.py` | Takes an SVG drawing of a track's racing-line ribbon, traces its outline, fills it in as a black-and-white image, and "erodes" that shape down to a single thin line (a skeleton) using image-processing (`scikit-image`'s `skeletonize`). Think of it like finding the centre line of a thick hand-drawn stripe. | ACTIVE |
| `centreline_extractor.py` | The skeleton from the step above is just a scattered cloud of pixel coordinates with no order. This file puts them in order (nearest-neighbour walking, using a `KDTree` for fast lookups) so you get a connected line you can walk around the track with, start to finish. | ACTIVE |
| `curvature_analyzer.py` | Given an ordered line of (x, y) points, calculates how sharply the track bends at every point — its *curvature* — using basic calculus (first and second derivatives of position). Straight sections score near zero; tight corners score high. | ACTIVE (near-duplicate of `src/corners/curvature_peak_detector.py`'s curvature math — see `DEPENDENCY_MAP.md`) |
| `__init__.py` | Empty file that makes this folder an importable Python package. | ACTIVE |

## 2. `src/corners/` — turning curvature numbers into "corners"

| File | What it does (plain language) | Status |
|---|---|---|
| `curvature_peak_detector.py` | Smooths the curvature signal and finds its "peaks" — the points where the track bends the most. Each peak is a corner candidate. Uses `scipy.signal.find_peaks` with a threshold based on the top 10% of curvature values. | ACTIVE |
| `corner_region_detector.py` | A corner isn't just one point — it has a start, an apex, and an end. This file takes one apex (peak) and walks outward in both directions until the curvature drops below a threshold, to find where the corner actually begins and ends. | ACTIVE |
| `region_deduplicator.py` | Corner detection can find the same corner twice with slightly different boundaries. This removes overlapping duplicates, keeping whichever candidate is "stronger," then sorts what's left in track order. | ACTIVE |
| `characteristics.py` | Two small pure functions: `classify_corner()` labels a corner as a *kink*, *bend*, *corner*, or *hairpin* based on its turning angle, and `calculate_severity()` scores how demanding a corner is (0–1) from its angle and strength. | ACTIVE |
| `corner_dependency.py` | One function, `calculate_exit_importance()`: scores (0–1) how much a corner's exit matters, based on how long the following straight is — the longer the straight after the corner, the more a good exit is worth. | ACTIVE |
| `track_insights.py` | A single function, `classify_insight()`, meant to tag a corner as `critical_exit` and/or `heavy_braking_candidate`. Documented in `docs/architecture.md` as "Corner Classification Logic," but **nothing imports this file anywhere in the repository**, and it currently has a syntax error (`list[str\]`) that would crash on import. | **BROKEN + DEAD CODE** |
| `__init__.py` | Package marker. | ACTIVE |

## 3. `src/models/` — shared data shapes

| File | What it does (plain language) | Status |
|---|---|---|
| `track_knowledge.py` | Defines two small Python `@dataclass` types, `TrackFact` and `TrackKnowledge`, meant to represent a fact about a track and a bundle of facts for one track. Listed in `docs/architecture.md` as "Track Knowledge Data Models," but **no other file in the repository imports either class** — every pipeline builds its knowledge as plain dictionaries instead. | **DEAD CODE** |
| `__init__.py` | Package marker. | ACTIVE |

## 4. `src/providers/` — pluggable ways to fetch a YouTube transcript

| File | What it does (plain language) | Status |
|---|---|---|
| `transcript_provider.py` | Defines the "contract" (an abstract base class) that any transcript-fetching method must follow: a `fetch(video_id)` method. | ACTIVE |
| `youtube_transcript_provider.py` | One implementation of that contract, using the third-party `youtube_transcript_api` library to pull captions directly from YouTube. | ACTIVE |
| `ytdlp_caption_provider.py` | A second implementation, using `yt-dlp` (a general video-downloading tool) to pull captions instead — a fallback when the first method is blocked or rate-limited. | ACTIVE |
| `provider_factory.py` | A tiny "pick one" function: pass it the string `"youtube"` or `"ytdlp"` and it hands back the matching provider object. This is what lets the rest of the pipeline swap transcript sources without changing its own code. | ACTIVE |
| `__init__.py` | Package marker. | ACTIVE |

## 5. `src/shared/` — small shared helpers

| File | What it does (plain language) | Status |
|---|---|---|
| `transcript_backoff.py` | One function, `transcript_backoff_minutes(attempts)`, that returns how long to wait before retrying a failed transcript download — 30 min, then 2h, 6h, 12h, 24h, capping at 24h. This is classic "exponential backoff" so the acquisition system doesn't hammer YouTube after a failure. | ACTIVE |
| `ytdlp_config.py` | A dictionary of configuration options passed to `yt-dlp` (e.g. which subtitle languages/formats to request). | ACTIVE |

## 6. `src/youtube/` — the original, simplest YouTube-mining scripts

These four scripts are the first, simplest version of subsystem B
(YouTube knowledge). They run as a strict chain and are **console-print
pipelines** — each one (except the last) prints its results to the
terminal rather than writing a file, so a human must redirect the output
by hand (e.g. `python -m src.youtube.segment_turn_ranges > research/youtube/turn_ranges.csv`).
That manual step is also why several files read their own CSV input back
in with `encoding="utf-16"` — Windows PowerShell's `>` redirection
produces UTF-16 text files, not UTF-8.

| File | What it does (plain language) | Status |
|---|---|---|
| `segment_turn_ranges.py` | Scans every downloaded transcript for the words "turn 1", "turn two", etc. (including spelled-out numbers), and prints, for each mention, which lines of the transcript belong to that corner's discussion. | ACTIVE, console-only |
| `extract_turn_facts_v2.py` | Reads the turn-range CSV (the output of the step above) and, for each corner mention, checks the surrounding text for keywords like "brake", "trail", "apex", "slippery", "hairpin" — printing which keyword-derived "facts" apply. | ACTIVE, console-only |
| `build_track_turn_consensus.py` | Reads the facts CSV and video-to-track lookup, and prints, per track *and per named corner*, how many times each fact keyword came up across all videos about that track. | ACTIVE, console-only |
| `build_track_fact_summary.py` | Same idea as above, but summarised per *track* (not per corner), and this one **does** write a real file: `research/youtube/track_fact_summary.json`. | ACTIVE, writes a file |
| `__init__.py` | Package marker. | ACTIVE |

## 7. `src/pipelines/` — 132 scripts: the core pipeline plus everything else

This is the largest folder by far. It mixes four very different kinds of
scripts together with no subfolders to separate them. Grouped by what
they actually do:

### 7a. Core geometry → corner → knowledge-pack pipeline (ACTIVE, runs for all 424 tracks)

| File | What it does |
|---|---|
| `build_track_catalog.py` | Scans the `racing-track-maps-vector` SVG folder and lists every track/layout it finds, writing `generated/track_catalog.json`. |
| `build_axis_library.py` | Runs every SVG through `skeleton_generator` + `centreline_extractor` and saves the raw, unevenly-spaced centreline as `generated/axes/<id>_axis.csv`. |
| `normalize_axis_library.py` | Resamples each raw centreline to exactly 2,048 evenly-spaced points (by lap distance), writing `generated/axes_normalized/<id>_axis.csv`. This — not `build_axis_library.py` — is the step that produces the "2,048 samples per track" figure quoted elsewhere in the docs. |
| `build_axis_registry.py` | Summarises each normalized axis file into a small metadata record (point count, lap coordinate system), writing `generated/axis_registry.json`. Nothing in the current pipeline reads this back — it used to be merged into packs by an archived script (`ORPHAN` output today; see `DATA_FLOW_DIAGRAM.md`). |
| `build_corner_candidate_library.py` | Runs curvature-peak detection over every normalized axis to find raw corner candidates. |
| `build_corner_apex_library.py` | Refines candidates into confirmed apex points. |
| `build_corner_region_library.py` | Expands each apex into a start/apex/end region and removes duplicates, writing `generated/corner_regions/<id>.json`. |
| `build_corner_metrics_library.py` | For each corner region, measures its angle (using the geometry of start/apex/end points) and width, writing `generated/corner_metrics/<id>.json`. |
| `build_corner_characteristics_library.py` | Classifies each corner (kink/bend/corner/hairpin) and scores its severity, writing `generated/corner_characteristics/<id>.json`. |
| `build_corner_dependency_library.py` | Scores how much each corner's exit matters based on the length of the next straight, writing `generated/corner_dependencies/<id>.json`. |
| `build_enriched_tracks.py` | Merges named corners (from the loose `generated/<id>.json` files), dependency scores, and characteristics into one record per track, writing `generated/enriched_tracks/<id>.json`. |
| `build_knowledge_registry.py` | Produces a summary of knowledge coverage per track (`direct`/`inherited`/`geometry_only`). Same story as above: written, but nothing currently reads it back (`ORPHAN` output; see `DATA_FLOW_DIAGRAM.md` and `DEPENDENCY_MAP.md` for the archived script that used to consume it). |
| `build_track_knowledge_pack.py` | The final step. Combines the loose `generated/<id>.json` track record, its corner regions, and any YouTube knowledge into one shipped file per track: `generated/knowledge_packs/<id>.json`. This is the file Shiftwright is meant to actually consume. |
| `build_acquisition_registry.py` | Produces a status/coverage report over the track catalog for the acquisition subsystem (not the geometry pipeline). |

### 7b. Acquisition & discovery automation (the largest group — roughly 110 files)

These scripts implement an always-on loop for finding new YouTube videos
and transcripts. They are designed to be chained by small orchestrator
scripts using `subprocess` rather than imported as functions. Representative
examples, grouped by role:

- **Orchestrators** (`run_track_discovery.py`, `run_acquisition_cycle.py`,
  `run_discovery_batch.py`, `run_scheduler_cycle.py`,
  `run_transcript_master.py`, `run_transcript_worker.py`,
  `run_transcript_pipeline.py`, `run_discovery_provider.py`,
  `run_acquisition_until_empty.py`) — each one runs a fixed sequence of
  other pipeline scripts as subprocesses, sometimes in a `while True:`
  loop (e.g. `run_transcript_master.py` runs forever, logging to
  `generated/transcript_master.log`). Note: `run_track_discovery.py`'s
  step list repeats `archive_discovery_selection` twice — likely a bug.
- **Queue/claim management** (`claim_next_track.py`,
  `claim_next_transcript.py`, `claim_next_transcript_task.py`,
  `claim_next_processing_track.py`, `release_transcript_queue.py`,
  `build_transcript_queue.py`, `build_transcript_tasks.py`,
  `upgrade_transcript_queue.py`) — these implement a simple work-queue
  pattern: pick the next track/video that needs processing, mark it as
  claimed, and release it back if the attempt fails.
- **Search & discovery** (`build_search_payload.py`,
  `build_search_terms_queue.py`, `build_discovery_task.py`,
  `rank_search_queries.py`, `prepare_discovery_query.py`,
  `execute_search_task.py`, `select_best_guides.py`,
  `store_selected_guides.py`) — build YouTube search queries per track,
  send them to the configured provider (`config/acquisition.json` picks
  `youtube_data_api`), and pick the best-looking results.
- **Transcript downloading & rate limiting**
  (`attempt_transcript_download.py`, `download_transcripts.py`,
  `download_single_vtt.py`, `init_transcript_rate_limit.py`,
  `record_transcript_429.py`, `start_transcript_cooldown.py`,
  `schedule_transcript_retry.py`, `mark_transcript_downloaded.py`,
  `cache_transcript_metadata.py`, `cache_caption_capabilities.py`,
  `inspect_caption_metadata.py`, `inspect_caption_urls.py`,
  `parse_json3_transcripts.py`) — the actual network calls, HTTP 429
  (rate-limit) handling via `transcript_backoff.py`, and caching.
- **Vehicle/car matching** (`build_vehicle_index.py`,
  `build_vehicle_lookup.py`, `build_vehicle_coverage.py`,
  `build_vehicle_alias_candidates.py`, `build_vehicle_alias_lookup.py`,
  `merge_vehicle_aliases.py`, `extract_vehicle_terms.py`,
  `build_car_profile.py`, `group_discovery_by_car.py`) — reads car data
  from `$DATA_ROOT/lovely-car-data` and tries to recognise which
  real-world/sim car a coaching video discusses, so knowledge can later
  be tagged "this applies to a GT3 car," etc.
- **Guide/content cataloguing** (`build_guide_registry.py`,
  `build_guide_metadata_registry.py`, `rebuild_guide_catalog.py`,
  `report_guide_catalog.py`, `report_catalog_summary.py`,
  `build_video_track_registry.py`) — keep a catalogue of which
  "guides" (videos) exist for which track.
- **Vocabulary & term mining** (`build_discovered_vocabulary.py`,
  `build_discovery_vocabulary.py`, `extract_discovered_terms.py`) —
  collect recurring words/phrases found across transcripts, likely to
  seed better keyword lists than the hard-coded `FACT_WORDS` dictionary
  in `extract_turn_facts_v2.py`.
- **Audits & diagnostics** (`audit_discovery_quality.py`,
  `audit_missing_discovery.py`, `audit_search_failure.py`,
  `audit_turn_order_coverage.py`, `audit_unclassified_content.py`,
  `audit_unclassified_videos.py`, `audit_unknown_vehicle_guides.py`,
  `audit_vehicle_classification.py`, `capture_search_failure.py`) —
  read-only scripts that print statistics about gaps/failures, intended
  for a human to run and inspect, not for other pipelines to depend on.
- **Manifest syncing** (`sync_manifest_from_knowledge.py`,
  `sync_manifest_from_transcripts.py`,
  `sync_manifest_from_video_registry.py`,
  `build_track_acquisition_manifest.py`,
  `update_track_state.py`) — keep one central "where does each track
  stand" manifest up to date from several different sources of truth.
- **One-off tests/experiments left in `src/pipelines/`**
  (`test_caption_language.py`, `test_caption_transport.py`,
  `test_direct_caption_url.py`, `test_node_runtime.py`,
  `test_subtitle_availability.py`, `test_transcript_provider.py`,
  `test_vehicle_lookup.py`, `preview_next_search.py`,
  `preview_next_transcript.py`, `preview_transcript_acquisition.py`,
  `download_caption_test.py`) — manual debugging scripts, not an
  automated test suite (there is no `pytest`/`unittest` runner wired
  into this repo).
- **Bridges into the YouTube knowledge pipeline**
  (`build_youtube_knowledge_library.py` — turns the legacy
  `track_fact_summary.txt` console dump into
  `generated/youtube_knowledge/<id>.json`; `build_youtube_evidence_library.py`,
  `build_youtube_priority_queue.py`, `build_youtube_coverage_report.py`,
  `cleanup_youtube_knowledge.py`, `merge_youtube_knowledge.py`,
  `enrich_pack_corner_knowledge.py`, `build_corner_knowledge_library.py`,
  `build_turn_consensus_library.py`, `build_turn_fact_confidence.py`,
  `build_turn_order_consensus.py`, `build_turn_order_library.py`,
  `normalize_turn_consensus.py`, `normalize_pack_turn_keys.py`) —
  a second, more structured generation of the YouTube-fact pipeline
  described in `docs/Cleanup_plan.md` Phase 7, layered on top of the
  original `src/youtube/` scripts.
- **Other map/search utilities** (`build_track_map.py`,
  `build_track_search_library.py`, `build_layout_alias_review.py`,
  `build_track_intelligence_library.py`, `build_corner_attention_model.py`,
  `build_corner_priority_library.py`, `build_corner_intelligence_library.py`,
  `build_discovery_effectiveness.py`, `build_discovery_results.py`,
  `build_discovery_result_template.py`, `ingest_discovery_result.py`,
  `ingest_discovery_result_file.py`, `ingest_discovery_selection.py`,
  `ingest_transcript_result.py`, `report_acquisition_status.py`,
  `report_discovery_priorities.py`, `archive_discovery_selection.py`) —
  supporting pieces of the acquisition subsystem for ranking, archiving,
  and reporting on discovery results.
- **`__init__.py`** — package marker.

## 8. `archive/` — retired code (210 Python files + analysis notes)

`archive/builders/` holds an earlier generation of the knowledge pipeline
(e.g. `build_track_knowledge.py`, `apply_inheritance.py`,
`build_layout_families.py`, `build_track_categories.py`). Notably,
`archive/builders/build_track_knowledge.py` is the script that originally
produced the 480 loose per-track JSON files still sitting in
`generated/` today (see `DEPENDENCY_MAP.md` Section 3). It reads from a
`registry/` folder and an `imports/lovely/` folder which no longer exist
*at the repository root* — but their contents are still in the repo,
relocated to `archive/legacy/registry/` and `archive/legacy/imports/lovely/`.
The script would need its path constants updated before it could run
again; the underlying data was not deleted.

`archive/legacy/src_legacy/` is a much larger discovery: a near-complete
**previous generation of the entire `src/` tree** (144 Python files,
mirroring `pipelines/`, `geometry/`, `corners/`, `models/`, `youtube/`,
plus a `services/` and `sources/` folder that the current `src/` doesn't
have at all). It includes several scripts with no equivalent in today's
pipeline — most importantly `apply_axis_registry_to_packs.py` and
`apply_knowledge_registry_to_packs.py`, which used to merge
`axis_registry.json` and `knowledge_registry.json` into every knowledge
pack (see `DATA_FLOW_DIAGRAM.md`'s note on this). `archive/legacy/registry/`
and `archive/legacy/imports/` are this legacy pipeline's data folders.
`archive/legacy/racing-track-maps-vector-testing/` appears to be an older,
local snapshot of the external SVG source repo used for testing before
`$DATA_ROOT/racing-track-maps-vector` was adopted.

`archive/experiments/experiments/` holds one-off geometry experiments
(SVG seam-finding, coordinate alignment, skeleton extraction variants,
several using `pandas`/`matplotlib` for visual debugging) — exploratory
work that was superseded by the current `src/geometry/` module.

`archive/analysis/`, `archive/commentary/`, `archive/reports/`,
`archive/images/`, `archive/inheritance/`, `archive/mapping/`,
`archive/scanners/`, and `archive/youtube/` hold further retired scripts
and plain-text/image notes from past investigations.

None of today's `src/` imports anything from `archive/`, and nothing in
`archive/` is run by any current pipeline or orchestrator. Status:
**ARCHIVED** — but, as above, not irrelevant: it's the best record of
why today's pipeline is shaped the way it is, and it holds working code
and data for at least two features (`axis`/`knowledge_registry` merging)
that were dropped rather than finished.

## 9. Data folders (not code)

| Folder | Contents | Produced by |
|---|---|---|
| `generated/` | 7,286 tracked files: all pipeline outputs. 480 loose `generated/<id>.json` track records (frozen legacy, see above), plus 22 subfolders (`axes/`, `corner_regions/`, `knowledge_packs/`, etc.) each holding one file per track for one pipeline stage. | The `src/pipelines/` core scripts (for the subfolders) + an archived script (for the loose root files) |
| `research/` | 67 tracked files: raw/working YouTube data — transcripts (43 cached), video catalogs, the turn/fact CSVs, `track_fact_summary.json`. | `src/youtube/` scripts + the acquisition subsystem |
| `data/` | 6 small supporting files. | Not traced to a specific generator in this pass — treat as manually curated. |
| `config/acquisition.json` | One small JSON file: `{"provider": "youtube_data_api", "max_results": 5, "preferred_video_type": "lap_walkthrough"}` — the only tunable setting discovered for the entire discovery subsystem. | Manually edited |
| `external/` | Full git clones of three other repositories: `racing-track-maps-vector` (SVG track geometry, actively used), `lovely-car-data` (car specs, actively used), and a nested `external/lovely-track-data` clone that **no current code references**. Git-ignored, not committed. | Cloned manually, not by any script in this repo |
| Top-level `*.txt` dumps (`485_enriched_youtube_dump.txt`, `caption_transport_dump.txt`, `caption_url.txt`, `repo_inventory.txt`, `transcript_pipeline_dump.txt`) | Ad-hoc, one-off debugging output saved from past terminal sessions (matching the command patterns in `REPO_AUDIT_COMMANDS.md`). Not consumed by any pipeline. | Manual `>` redirection during past debugging |

---

## Summary table — status counts

| Status | Count | Examples |
|---|---|---|
| ACTIVE (part of a running pipeline) | ~155 of 158 `src/` files | Everything in `src/geometry/`, `src/providers/`, `src/shared/`, almost all of `src/pipelines/` |
| DEAD CODE (unused) | 2 | `src/models/track_knowledge.py`, `src/corners/track_insights.py` |
| BROKEN (syntax error) | 1 | `src/corners/track_insights.py` (also dead code) |
| Outputs not read by the current pipeline, but previously wired in | 2 known | `generated/axis_registry.json`, `generated/knowledge_registry.json` (see `archive/legacy/src_legacy/pipelines/apply_*_to_packs.py`) |
| ARCHIVED | 210 files in `archive/builders`, `archive/experiments`, etc. + 144 more in `archive/legacy/src_legacy/` | everything under `archive/` |
| Generated data whose generator moved, not disappeared | 480 files | loose `generated/<id>.json` track records — generator and inputs now live under `archive/legacy/` and `archive/builders/` |
