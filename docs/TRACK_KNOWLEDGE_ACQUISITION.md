> **2026-10-24 note:** kept as the clearest status snapshot of the
> acquisition subsystem. Numbers below (guides catalogued, queue depth,
> percentage-complete assessment) are a point-in-time snapshot, already
> somewhat stale — e.g. the transcript queue now shows 55 ready / 14
> downloaded / 9 claimed, not the ~76 ready_for_download recorded here,
> and the HTTP 429 caption-download block described below is not
> currently active (checked `generated/transcript_rate_limit.json`). The
> *shape* of the system and the "transport is the real bottleneck, not
> discovery" conclusion are still accurate. Re-check current numbers with
> the commands in `TRANSCRIPT_TRANSPORT_STATUS.txt` before trusting the
> figures below. See `DEPENDENCY_MAP.md` and `DATA_FLOW_DIAGRAM.md` for
> the verified current pipeline shape.

Current Objective

Build a reusable, shareable repository of:

Track
↓
Vehicle
↓
Guide Knowledge
↓
Future Transcript Knowledge


without hard-coding any preference for GT3, MX5, NASCAR, etc.

The repository should answer:

Where does knowledge exist?


rather than:

What should Jacob drive?

Current State
Discovery

Status:

WORKING


Pipeline:

claim_next_track
↓
build_search_payload
↓
build_discovery_task
↓
run_discovery_provider
↓
select_best_guides
↓
store_selected_guides
↓
archive_discovery_selection


Results:

guides_catalogued > 45
pending_search > 400

Guide Catalog

Location:

generated/guide_catalog


Contains:

{
  "track_id": 8,
  "layout": "8-summit-jefferson",

  "selected_guides": {
    "mx5": [...],
    "ff1600": [...],
    "vee": [...]
  }
}


Purpose:

Permanent guide inventory

Guide Discovery (run_guide_discovery, version 3)

- Track names come only from src/shared/iracing_tracks.py, which repairs the metadata's
  double-encoded accents ("AutÃ³dromo" -> "Autódromo"). Never read the metadata file directly.
- Names and titles are compared normalised (case, accents, punctuation, spacing; src/shared/track_names.py).
- config/track_aliases.json lists other names a venue goes by ("Mexico City" for Autódromo
  Hermanos Rodríguez). Aliases are searched for and count as a full venue match.
- A title's venue match is a confidence (0..1), not an exact match; rejected candidates carry a reason.
- A video is identified only by its YouTube id. Previously selected videos stay selected (their
  transcripts stay linked); every candidate seen is kept in `generated/guide_candidates/<id>.json`
  and re-evaluated on the next run; new videos fill the selection up to 10.
- Each run first copies the catalog, candidates, manifest and transcript queue to
  `generated/discovery_snapshots/<timestamp>/`. report_discovery_refresh compares the current state
  with a snapshot and validates it (duplicates, lost selections, manifest, transcript links).
- --debug writes every query, candidate, confidence and rejection reason to
  `generated/guide_discovery_debug/<id>.json`.

Vehicle Classification

Source:

data/vehicle_aliases.json
generated/vehicle_lookup.json


Examples:

mx5
ff1600
vee
usf2000
bmw_m2
nascar
late_model
modified
rallycross_beetle
pro_lite_2

Discovery Effectiveness

Location:

generated/discovery_effectiveness.json


Outputs:

Track
Cars
Guides


Example:

Track 8
Cars: 5
Guides: 6

Track 9
Cars: 4
Guides: 8

Knowledge Backlog

Location:

generated/knowledge_backlog.json


Purpose:

Rank tracks by discovery richness


Example:

Track 9
Priority 32

Track 8
Priority 30

Track 114
Priority 24


Formula:

priority = guides × cars

Transcript System
Queue

Location:

generated/transcript_queue.json


Current:

~76 ready_for_download


Structure:

{
  "track_id": 101,
  "car": "nascar",
  "video_id": "...",
  "status": "ready_for_download"
}

Transcript Worker

Pipeline:

claim_next_transcript
↓
attempt_transcript_download

Backoff

Location:

src/shared/transcript_backoff.py


Schedule:

30 min
120 min
360 min
720 min
1440 min

Global Failsafe

Location:

generated/transcript_rate_limit.json


Example:

{
  "last_429": "...",
  "global_pause_until": "..."
}


Behavior:

429
↓
Pause entire transcript system
↓
Retry later

Caption System
Metadata

Status:

WORKING


We have confirmed:

automatic_captions


exist.

Available formats:

json3
vtt
srv1
srv2
srv3
ttml
srt

Download

Status:

BLOCKED


Current outcome:

HTTP 429


Observed for:

youtube_transcript_api
yt-dlp subtitle downloads
direct timedtext URLs

Important Conclusion

Current state:

Captions Exist
✅

Caption Metadata Accessible
✅

Caption Download
❌


The bottleneck is:

Caption Transport


NOT:

Discovery
Classification
Cataloguing
State Machine

What We Are Collecting Today

Current repository value:

Track
↓
Vehicle
↓
Guide Inventory


Examples:

MX5
FF1600
Formula Vee
BMW M2
Late Model
Modified
NASCAR
Rallycross Beetle

What We Are NOT Collecting Yet

Not currently successful:

Subtitles
Transcripts
Turn Facts
Knowledge Packs From New Guides


because transcript retrieval remains blocked.

Immediate Next Priority

Continue:

Discovery
↓
Guide Catalog
↓
Guide Coverage


while transcript retrieval remains paused.

The repository already contains valuable:

Track
+
Vehicle
+
Guide Coverage


knowledge even without captions.

Future Phase

Once caption transport succeeds:

Guide
↓
json3 Transcript
↓
Parsed Transcript
↓
Turn Segments
↓
Turn Facts
↓
Track Knowledge
↓
Knowledge Pack


All infrastructure required for that phase is already in place.

Current Assessment
Discovery Engine        95%
Guide Catalog          95%
Vehicle Classification 85%
Transcript Queue       95%
Transcript Transport   10%
Knowledge Extraction   40%


The remaining blocker is:

Reliable Caption Download


Everything else is operational.