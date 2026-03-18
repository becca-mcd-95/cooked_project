from typing import Iterable, Tuple, List, Set


DEFAULT_CUISINES: Tuple[str, ...] = (
    "American",
    "British",
    "Chinese",
    "French",
    "Indian",
    "Italian",
    "Japanese",
    "Korean",
    "Mediterranean",
    "Mexican",
    "Spanish",
    "Thai",
    "Turkish",
    "Vegetarian",
    "Vegan",
    "Dessert",
)

DEFAULT_OCCASIONS: Tuple[str, ...] = (
    "Weeknight dinner",
    "Weekend brunch",
    "Hosting",
    "Party",
    "Family meal",
    "Date night",
    "Meal prep",
    "Quick snack",
    "Comfort meal",
    "Holiday",
)


def has_cjk(text: str) -> bool:
    """
    Returns True if the string contains any CJK (Chinese/Japanese/Korean) characters.
    Used to keep filter option labels English-only in the UI without mutating stored data.
    """
    for ch in text:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF  # CJK Unified Ideographs
            or 0x3400 <= code <= 0x4DBF  # CJK Unified Ideographs Extension A
            or 0x3040 <= code <= 0x30FF  # Hiragana + Katakana
            or 0xAC00 <= code <= 0xD7AF  # Hangul Syllables
        ):
            return True
    return False


def english_only(values: Iterable[str]) -> List[str]:
    return [v for v in values if v and not has_cjk(v)]


def merge_defaults(*, values: Iterable[str], defaults: Iterable[str], limit: int) -> List[str]:
    """
    Merge a dynamic list with defaults, de-duplicated (case-insensitive), preserving order.
    """
    merged: List[str] = []
    seen: Set[str] = set()

    def add(v: str) -> None:
        key = v.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        merged.append(v)

    for v in values:
        if len(merged) >= limit:
            break
        add(v)

    for v in defaults:
        if len(merged) >= limit:
            break
        add(v)

    return merged
