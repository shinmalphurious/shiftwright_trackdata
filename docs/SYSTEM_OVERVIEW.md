# System Overview

**A beginner-friendly guide to what this repository is and how it works.**

This document assumes no prior knowledge of the codebase. It was written by
reading every source file, every generated artifact, and every existing
document in the repository as of 2026-10-24, and checking claims against
real file counts and real code rather than against other documentation.

---

## 1. What problem does this repo solve?

This repository produces **track knowledge** for the sim-racing project
"Shiftwright" — a separate project that lives outside this repo
(`E:\Project_Shiftwright`). "Track knowledge" means information about a
race track that a human coach or an AI assistant could use to explain the
track to a driver, for example:

- Where the corners are, and how sharp they are
- What a corner is *called* (e.g. "Eau Rouge", "Turn 1")
- Whether a corner is a hairpin, a fast sweeper, a chicane, a kink
- Whether a corner matters a lot for the next straight (exit-critical)
- What real drivers say about a corner in YouTube coaching videos
  (e.g. "slippery", "trail braking here", "flat in a GT3 car")

This is explicitly **not** telemetry analysis (lap times, speed traces,
etc.) — that logic lives inside Shiftwright itself. This repo only builds
*descriptive, human-readable* knowledge about tracks.

## 2. The three things this repo actually does

Reading the code reveals three largely separate subsystems, of very
different size and maturity. Documentation elsewhere in `docs/` only
really describes the first one.

### A. The Geometry → Corner → Knowledge Pack pipeline ("the core")

A deterministic, from-scratch-every-time pipeline that turns an SVG
drawing of a track's racing line into a structured description of its
corners. No AI, no manual labelling — pure geometry math (curvature,
peak detection, angle calculation). This is the most polished, most
reliable part of the repo. It runs over all **424 tracks** found in the
`racing-track-maps-vector` SVG collection and produces one output file
per track at every stage. See `DATA_FLOW_DIAGRAM.md` for the exact
stage-by-stage flow.

### B. The YouTube knowledge pipeline ("enrichment via coaching videos")

A much rougher, partly manual pipeline that tries to mine racing
knowledge out of YouTube video transcripts: it searches for coaching
videos, downloads their transcripts, and looks for sentences that
mention "Turn 7", "brake", "slippery", etc. It is the least mature part
of the system — several of its stages only print results to the
terminal (`print(...)`) rather than writing files, so a human has to
manually redirect the output into a CSV with `> file.csv`. This explains
an odd detail you'll see throughout the code: many files are read with
`encoding="utf-16"` — that's because Windows PowerShell writes redirected
output as UTF-16 text, not UTF-8. Right now only **3 out of 424** tracks
have any YouTube-derived knowledge attached.

### C. The acquisition / discovery subsystem ("finding more videos")

By far the *largest* amount of code in the repo (over 130 files in
`src/pipelines/`, versus roughly 20 for the core pipeline). This is an
automation system for continuously finding, downloading, and cataloguing
YouTube videos and their transcripts at scale: claiming the next track to
research, building search queries, calling a discovery provider (YouTube
Data API or `yt-dlp`), rate-limiting and backing off after failures,
matching videos to specific sim-racing cars ("vehicles"), and tracking
progress in various registries and queues. It is designed to be run
repeatedly/forever via small orchestrator scripts (`run_*.py`) that chain
these steps together with `subprocess`. It feeds subsystem B, but mostly
hasn't produced much usable output yet (see Section 5).

A fourth, much smaller area exists for **car/vehicle data** (matching
car names from `$DATA_ROOT/lovely-car-data` to car classes), which is used
by the acquisition subsystem to tag which car a coaching video is about.

## 3. The "shape" of the repository on disk

```text
track-knowledge/
├── src/                  Production Python code (158 files)
│   ├── geometry/         SVG -> skeleton -> ordered points -> curvature
│   ├── corners/          Curvature -> corner candidates -> characteristics
│   ├── models/           Data model definitions (mostly unused, see below)
│   ├── pipelines/        132 scripts: the core pipeline + all acquisition
│   ├── providers/        Pluggable transcript-fetching backends
│   ├── shared/           Small shared constants/helpers
│   └── youtube/          The original, simplest YouTube-mining scripts
│
├── generated/            7,286 tracked output files (the pipeline's results)
├── research/             Raw/working YouTube data: transcripts, CSVs, catalogs
├── data/                 A handful of small supporting data files
├── archive/              210 retired Python scripts + old analysis notes
├── config/               One small JSON config file for video discovery
├── docs/                 Architecture notes, plans, this document and its siblings
└── *.txt (top level)     Ad-hoc debug dumps from past investigations
```

A detail worth knowing: almost everything under `generated/`, `research/`
and `archive/` **is committed to git** (over 7,700 files combined) — this
is a repo that stores its data outputs in version control, not just its
code. Third-party datasets are not stored here at all: they live in the
shared data root (`SHIFTWRIGHT_DATA_ROOT`, see `src/shared/paths.py`).

## 4. How to navigate this codebase as a newcomer

