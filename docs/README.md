# Documentation Index

Ten active documents, last reconciled against the actual codebase on
2026-10-24. Read them in this order:

| # | Document | What it's for |
|---|---|---|
| 1 | [`SYSTEM_OVERVIEW.md`](SYSTEM_OVERVIEW.md) | Start here. Beginner-friendly explanation of what this repo does and its three subsystems. |
| 2 | [`ONE_PAGE_ARCHITECTURE.md`](ONE_PAGE_ARCHITECTURE.md) | A single diagram: active / dead / experimental / required-to-rebuild, at a glance. |
| 3 | [`COMPONENT_CATALOG.md`](COMPONENT_CATALOG.md) | Every module and folder, what it does, and its status (active/dead/orphan/archived). |
| 4 | [`DATA_FLOW_DIAGRAM.md`](DATA_FLOW_DIAGRAM.md) | How data actually moves between scripts, traced from code — not from intent. |
| 5 | [`DEPENDENCY_MAP.md`](DEPENDENCY_MAP.md) | Import graph, file-level dependencies, external dependencies, and concrete fragility risks. |
| 6 | [`Cleanup_plan.md`](Cleanup_plan.md) | The 11-phase stabilization roadmap — what to do, in what order. |
| 7 | [`NEXT_STEPS.md`](NEXT_STEPS.md) | Concrete current priorities and open questions (has a correction note at the top — read it). |
| 8 | [`TRACK_KNOWLEDGE_ACQUISITION.md`](TRACK_KNOWLEDGE_ACQUISITION.md) | Status snapshot of the acquisition subsystem specifically — discovery/guide-catalog/transcript-queue completion %, and why transport (not discovery) is the real bottleneck. Numbers are stale; shape is accurate. |
| 9 | [`TRANSCRIPT_TRANSPORT_STATUS.txt`](TRANSCRIPT_TRANSPORT_STATUS.txt) | Operational notes on running the transcript downloader, the exact commands to check queue/rate-limit health, and the known HTTP 429 history. Numbers are stale — re-run the commands in it for today's real state. |
| 10 | [`DISCOVERY_RESULT_SCHEMA.json`](DISCOVERY_RESULT_SCHEMA.json) | The expected shape of a video-discovery result record. Small reference, not prose — keep as-is. |
| 11 | [`KNOWLEDGE_PACK.md`](KNOWLEDGE_PACK.md) | **The contract with the Shiftwright platform**: centrelines, turn markers, knowledge packs, rebuild order. |
| 12 | [`CENTRELINE_INVESTIGATION.md`](CENTRELINE_INVESTIGATION.md) | Evidence for the skeleton centreline method (moved from the platform repo). |

## Everything else has moved

Older architecture notes, source-evaluation brainstorms, stale count
snapshots, and an ad-hoc audit-commands dump were archived to
[`archive/docs/`](../archive/docs/README.md) on 2026-10-24 — each one superseded
by a document in the table above. They're not deleted, just out of the
way so they don't get loaded by default. See `archive/docs/README.md`
for exactly what moved and why.

## Keeping this current

The five numbered documents (2–5, plus this index) describe what the
codebase *is*. They go stale the same way any documentation does — if
you add, remove, or rewire a pipeline stage, update the matching
section rather than letting it drift. `Cleanup_plan.md` and
`NEXT_STEPS.md` describe what to do *next*; update those as priorities
actually shift, and strike through phases as they're completed.
