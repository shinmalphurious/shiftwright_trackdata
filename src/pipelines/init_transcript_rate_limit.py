import json

state = {
    "last_429": None,
    "global_pause_until": None
}

with open(
    "generated/transcript_rate_limit.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        state,
        fp,
        indent=2
    )

print("created")
