# Post-download run 2026-10-27 21:53

8 passed, 2 failed, 0 not run - 73.4 min

| # | Step | Result | Time | Log |
|---|------|--------|------|-----|
| 1 | Verify lap-guide transcripts | passed | 0s | [log](logs/01_verify.log) |
| 2 | Extract corner guidance (Ollama) | **FAILED** (exit 1) | 12s | [log](logs/02_extract.log) |
| 3 | Assign notes to corners | passed | 9s | [log](logs/03_enrich.log) |
| 4 | Telemetry coverage | passed | 0s | [log](logs/04_coverage.log) |
| 5 | Validate track knowledge | passed | 0s | [log](logs/05_validate.log) |
| 6 | Research corner facts | passed | 4374s | [log](logs/06_research.log) |
| 7 | Validate corner facts | **FAILED** (exit 1) | 3s | [log](logs/07_validate_facts.log) |
| 8 | Build corner guidance | passed | 2s | [log](logs/08_corner_guidance.log) |
| 9 | Build track knowledge packs | passed | 1s | [log](logs/09_knowledge_pack.log) |
| 10 | Import packs into Shiftwright | passed | 2s | [log](logs/10_import.log) |

## Failures

Fix the first failure first: later steps use its output, so they may have failed or run on stale data because of it. First failure: **Extract corner guidance (Ollama)**.

### Extract corner guidance (Ollama)

`E:\track-knowledge\.venv\Scripts\python.exe -m src.pipelines.extract_corner_guidance`

Last 16 lines (full output in `logs/02_extract.log`):

```text
transcripts to extract: 31  model: qwen2.5:14b
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\track-knowledge\src\pipelines\extract_corner_guidance.py", line 310, in <module>
    main()
    ~~~~^^
  File "E:\track-knowledge\src\pipelines\extract_corner_guidance.py", line 297, in main
    result = extract(video_id, queue[video_id], args.model)
  File "E:\track-knowledge\src\pipelines\extract_corner_guidance.py", line 225, in extract
    allowed = {f"T{n}" for n in turns_said(context)} | names_said(context, names)
                                                       ~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "E:\track-knowledge\src\pipelines\extract_corner_guidance.py", line 161, in names_said
    for part in re.split(r"[/&]| and ", name.lower()):
                                        ^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'lower'
```

### Validate corner facts

`E:\track-knowledge\.venv\Scripts\python.exe -m src.pipelines.validate_knowledge_candidates`

Last 10 lines (full output in `logs/07_validate_facts.log`):

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "E:\track-knowledge\src\pipelines\validate_knowledge_candidates.py", line 285, in <module>
    main()
    ~~~~^^
  File "E:\track-knowledge\src\pipelines\validate_knowledge_candidates.py", line 219, in main
    own_evidence = record["counts"]["telemetry"] == "confirm" or record["counts"]["transcript_confirmations"]
                   ~~~~~~^^^^^^^^^^
KeyError: 'counts'
```

Re-run one step on its own with the command above, or the whole run with
`python -m src.pipelines.run_post_download`; finished work is kept.
