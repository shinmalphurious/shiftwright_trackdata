# Dependency Map

**What depends on what, at every level: Python imports, file I/O between
scripts, external libraries, and external data repositories.** This
complements `DATA_FLOW_DIAGRAM.md` (which shows the pipeline shape) by
focusing specifically on *dependency risk* — what breaks if something is
removed, missing, or changed.

---

## 1. Python import graph (code-level dependencies)

Most scripts in this repo do **not** import each other — they only share
data through files (see Section 2). The only real `import` edges between
modules are:

```text
src/pipelines/build_axis_library.py
    → src/geometry/skeleton_generator.py   (svg_to_skeleton)
    → src/geometry/centreline_extractor.py (skeleton_to_points, order_skeleton)

src/pipelines/build_corner_candidate_library.py
    → src/corners/curvature_peak_detector.py
src/pipelines/build_corner_apex_library.py
    → src/corners/curvature_peak_detector.py
src/pipelines/build_corner_region_library.py
    → src/corners/curvature_peak_detector.py
    → src/corners/corner_region_detector.py
    → src/corners/region_deduplicator.py
src/pipelines/build_corner_characteristics_library.py
    → src/corners/characteristics.py       (classify_corner, calculate_severity)
src/pipelines/build_corner_dependency_library.py
    → src/corners/corner_dependency.py     (calculate_exit_importance)

src/providers/provider_factory.py
    → src/providers/youtube_transcript_provider.py
    → src/providers/ytdlp_caption_provider.py
src/providers/youtube_transcript_provider.py
    → src/providers/transcript_provider.py (abstract base class)
src/providers/ytdlp_caption_provider.py
    → src/providers/transcript_provider.py

src/pipelines/attempt_transcript_download.py
    → src/providers/provider_factory.py
src/pipelines/test_transcript_provider.py
    → src/providers/provider_factory.py
src/pipelines/run_discovery_provider.py
    → src/shared/ytdlp_config.py
src/pipelines/inspect_caption_metadata.py
    → src/shared/ytdlp_config.py
src/pipelines/run_transcript_worker.py
    → src/shared/transcript_backoff.py
```

That is the **entire** internal import graph — 17 edges across 158
Python files. Everything else in `src/pipelines/` is a standalone script
that only talks to other scripts by reading/writing files in `generated/`
or `research/`.

**Never imported by anything** (true dead code, confirmed by searching
every `.py` file in the repo for a reference):

- `src/models/track_knowledge.py` (`TrackFact`, `TrackKnowledge`)
- `src/corners/track_insights.py` (`classify_insight`) — and this one
  also fails to even parse (`SyntaxError: unexpected character after
  line continuation character`, from `list[str\]` on line 6). Confirmed
  with `python -m ast` against every file in `src/`: this is the only
  file in the entire `src/` tree that does not compile.

**Orchestration via subprocess, not import** — a separate and much more
common pattern in `src/pipelines/`. Scripts like `run_track_discovery.py`,
`run_acquisition_cycle.py`, `run_discovery_batch.py`,
`run_transcript_master.py`, and `run_scheduler_cycle.py` call other
pipeline scripts with `subprocess.run([sys.executable, "-m",
"src.pipelines.<name>"])`. This means: (a) these dependencies are
**invisible to `grep "^from\|^import"`** — you have to search for string
literals of module names instead — and (b) there is no way to call these
steps from inside another Python program without spawning a new process.

---

## 2. File-level dependency graph (the real "API" of this repo)

Because scripts talk through files, the actual dependency surface is
"which script writes a path that another script reads." The high-risk
edges — where removing or renaming a file would silently break a
downstream script — are:

