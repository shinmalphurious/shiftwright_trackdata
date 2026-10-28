# Guide discovery refresh

Before: snapshot `generated\discovery_snapshots\20261027-195832`. After: current data.

| Metric | Before | After |
|---|---:|---:|
| Layouts with guides | 404 | 411 |
| Unique videos | 1,977 | 8,685 |
| Candidates (per layout) | 14,687 | 14,451 |
| Unique candidate videos | not recorded | 8,685 |
| Accepted guides (per layout) | not recorded | 6,104 |
| Unique accepted videos | not recorded | 3,432 |
| Selected guides (per layout) | 3,662 | 3,754 |
| Unique selected videos | 1,977 | 2,008 |

| Discovery delta | Count |
|---|---:|
| New videos (never seen before) | 6,695 |
| New candidates (per layout) | 10,789 |
| New accepted videos | 1,451 |
| New accepted guides (per layout) | 2,442 |
| New selections (per layout) | 92 |
| … of videos new to the system | 56 |
| … of videos already known (linked to another layout) | 36 |
| Candidates found only via aliases | 224 |
| … accepted | 172 |
| … selected | 13 |
| Candidates found due to metadata repair | 1,276 |
| … accepted | 383 |
| … selected | 22 |

## Mexico and Interlagos

| Layout | Before (cand / sel) | After (cand / acc / sel) | Queries |
|---|---:|---:|---:|
| 212 Autódromo José Carlos Pace - Grand Prix | 0 / 0 | 66 / 57 / 10 | 7/12 |
| 213 Autódromo José Carlos Pace - Moto | 0 / 0 | 76 / 59 / 10 | 7/12 |
| 572 Autódromo Hermanos Rodríguez - Grand Prix | 20 / 10 | 47 / 35 / 10 | 6/11 |
| 573 Autódromo Hermanos Rodríguez - Grand Prix Historic | 0 / 0 | 55 / 36 / 10 | 6/11 |
| 574 Autódromo Hermanos Rodríguez - National | 0 / 0 | 59 / 36 / 10 | 6/11 |
| 575 Autódromo Hermanos Rodríguez - National Historic | 0 / 0 | 51 / 36 / 10 | 6/11 |
| 576 Autódromo Hermanos Rodríguez - EV Circuit | 0 / 0 | 45 / 35 / 10 | 6/11 |
| 577 Autódromo Hermanos Rodríguez - Oval | 1 / 1 | 63 / 35 / 10 | 6/11 |
| 578 Autódromo Hermanos Rodríguez - Oval Stadium | 0 / 0 | 44 / 35 / 10 | 6/11 |

## Validation

| Check | Result |
|---|---|
| Unreadable catalog or ledger files | OK (0) |
| Catalog structure problems | OK (0) |
| Duplicate video ids within a layout's selection | OK (0) |
| Duplicate video ids in the transcript queue | OK (0) |
| Previous selections no longer selected | OK (0) |
| Manifest out of step with catalog | OK (0) |
| Downloaded transcripts no longer linked to a layout | OK (0) |
| Transcript queue items lost | OK (0) |
| Half-written files | OK (0) |
| Previous selections the v3 rules would reject (kept) | 13 |
