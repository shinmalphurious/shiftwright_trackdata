import json

data = json.load(
    open(
        "generated/discovery_result.json",
        encoding="utf-8"
    )
)

for video in data["videos"]:

    if video.get("car"):
        continue

    print()
    print("TITLE")
    print(video["title"])

    print()
    print("DESCRIPTION")
    print(
        (
            video.get(
                "description",
                ""
            )[:300]
        )
    )
