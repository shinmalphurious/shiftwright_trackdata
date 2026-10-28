# Knowledge Pack Contract

The outputs below are the **only** interface between track-knowledge and the Shiftwright platform
(`../Project_Shiftwright`, read via `SHIFTWRIGHT_TRACK_KNOWLEDGE`). Changing a field is a breaking change:
update the platform's `KnowledgePackImportService` / `TrackKnowledgeStore` in the same change.

All coordinates are SVG space (`viewBox 0 0 1920 1080`) of `racing-track-maps-vector`.
`lap_pct` is iRacing `LapDistPct`: 0 at the start/finish line, increasing in race direction.

## `generated/centrelines/<track_id>.csv`

`lap_pct,x,y`, 1025 rows, first row == last row (closed loop).
Built by `src/pipelines/build_centreline_library.py` from `axes_normalized/` + `start-finish.svg` + `turns.svg`.
The axis is the centre of the active.svg ribbon (`src/geometry/ribbon_axis.py`, since 2026-10-26): even-odd
fill of the outer and inner outlines, spur pruning, a heading-following loop trace and 15 px smoothing. It is
published only when at most 2 % of its points lie off the ribbon and it covers 95 % of it (393 of 424
layouts; the other 31 keep their previous axis, flagged in `centreline_check`). Checked against GPS laps:
Spa 6.6 m, Red Bull Ring 4.5 m, Le Mans 11.7 m median (the previous axes: 169 m, 5.3 m, 14.6 m).

## `generated/turn_markers/<track_id>.json`

```json
{"track_id": 403, "direction_known": true,
 "turns": [{"label": "T1", "number": 1, "x": 881.4, "y": 921.9, "lap_pct": 0.1133}]}
```

`direction_known` is false when fewer than 3 numbered turns exist or both directions score equally.

## `generated/knowledge_packs/<track_id>.json`

| Field | Meaning |
| --- | --- |
| `track_id` | iRacing track id |
| `knowledge_level` | `named` (has named corners) or `geometry_only` |
| `metadata` | `{name, length_m}` (may be empty) |
| `direction_known`, `turns` | Copied from turn markers |
| `centreline_check` | `{method, off_track_share, coverage, ok}` from `generated/axes/axis_quality.json`; `ok: false` means the centreline is approximate for this layout |
| `named_corners[]` | `{name, start_pct, end_pct, labels[], ...}`; `labels` = turns inside the range (empty if direction unknown) |
| `generated_corner_regions[]` | Curvature-detected `{start_pct, apex_pct, end_pct, strength}` |
| `youtube_summary`, `turn_consensus` | Old keyword counts from YouTube (3 tracks; superseded by `corner_guidance`) |
| `corner_facts` | `{"T1": [{claim, statement, confidence, basis, evidence: {research, transcript, telemetry_laps, variants}, explanation, source_track?, source_corner?, inheritance_confidence?}]}`: consensus-approved facts only, from `generated/knowledge/validated/` (`basis` is `consensus` or `inherited`). Research candidates never appear here. The platform maps claims to `corner_type` / `brake_type` / `importance` (`HEAVY_BRAKING`, `FLAT_OUT`, `HAIRPIN`, `CHICANE`, `SLOW`, `FAST`, importance `HIGH`) on rows it owns and reports disagreements with hand-written rows as `curated_conflicts`. |
| `corner_guidance` | `{"T3": {name, videos, cars[], notes_by_method, tip, braking\|gear\|line\|exit\|mistakes: [{text, videos, cars[], confidence, methods[]}]}}`; `confidence` 1.0 = the speaker named the corner, lower = placed by `enrich_corner_assignments` (alias, telemetry, sequence or lap position) per-turn driving instructions from lap-guide videos (`build_corner_guidance`); statements ordered by how many videos agree. The platform writes `tip` to `coaching_tip` and the statements to `description`. |

## Rebuild order

```text
build_track_catalog → build_axis_library → normalize_axis_library → build_centreline_library
  → (corner pipeline, see DATA_FLOW_DIAGRAM.md) → build_track_knowledge_pack
```

Corner guidance (needs a local Ollama, default model `qwen2.5:14b`, override with `OLLAMA_MODEL`):

```text
verify_lap_guide_transcripts → extract_corner_guidance → enrich_corner_assignments
  → build_corner_guidance → build_track_knowledge_pack (runs validate_track_knowledge first)
```

The platform import withdraws guidance it wrote earlier for corners the pack no longer has guidance for.

Then in the platform: `python scripts/import_knowledge_packs.py`.
