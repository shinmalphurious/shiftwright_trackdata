import json
import urllib.request

with open(
    "generated/current_transcript_task.json",
    encoding="utf-8"
) as fp:

    task = json.load(fp)

video_id = task["video_id"]

print(
    "testing",
    video_id
)

url = input(
    "Paste direct caption URL: "
)

try:

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    data = urllib.request.urlopen(
        req,
        timeout=20
    ).read(500)

    print(
        "SUCCESS"
    )

    print(
        data[:200]
    )

except Exception as ex:

    print(
        "FAIL"
    )

    print(ex)