1. Start with `docs/CORE_FILES.md` for the officially "blessed" 24-file
   list — but cross-check it against `COMPONENT_CATALOG.md` in this set,
   since the real pipeline needs a couple of files `CORE_FILES.md` omits
   and includes one or two that nothing actually imports.
2. Read `DATA_FLOW_DIAGRAM.md` before touching any pipeline script — the
   file-to-file dependencies are the real "API" of this codebase (scripts
   talk to each other only by reading/writing JSON/CSV files on disk,
   never by calling each other's functions).
3. Treat `src/pipelines/` as two different codebases living in one
   folder: a small, stable "track geometry" core, and a large, evolving
   "YouTube acquisition" automation system. Don't assume a file in
   `build_*` is part of the core just because of its prefix — most
   `build_*` files belong to acquisition.
4. `archive/` is retired code kept for reference — but don't skip it
   entirely. Nothing in current `src/` depends on it, but it depends on
   data folders (`registry/`, `imports/`) that were relocated to
   `archive/legacy/` rather than deleted, and it contains at least two
   working integration scripts (merging `axis_registry.json` and
   `knowledge_registry.json` into knowledge packs) that the current
   pipeline dropped. Treat it as read-only history that may still be
   worth reviving, not as noise.

## 5. Current state — what's solid, and what's visibly unfinished

This project reads as **AI-assisted, iteratively built**: individual
functions are small, clean, and well-tested conceptually (pure math, one
responsibility each), but the wiring between stages, naming
consistency, and documentation lag behind the code. Concretely:

- **Solid:** the geometry pipeline. 424/424 tracks produce a skeleton,
  centreline, axis, and curvature profile; corner detection and region
  building run end-to-end for all 424.
- **Inconsistent vocabulary:** two different pipelines independently
  invented a "knowledge_level" field with *different* possible values.
  `build_knowledge_registry.py` writes `direct` / `inherited` /
  `geometry_only`. `build_track_knowledge_pack.py` — the script that
  actually produces the final, shipped knowledge packs — writes only
  `named` / `geometry_only`, and never reads the registry at all. See
  `DEPENDENCY_MAP.md` for the proof.
- **Outputs the current pipeline no longer consumes, but used to:**
  `generated/knowledge_registry.json` and `generated/axis_registry.json`
  are each written by one script and read by nothing else in the
  *current* `src/` pipeline. This isn't because they were never meant to
  be used, though — a whole earlier generation of this pipeline, still
  sitting in `archive/legacy/src_legacy/pipelines/`, contains
  `apply_knowledge_registry_to_packs.py` and
  `apply_axis_registry_to_packs.py`, which merged exactly these two files
  into each knowledge pack (adding `pack["knowledge_registry"]` and
  `pack["axis"]`). That merge step did not survive the "32-file core
  architecture rebuild" recorded in the git history — it looks like
  enrichment that was dropped during cleanup, not something incomplete.
- **Data that looks frozen, but its source files are just relocated:**
  the 480 loose per-track JSON files directly under `generated/` (e.g.
  `generated/101.json`) — which hold the "named corners" that make a
  knowledge pack `named` instead of `geometry_only` — were produced by
  `archive/builders/build_track_knowledge.py`, a retired script that
  reads from a `registry/` folder and an `imports/lovely/` folder. Those
  exact folders don't exist at the repository root anymore, but their
  contents do: they were moved to `archive/legacy/registry/` and
  `archive/legacy/imports/lovely/` (129 cars' worth of Lovely data) when
  the project was cleaned up. The archived script would need its three
  path constants updated to point there before it could run again — it's
  a half-hour fix, not a lost cause.
- **Two files that look structural but are dead code:**
  `src/models/track_knowledge.py` (data classes `TrackFact`/`TrackKnowledge`)
  and `src/corners/track_insights.py` (`classify_insight`) are both listed
  in `docs/architecture.md` as pipeline stages, but neither is imported by
  *any* other file in the repository. `track_insights.py` additionally
  contains a real syntax error (`list[str\]` — a stray backslash) and
  would crash Python if anyone tried to import it today.
- **A duplicated step:** `src/pipelines/run_track_discovery.py` runs the
  step `archive_discovery_selection` twice in its list of steps — almost
  certainly a copy-paste slip rather than an intentional double-run.
- **The YouTube pipeline is a manual, fragile chain.** Several stages
  only `print()` their results; a human must redirect that output into a
  CSV by hand, which is why so much code reads files with
  `encoding="utf-16"`. Of 424 tracks, only 3 currently have any YouTube
  knowledge, confirming `docs/next steps.md`'s framing that this is the
  "next thing to fix."

None of this means the repo is broken — the core pipeline genuinely works
end-to-end for all 424 tracks, which is the hard part. It means the
*enrichment* layers (YouTube facts, car/vehicle tagging, acquisition
automation) are still works in progress, and the documentation in `docs/`
describes the intended end-state more than the current, partially-wired
reality. `DEPENDENCY_MAP.md` and `DATA_FLOW_DIAGRAM.md` in this set
describe what the code *actually* does today.
