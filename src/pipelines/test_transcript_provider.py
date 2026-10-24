import json

from src.providers.provider_factory import (
    get_provider
)

config = json.load(
    open(
        "generated/transcript_provider.json",
        encoding="utf-8"
    )
)

provider = get_provider(
    config["provider"]
)

print(
    type(provider).__name__
)
