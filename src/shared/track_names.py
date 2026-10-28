"""Track name cleanup and comparison.

The iRacing track metadata stores accented names double-encoded ("AutÃ³dromo Hermanos
RodrÃ­guez" for "Autódromo Hermanos Rodríguez"): UTF-8 bytes that were decoded as Latin-1
before being saved. repair() undoes that. normalize() turns any name or video title into a
form that compares equal regardless of case, accents, punctuation and spacing.
"""
import json
import re
import unicodedata
from functools import lru_cache

from src.shared.paths import REPO_ROOT

ALIASES = REPO_ROOT / "config" / "track_aliases.json"

# A UTF-8 lead byte read as Latin-1/CP1252 followed by a continuation byte. Only a hint: repair()
# keeps the text unless re-encoding it gives valid UTF-8, which correctly accented text does not.
_MOJIBAKE = re.compile("[Â-ßâ][\u0080-¿Œ-Ÿƒˆ˜–-™]")


def repair(text):
    """Undo UTF-8 text that was decoded as Latin-1 or CP1252. Clean text is returned unchanged."""
    if not text or not _MOJIBAKE.search(text):
        return text
    for codec in ("cp1252", "latin-1"):
        try:
            return text.encode(codec).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return text


def fold(text):
    """Repaired text with accents removed: 'Autódromo' -> 'Autodromo'. Case is kept."""
    text = unicodedata.normalize("NFKD", repair(text or ""))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.replace("­", "").replace("ß", "ss").replace("ø", "o").replace("Ø", "O")


def normalize(text):
    """Lowercase, no accents, punctuation as spaces, single spaces: the form names are compared in.

    normalize("Autódromo  Hermanos Rodríguez") == normalize("autodromo hermanos-rodriguez")
    """
    return " ".join(re.findall(r"[a-z0-9]+", fold(text).casefold()))


def squash(text):
    """normalize() without spaces, for names written as one word ('MexicoCity')."""
    return normalize(text).replace(" ", "")


def contains_phrase(normalized_text, phrase):
    """Whether a phrase appears in normalized text as whole words."""
    phrase = normalize(phrase)
    return bool(phrase) and f" {phrase} " in f" {normalized_text} "


@lru_cache(maxsize=1)
def _alias_table():
    if not ALIASES.exists():
        return {}
    data = json.loads(ALIASES.read_text(encoding="utf-8"))
    return {normalize(venue): entry for venue, entry in data.get("venues", {}).items()}


def aliases(venue):
    """Curated other names for a venue, from config/track_aliases.json.

    Returns (strong, weak): strong aliases identify the venue on their own and are also searched
    for; weak ones ('Mexico') only add confidence to a title that already looks like a guide.
    """
    entry = _alias_table().get(normalize(venue), {})
    return list(entry.get("aliases", [])), list(entry.get("weak_aliases", []))
