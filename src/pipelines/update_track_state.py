import json
import sys

if len(sys.argv) < 4:

    print(
        "usage: track_id field value"
    )

    raise SystemExit

track_id = int(sys.argv[1])

field = sys.argv[2]

value = sys.argv[3]

manifest_path = (
    "generated/track_acquisition_manifest.json"
)

manifest = json.load(
    open(
        manifest_path,
        encoding="utf-8"
    )
)

updated = False

for track in manifest:

    if track["track_id"] != track_id:
        continue

    if field == "youtube.video_id":

        if "video_ids" not in track["youtube"]:
            track["youtube"]["video_ids"] = []

        if value not in track["youtube"]["video_ids"]:

            track["youtube"]["video_ids"].append(
                value
            )

        track["youtube"]["videos_found"] = len(
            track["youtube"]["video_ids"]
        )

        if track["youtube"]["videos_found"] > 0:
            track["state"] = "videos_found"

    elif "." in field:

        left,right = field.split(
            ".",
            1
        )

        if left not in track:
            track[left] = {}

        try:
            value = int(value)
        except:
            pass

        track[left][right] = value

    else:

        track[field] = value

    updated = True

    break

with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        manifest,
        fp,
        indent=2
    )

print(
    "updated:",
    updated
)
