# Knowledge Pack Contract

The outputs below are the **only** interface between track-knowledge and the Shiftwright platform
(`../Project_Shiftwright`, read via `SHIFTWRIGHT_TRACK_KNOWLEDGE`). Changing a field is a breaking change:
update the platform's `KnowledgePackImportService` / `TrackKnowledgeStore` in the same change.

All coordinates are SVG space (`viewBox 0 0 1920 1080`) of `racing-track-maps-vector`.
`lap_pct` is iRacing `LapDistPct`: 0 at the start/finish line, increasing in race direction.

## `generated/centrelines/<track_id>.csv`

`lap_pct,x,y`, 1025 rows, first row == last row (closed loop).
Built by `src/pipelines/build_centreline_library.py` from `axes_normalized/` + `start-finish.svg` + `turns.svg`.

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
| `named_corners[]` | `{name, start_pct, end_pct, labels[], ...}`; `labels` = turns inside the range (empty if direction unknown) |
| `generated_corner_regions[]` | Curvature-detected `{start_pct, apex_pct, end_pct, strength}` |
| `youtube_summary`, `turn_consensus` | YouTube enrichment (sparse) |

## Rebuild order

```text
build_track_catalog → build_axis_library → normalize_axis_library → build_centreline_library
  → (corner pipeline, see DATA_FLOW_DIAGRAM.md) → build_track_knowledge_pack
```

Then in the platform: `python scripts/import_knowledge_packs.py`.
