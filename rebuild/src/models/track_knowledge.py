from dataclasses import dataclass

@dataclass
class TrackFact:
    category: str
    value: str
    source: str
    confidence: str = "manual"


@dataclass
class TrackKnowledge:
    track_id: int
    track_name: str
    source: str
    facts: list