| Output file / folder | Written by | Read by |
|---|---|---|
| `generated/track_catalog.json` | `build_track_catalog.py` | `build_acquisition_registry.py`, `build_layout_alias_review.py`, `build_track_intelligence_library.py`, `build_track_map.py`, `build_track_search_library.py`, `build_youtube_coverage_report.py` |
| `generated/axes/<id>_axis.csv` | `build_axis_library.py` | `normalize_axis_library.py` |
| `generated/axes_normalized/<id>_axis.csv` | `normalize_axis_library.py` | `build_axis_registry.py`, `build_corner_metrics_library.py` |
| `generated/axis_registry.json` | `build_axis_registry.py` | **nothing in current `src/`** — but `archive/legacy/src_legacy/pipelines/apply_axis_registry_to_packs.py` used to merge it into every pack as `pack["axis"]`, before that step was dropped during the cleanup |
| `generated/corner_regions/<id>.json` | `build_corner_region_library.py` | `build_corner_metrics_library.py`, `build_corner_dependency_library.py`, `build_knowledge_registry.py`, `build_track_knowledge_pack.py` |
| `generated/corner_metrics/<id>.json` | `build_corner_metrics_library.py` | `build_corner_characteristics_library.py` |
| `generated/corner_characteristics/<id>.json` | `build_corner_characteristics_library.py` | `build_enriched_tracks.py` |
| `generated/corner_dependencies/<id>.json` | `build_corner_dependency_library.py` | `build_enriched_tracks.py` |
| `generated/knowledge_registry.json` | `build_knowledge_registry.py` | **nothing in current `src/`** — same story as `axis_registry.json`: `archive/legacy/src_legacy/pipelines/apply_knowledge_registry_to_packs.py` used to merge it in as `pack["knowledge_registry"]` |
| `generated/enriched_tracks/<id>.json` | `build_enriched_tracks.py` | **nothing found in current `src/`**; its extra fields (`exit_importance`, `corner_type`) never reach `knowledge_packs/` today |
| `generated/<id>.json` (loose, 480 files) | **an archived script** (`archive/builders/build_track_knowledge.py`) whose input paths now point to folders that moved — see Section 3 | `build_enriched_tracks.py`, `build_track_knowledge_pack.py` |
| `generated/youtube_knowledge/<id>.json` (only 3 files) | `build_youtube_knowledge_library.py` | `build_track_knowledge_pack.py` |
| `generated/knowledge_packs/<id>.json` | `build_track_knowledge_pack.py` | ★ terminal output — imported by the platform (`KnowledgePackImportService`); contract in `KNOWLEDGE_PACK.md` |
| `research/youtube/turn_ranges.csv` | `src/youtube/segment_turn_ranges.py`, manually redirected | `src/youtube/extract_turn_facts_v2.py` |
| `research/youtube/turn_facts_v2.csv` | `src/youtube/extract_turn_facts_v2.py`, manually redirected | `build_track_fact_summary.py`, `build_track_turn_consensus.py` |
| `research/youtube/track_fact_summary.txt` | `build_track_turn_consensus.py`'s sibling print-script, manually redirected | `build_youtube_knowledge_library.py` |
| `generated/track_acquisition_manifest.json` | `build_track_acquisition_manifest.py` | `claim_next_track.py`, `sync_manifest_from_knowledge.py`, and most of the acquisition orchestrators |
| `$DATA_ROOT/lovely-car-data/data/iracing/*.json` | external repo (not generated here) | `build_vehicle_index.py` |
| `$DATA_ROOT/racing-track-maps-vector/from-iracing/**/*.svg` | external repo (not generated here) | `build_track_catalog.py`, `build_axis_library.py` |

**Two outputs the current pipeline doesn't read, but used to feed the
packs:** `generated/axis_registry.json` and
`generated/knowledge_registry.json` — see the legacy `apply_*_to_packs.py`
scripts above. A third, likely still-genuinely-unused output:
`generated/enriched_tracks/`.

---

## 3. Data provenance / "what breaks if this is missing" risks

### Highest risk: the 480 loose `generated/<id>.json` files have no *working* generator at their expected paths

`build_enriched_tracks.py` and `build_track_knowledge_pack.py` — i.e.
**the entire value-add of "named corners"** in the final knowledge packs
— both depend on these files. Their only known generator,
`archive/builders/build_track_knowledge.py`, depends on three
hard-coded paths:

```text
registry/source_coverage.json     — produced by archive/builders/build_source_coverage.py,
                                     which itself reads registry/tracks.json
                                     and registry/lovely_coverage.json
imports/lovely/<id>.json          — per-car Lovely data, 129 files
```

None of `registry/`, `imports/` exist at the repository root anymore —
but the data was **relocated, not deleted**: it now lives at
`archive/legacy/registry/{tracks.json, lovely_coverage.json,
source_coverage.json}` and `archive/legacy/imports/lovely/*.json`. If any
of the 480 files needs regenerating (e.g. the upstream Lovely data
changes), the fix is to update the three path constants in
`archive/builders/build_track_knowledge.py` (and, if `source_coverage.json`
also needs refreshing, in `archive/builders/build_source_coverage.py`
too) to point at their new `archive/legacy/...` location, not to write a
generator from scratch. Still worth flagging as fragile: nothing
currently guards against these generated files silently going stale if
the Lovely source data in `archive/legacy/imports/lovely/` is updated
without anyone remembering this step exists.

### Second risk (resolved 2026-10-25): external datasets

Datasets are no longer copied into this repo. All paths resolve through
`src/shared/paths.py` → `SHIFTWRIGHT_DATA_ROOT` (default
`../Project_Shiftwright/external`, where they are pinned git submodules:
`racing-track-maps-vector`, `lovely-car-data`, `lovely-track-data`).
A fresh clone needs the platform repo checked out alongside, or the
variable set.

### Third risk: no dependency manifest for third-party Python packages

