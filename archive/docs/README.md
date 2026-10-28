# Archived Documentation

These documents were moved here on 2026-10-24 during a documentation
cleanup. They are **not deleted** — just taken out of the active `docs/`
folder so a newcomer (human or AI) doesn't load stale or duplicate
material into context by default. Each entry below says why it was
archived and what replaced it.

| File | Why archived | Superseded by |
|---|---|---|
| `architecture.md` | A byte-for-byte copy of `chat primer.md`, except ~100 characters were silently corrupted to `*` in every commit (breaks from line 138 on — code fences, `---` separators, and words are mangled). Also missing the later pipeline stages (`normalize_axis_library`, `build_axis_registry`, metrics/characteristics/dependencies). | `docs/DATA_FLOW_DIAGRAM.md` |
| `chat primer.md` | The clean source `architecture.md` was corrupted from — same content, just not garbled. Kept only as the un-corrupted reference until the replacement doc existed. | `docs/DATA_FLOW_DIAGRAM.md` |
| `ARCHITECTURE_FREEZE.md` | A one-time "424 everywhere, PRODUCTION CORE" snapshot with no way to tell if it's still true. | `docs/ONE_PAGE_ARCHITECTURE.md`, `docs/COMPONENT_CATALOG.md` |
| `BASELINE_COUNTS.md` | Same kind of static count snapshot, same staleness risk. | `docs/COMPONENT_CATALOG.md`, `docs/DEPENDENCY_MAP.md` |
| `CORE_FILES.md` | Listed as the rebuild source of truth, but verified inaccurate: includes `src/models/track_knowledge.py` and `src/corners/track_insights.py`, neither of which anything imports (the second doesn't even parse — real `SyntaxError`). | `docs/COMPONENT_CATALOG.md` (status-tagged, verified against actual imports) |
| `core_pipeline_dump.txt` | The 2,415-line source dump `CORE_FILES.md` called its "source of truth." Archived alongside it — a one-time concatenation of file contents, not a live artifact anything regenerates or diffs against. | `docs/COMPONENT_CATALOG.md` |
| `inventory/` | Raw PowerShell/CSV inventory output from the *previous* cleanup effort (the one recorded in the git history as "32-file core architecture rebuild") — includes two very large before/after directory-listing dumps (`repo_listing_before_cleanup.txt`, 1.5 MB; `repo_tree_before_cleanup.txt`, 324 KB) that are pure token-bloat risk if ever loaded. | `docs/COMPONENT_CATALOG.md`, `docs/DEPENDENCY_MAP.md` |
| `SOURCE_EVALUATION.md` | Pre-implementation brainstorming about candidate knowledge sources (OSM, DEMs, driver guides) written before the pipeline existed. Most of it was never acted on. | `docs/DEPENDENCY_MAP.md` §3 (what's actually wired in today) |
| `SOURCE_MATRIX.md` | A second, overlapping version of the same brainstorm with a slightly different source list. | same as above |
| `YOUTUBE_ARCHITECTURE.md` | A short duplicate of the YouTube pipeline section already in the old `architecture.md`/`chat primer.md`, with its arrows corrupted to `?` by an encoding round-trip. | `docs/DATA_FLOW_DIAGRAM.md` §2 |
| `REPO_AUDIT_COMMANDS.md` | A grab-bag of PowerShell/Python one-liners for manual repo inspection. Several reference files that no longer exist (e.g. `generated/discovery_effectiveness.json`). The investigation it supported is now written up properly. | `docs/COMPONENT_CATALOG.md`, `docs/DEPENDENCY_MAP.md` |

Also moved (not documentation, but historical debug output cluttering
the repo root): `485_enriched_youtube_dump.txt`, `caption_transport_dump.txt`,
`caption_url.txt`, `repo_inventory.txt`, `transcript_pipeline_dump.txt` →
`archive/analysis/`. None of these were read by any pipeline script.

If you need to double-check a claim in the current docs against the
original source material, it's all still here — just `git log --follow`
on the file if you need to see where it lived before.
