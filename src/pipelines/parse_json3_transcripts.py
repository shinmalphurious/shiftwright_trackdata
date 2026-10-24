import json
from pathlib import Path

for file in Path(
    "research/youtube/transcripts"
).glob("*.json"):

    try:

        data = json.load(
            open(
                file,
                encoding="utf-8"
            )
        )

        segments = []

        for event in data.get(
            "events",
            []
        ):

            text = ""

            for seg in event.get(
                "segs",
                []
            ):

                text += seg.get(
                    "utf8",
                    ""
                )

            if not text.strip():
                continue

            segments.append(
                {
                    "start":
                        event.get(
                            "tStartMs",
                            0
                        ) / 1000,

                    "text":
                        text.strip()
                }
            )

        outfile = (
            Path(
                "research/youtube/parsed_transcripts"
            )
            /
            file.name
        )

        json.dump(
            segments,
            open(
                outfile,
                "w",
                encoding="utf-8"
            ),
            indent=2
        )

        print(
            outfile.name
        )

    except Exception:

        pass
