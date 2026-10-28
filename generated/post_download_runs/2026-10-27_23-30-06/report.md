# Post-download run 2026-10-27 23:30

9 passed, 1 failed, 0 not run - 79.9 min

| # | Step | Result | Time | Log |
|---|------|--------|------|-----|
| 1 | Verify lap-guide transcripts | passed | 0s | [log](logs/01_verify.log) |
| 2 | Extract corner guidance (Ollama) | passed | 329s | [log](logs/02_extract.log) |
| 3 | Assign notes to corners | **FAILED** (exit 1) | 0s | [log](logs/03_enrich.log) |
| 4 | Telemetry coverage | passed | 0s | [log](logs/04_coverage.log) |
| 5 | Validate track knowledge | passed | 0s | [log](logs/05_validate.log) |
| 6 | Research corner facts | passed | 4104s | [log](logs/06_research.log) |
| 7 | Validate corner facts | passed | 4s | [log](logs/07_validate_facts.log) |
| 8 | Build corner guidance | passed | 353s | [log](logs/08_corner_guidance.log) |
| 9 | Build track knowledge packs | passed | 1s | [log](logs/09_knowledge_pack.log) |
| 10 | Import packs into Shiftwright | passed | 2s | [log](logs/10_import.log) |

## Failures

Fix the first failure first: later steps use its output, so they may have failed or run on stale data because of it. First failure: **Assign notes to corners**.

### Assign notes to corners

`E:\track-knowledge\.venv\Scripts\python.exe -m src.pipelines.enrich_corner_assignments`

Last 23 lines (full output in `logs/03_enrich.log`):

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 801, in <module>
    main()
    ~~~~^^
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 677, in main
    settings, applied = calibrate(raws, config, uncalibrated)
                        ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 581, in calibrate
    measured = calibration(raws, config, settings)["by_method"]
               ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 566, in calibration
    result = enrich(hidden, config, s)
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 421, in enrich
    aliases = alias_table(raw["track_id"], pack, config, [l for l, _ in turns])
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 201, in alias_table
    for phrase, (labels, conf, _) in alias_claims(track_id, pack, config, turn_labels).items()
                                     ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\track-knowledge\src\pipelines\enrich_corner_assignments.py", line 177, in alias_claims
    name = corner["name"].lower()
           ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'lower'
```

Re-run one step on its own with the command above, or the whole run with
`python -m src.pipelines.run_post_download`; finished work is kept.
