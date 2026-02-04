# metadata_utils.py
#
# Handles:
# - whitespace cleanup
# - title normalization
# - artist normalization
# - genre normalization
# - BPM extraction
# - key extraction
#
# Used by audio_reader.py to keep metadata clean and consistent.

import os


# ============================================================
# Whitespace cleanup
# ============================================================
def clean_whitespace(text: str | None) -> str | None:
    if not text:
        return None
    return " ".join(text.split()).strip()


# ============================================================
# Title normalization
# ============================================================
def normalize_title(title: str | None) -> str | None:
    if not title:
        return None

    title = clean_whitespace(title)

    # Remove common mix tags
    mix_tags = [
        "(Original Mix)",
        "(Extended Mix)",
        "(Radio Edit)",
        "(Club Mix)",
        "(Remix)",
    ]

    for tag in mix_tags:
        if title.endswith(tag):
            title = title[: -len(tag)].strip()

    return title


# ============================================================
# Artist normalization
# ============================================================
def normalize_artist(artist: str | None) -> str | None:
    if not artist:
        return None

    artist = clean_whitespace(artist)

    # Normalize "feat" variations
    replacements = {
        " feat. ": " feat ",
        " ft. ": " feat ",
        " Ft. ": " feat ",
        " Feat. ": " feat ",
        " featuring ": " feat ",
    }

    for old, new in replacements.items():
        artist = artist.replace(old, new)

    return artist


# ============================================================
# Genre normalization
# ============================================================
def normalize_genre(genre: str | None) -> str | None:
    if not genre:
        return None

    genre = clean_whitespace(genre).lower()

    mapping = {
        "r&b": "R&B",
        "rnb": "R&B",
        "hip hop": "Hip-Hop",
        "hip-hop": "Hip-Hop",
        "house": "House",
        "deep house": "Deep House",
        "tech house": "Tech House",
        "edm": "EDM",
        "pop": "Pop",
        "rock": "Rock",
    }

    return mapping.get(genre, genre.title())


# ============================================================
# BPM extraction
# ============================================================
def extract_bpm(tags) -> int | None:
    if not tags:
        return None

    for key in ["TBPM", "bpm", "BPM"]:
        if key in tags:
            value = tags[key]
            if isinstance(value, list):
                value = value[0]

            try:
                return int(round(float(str(value).strip())))
            except Exception:
                return None

    return None


# ============================================================
# Key extraction
# ============================================================
def extract_key(tags) -> str | None:
    if not tags:
        return None

    for key in ["TKEY", "initialkey", "INITIALKEY", "key", "KEY"]:
        if key in tags:
            value = tags[key]
            if isinstance(value, list):
                value = value[0]

            value = str(value).strip()
            return value or None

    return None


# ============================================================
# Genre extraction
# ============================================================
def extract_genre(tags) -> str | None:
    if not tags:
        return None

    for key in ["TCON", "genre", "GENRE"]:
        if key in tags:
            value = tags[key]
            if isinstance(value, list):
                value = value[0]

            value = str(value).strip()
            return value or None

    return None


# ============================================================
# Title extraction (fallback to filename)
# ============================================================
def extract_title(tags, filepath: str) -> str | None:
    if tags:
        for key in ["TIT2", "title", "TITLE"]:
            if key in tags:
                value = tags[key]
                if isinstance(value, list):
                    value = value[0]
                value = str(value).strip()
                if value:
                    return value

    # Fallback: filename without extension
    base = os.path.basename(filepath)
    name, _ = os.path.splitext(base)
    return name.strip() or None


# ============================================================
# Artist extraction
# ============================================================
def extract_artist(tags) -> str | None:
    if not tags:
        return None

    for key in ["TPE1", "artist", "ARTIST"]:
        if key in tags:
            value = tags[key]
            if isinstance(value, list):
                value = value[0]
            value = str(value).strip()
            if value:
                return value

    return None