There is no `requirements.txt`, `pyproject.toml`, or `setup.py` anywhere
in the repository. The third-party packages actually imported by the
code (found by scanning every `import`/`from` line) are:

```text
numpy              — geometry/curvature math throughout
scipy              — KDTree, gaussian_filter1d, find_peaks
scikit-image       — skeletonize (src/geometry/skeleton_generator.py)
Pillow (PIL)       — Image/ImageDraw (src/geometry/skeleton_generator.py)
svgpathtools       — SVG parsing (src/geometry/skeleton_generator.py)
youtube_transcript_api — src/providers/youtube_transcript_provider.py
yt_dlp             — src/providers/ytdlp_caption_provider.py, src/shared/ytdlp_config.py
```

`pandas` and `matplotlib` also appear in the codebase, but only inside
`archive/experiments/` — none of the live `src/` pipeline imports either
of them.

A fresh environment has no authoritative list to install from; a
newcomer has to `pip install` on failure, one `ModuleNotFoundError` at a
time.

### Fourth risk: two incompatible "knowledge_level" vocabularies

`build_knowledge_registry.py` assigns one of `direct` / `inherited` /
`geometry_only`. `build_track_knowledge_pack.py` independently assigns
one of `named` / `geometry_only` to the same concept, using different
logic, and does not consult the registry at all. Any downstream
consumer (in Shiftwright, or a future script here) that expects the
three-value vocabulary documented in `docs/architecture.md` will get the
wrong answer if it actually reads from `knowledge_packs/`.

### Fifth risk: `docs/CORE_FILES.md` is slightly wrong as a rebuild list

Cross-checking `docs/CORE_FILES.md` against the real import/file graph
above:

- It correctly lists the 14 core pipeline scripts and the geometry/corner
  support modules.
- It lists `src/models/track_knowledge.py` and `src/corners/track_insights.py`
  as required — but neither is imported by anything (and the latter
  doesn't even parse). They are not actually needed to rebuild the
  pipeline.
- It references `core_pipeline_dump.txt` as the ultimate "source of
  truth" for this list. That file does exist (it was in `docs/`, now
  moved to `archive/docs/core_pipeline_dump.txt` alongside `CORE_FILES.md`
  itself) — it's a 2,415-line concatenation of the listed files' actual
  source code, generated for a one-time review rather than kept as a
  live build artifact. Since nothing regenerates or diffs against it,
  it will silently go stale the next time a core file changes; treat
  `docs/COMPONENT_CATALOG.md` as the live equivalent instead.

---

## 4. Directory-level architecture rules — how well are they followed?

`docs/Cleanup_plan.md` (Phase 3) defines three rules. Checked against the
actual repo:

| Rule | Status | Evidence |
|---|---|---|
| `src` imports `src` only | **Followed** | No `.py` file under `src/` imports from `research/` or `generated/` as code (confirmed by search); they only read generated files as plain data via `Path`/`open()`, which is the intended pattern. |
| `research` imports `src`, never the reverse | **Followed by omission** | No file under `research/` is itself a Python module that imports anything — `research/` contains only data (CSV/JSON/TXT), no code. |
| `generated` contains outputs only, no source code | **Followed** | Zero `.py` files found inside `generated/`. |

The directory-separation rules are, encouragingly, the one piece of the
cleanup plan that has actually held up — even though the finer-grained
goals in later phases (schema freeze, adapter architecture, console-output
removal) have not yet been reached.

---

## 5. Quick-reference: "if I change X, what do I need to re-run?"

```text
Change an SVG in $DATA_ROOT/racing-track-maps-vector
    → re-run: build_track_catalog, build_axis_library, normalize_axis_library,
              build_axis_registry, build_corner_candidate_library,
              build_corner_apex_library, build_corner_region_library,
              build_corner_metrics_library, build_corner_characteristics_library,
              build_corner_dependency_library, build_enriched_tracks,
              build_track_knowledge_pack
      (build_knowledge_registry too, though nothing reads its output)

Change src/corners/characteristics.py's classification thresholds
    → re-run: build_corner_characteristics_library only
      (does NOT require re-running geometry or apex/region detection)

Add a new transcript to research/youtube/transcripts/
    → re-run the full src/youtube/ chain by hand (segment_turn_ranges →
      redirect → extract_turn_facts_v2 → redirect → build_track_fact_summary
      AND build_track_turn_consensus → redirect) → build_youtube_knowledge_library
      → build_track_knowledge_pack

Add/update a track's named corners in generated/<id>.json
    → re-run: build_enriched_tracks, build_track_knowledge_pack
      (the generator for this file, archive/builders/build_track_knowledge.py,
      still exists but points at registry/ and imports/ folders that moved
      to archive/legacy/ — see Section 3's "highest risk" item — so either
      update its three path constants and re-run it, or edit generated/<id>.json
      by hand)
```
