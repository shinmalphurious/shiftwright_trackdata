# Car Knowledge Contract

Car-specific knowledge for the platform's AI coach, from the **official iRacing car manuals**.
Read by the platform's `src/coaching/knowledge/car_knowledge.py`.

## Source

`$SHIFTWRIGHT_DATA_ROOT/iracing-manuals/*.pdf` (iRacing's user manuals, kept outside git).

## Build

```text
python -m src.pipelines.build_car_knowledge
```

## `generated/car_knowledge/<slug>.json` (git-ignored: the text is iRacing's)

| Field | Meaning |
| --- | --- |
| `slug` | From the manual's file name, e.g. `mclaren-720s-gt3-v2` |
| `manual_file` | Source PDF |
| `title` | The manual's own car title, from its "CAR \| USER MANUAL" header, e.g. `MCLAREN 720S GT3` |
| `sections[]` | `{title, text}` as written: `INTRODUCTION`, `TECH SPECS`, `ADVANCED SETUP OPTIONS`, `SETUP TIPS`, ... Dash-display pages are left out |
| `extracted_at` | UTC time of extraction |

`generated/car_knowledge/index.json` lists every car: `{slug, title, manual_file, sections}`.

## `config/car_knowledge_aliases.json` (committed)

Exact iRacing session car name → slug, for cars whose manual title differs from the name iRacing
reports (e.g. `"McLaren 720S GT3 EVO": "mclaren-720s-gt3-v2"`). Other cars are matched by the
platform from the manual title: every model designation (a word with a digit, e.g. `720S`, `GT3`,
`F4`) must agree and one other word must match; otherwise the car has no knowledge (never a guess).

## What the coach receives

The platform sends a budgeted excerpt: tech specs, then passages on driver aids and controls (brake
bias, ABS, traction control, throttle shape, downshift protection), then passages naming the
session's track, then handling notes.
