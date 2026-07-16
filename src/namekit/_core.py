"""Deterministic key-to-name mapping with filtering and format options."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, Literal

from namekit._data import (
    AFFILIATIONS,
    ENTITIES,
    ENTITY_TYPES,
    FRANCHISES,
    Affiliation,
    Entity,
    EntityType,
)

NamePart = Literal["first", "last", "full"]
Case = Literal["snake", "title", "compact", "kebab"]

NAME_PARTS: tuple[NamePart, ...] = ("first", "last", "full")
CASES: tuple[Case, ...] = ("snake", "title", "compact", "kebab")


def _as_set(value: str | Iterable[str] | None) -> set[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return {value}
    return set(value)


def _validate(field: str, allowed: tuple[str, ...], values: set[str] | None) -> None:
    if values is None:
        return
    bad = values - set(allowed)
    if bad:
        raise KeyError(f"Unknown {field}: {sorted(bad)}. Allowed: {list(allowed)}")


_PUNCT_STRIP = re.compile(r"[‘’']")  # apostrophes
_SEP_RUN = re.compile(r"[\s\-]+")  # internal whitespace and hyphens


def _slug(part: str, sep: str) -> str:
    """Lowercase a part; convert internal whitespace/hyphens to `sep`.

    Apostrophes and any remaining non-alphanumerics are stripped. When `sep`
    is the empty string ("compact" case), all separators collapse to nothing.
    """
    s = _PUNCT_STRIP.sub("", part.lower())
    s = _SEP_RUN.sub(sep, s)
    if sep:
        s = re.sub(rf"[^a-z0-9{re.escape(sep)}]", "", s)
    else:
        s = re.sub(r"[^a-z0-9]", "", s)
    return s


def format_name(
    entity: Entity,
    *,
    name_part: NamePart = "full",
    case: Case = "snake",
) -> str:
    """Format an Entity into a string per the chosen name_part and case.

    Raises ValueError if name_part is "last" but the entity has no last name.
    """
    if name_part == "first":
        selected: tuple[str, ...] = (entity.parts[0],)
    elif name_part == "last":
        if entity.last is None:
            raise ValueError(
                f"Entity {entity.parts!r} has no last name; "
                "cannot format with name_part='last'."
            )
        selected = (entity.last,)
    elif name_part == "full":
        selected = entity.parts
    else:
        raise ValueError(
            f"Unknown name_part: {name_part!r}. Allowed: {list(NAME_PARTS)}"
        )

    if case == "title":
        return " ".join(selected)
    sep_for_case = {"snake": "_", "kebab": "-", "compact": ""}
    if case not in sep_for_case:
        raise ValueError(f"Unknown case: {case!r}. Allowed: {list(CASES)}")
    sep = sep_for_case[case]
    cleaned = [_slug(p, sep) for p in selected]
    return sep.join(cleaned)


def _filter_entities(
    franchise: str | Iterable[str] | None,
    entity_type: str | Iterable[str] | None,
    affiliation: str | Iterable[str] | None,
    name_part: NamePart,
) -> list[Entity]:
    franchises = _as_set(franchise)
    entity_types = _as_set(entity_type)
    affiliations = _as_set(affiliation)

    _validate("franchise", FRANCHISES, franchises)
    _validate("entity_type", ENTITY_TYPES, entity_types)
    _validate("affiliation", AFFILIATIONS, affiliations)

    out = []
    for e in ENTITIES:
        if franchises is not None and e.franchise not in franchises:
            continue
        if entity_types is not None and e.entity_type not in entity_types:
            continue
        if affiliations is not None and e.affiliation not in affiliations:
            continue
        if name_part == "last" and e.last is None:
            continue
        out.append(e)
    return out


def _select_corpus(
    franchise: str | Iterable[str] | None,
    entity_type: str | Iterable[str] | None,
    affiliation: str | Iterable[str] | None,
    name_part: NamePart,
    case: Case,
) -> list[str]:
    if name_part not in NAME_PARTS:
        raise ValueError(
            f"Unknown name_part: {name_part!r}. Allowed: {list(NAME_PARTS)}"
        )
    if case not in CASES:
        raise ValueError(f"Unknown case: {case!r}. Allowed: {list(CASES)}")

    seen: set[str] = set()
    out: list[str] = []
    for e in _filter_entities(franchise, entity_type, affiliation, name_part):
        formatted = format_name(e, name_part=name_part, case=case)
        if formatted in seen:
            continue
        seen.add(formatted)
        out.append(formatted)
    return out


def _digest(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (set, frozenset)):
        return sorted(obj, key=repr)
    return str(obj)


def to_key(mapping: Mapping[str, Any], *, exclude: Iterable[str] = ()) -> str:
    """Serialize a mapping to a canonical, stable string key.

    The key is order-independent (keys are sorted at every level) and
    whitespace-free, so equal mappings always produce the same key across
    processes and machines. Sets are sorted; other non-JSON values fall back
    to ``str``. Top-level keys in ``exclude`` are dropped before serializing.

    Args:
        mapping: The mapping to serialize (e.g. a config dumped to a dict).
        exclude: Top-level keys to omit from the key.

    Returns:
        A compact, deterministic JSON string.
    """
    excluded = set(exclude)
    data = {k: v for k, v in mapping.items() if k not in excluded}
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), default=_json_default
    )


def name_from_mapping(
    mapping: Mapping[str, Any], *, exclude: Iterable[str] = (), **kwargs: Any
) -> str:
    """Map a mapping to a name via its canonical key (see :func:`to_key`).

    The same mapping (ignoring ``exclude`` keys) always yields the same name,
    which makes it convenient for naming runs or experiments straight from a
    config dumped to a dict.

    Args:
        mapping: The mapping to name.
        exclude: Top-level keys to omit from the key.
        **kwargs: Forwarded to :func:`name` (``franchise``, ``case``,
            ``suffix``, ...).

    Returns:
        A formatted entity name (see :func:`name`).
    """
    return name(to_key(mapping, exclude=exclude), **kwargs)


def name(
    key: str,
    *,
    franchise: str | Iterable[str] | None = None,
    entity_type: EntityType | Iterable[EntityType] | None = None,
    affiliation: Affiliation | Iterable[Affiliation] | None = None,
    name_part: NamePart = "full",
    case: Case = "snake",
    suffix: bool = False,
    suffix_length: int = 5,
    separator: str = "_",
) -> str:
    """Map a string key to a pop-culture entity name, deterministically.

    The mapping is stable across processes, machines, and Python versions
    because it uses SHA-256 rather than the salted built-in hash().

    Args:
        key: Arbitrary string used as the lookup key.
        franchise: Restrict to one or more franchises (e.g., "lotr").
        entity_type: Restrict to "character", "place", or both.
        affiliation: Restrict to "good", "bad", "neutral", or any combination.
        name_part: Which slice of the name to return ("first", "last", "full").
            "last" filters out entities that have no last name.
        case: Output casing ("snake", "title", "compact", "kebab").
        suffix: If True, append a short hex digest of the key for uniqueness.
        suffix_length: Number of hex characters in the suffix.
        separator: String placed between the name and the suffix.

    Returns:
        A formatted entity name, optionally followed by a hash suffix.
    """
    corpus = _select_corpus(franchise, entity_type, affiliation, name_part, case)
    if not corpus:
        raise ValueError("Selected corpus is empty for the given filters.")

    digest = _digest(key)
    chosen = corpus[int(digest, 16) % len(corpus)]

    if suffix:
        return f"{chosen}{separator}{digest[:suffix_length]}"
    return chosen


def list_names(
    *,
    franchise: str | Iterable[str] | None = None,
    entity_type: EntityType | Iterable[EntityType] | None = None,
    affiliation: Affiliation | Iterable[Affiliation] | None = None,
    name_part: NamePart = "full",
    case: Case = "snake",
) -> list[str]:
    """Return the deduplicated list of formatted names matching the filters."""
    return _select_corpus(franchise, entity_type, affiliation, name_part, case)


def list_entities(
    *,
    franchise: str | Iterable[str] | None = None,
    entity_type: EntityType | Iterable[EntityType] | None = None,
    affiliation: Affiliation | Iterable[Affiliation] | None = None,
    name_part: NamePart = "full",
) -> list[Entity]:
    """Return Entity objects matching the filters (no formatting, no dedup).

    `name_part="last"` filters out entities without a last name.
    """
    return _filter_entities(franchise, entity_type, affiliation, name_part)


class NameKit:
    """Reusable namer bound to a fixed corpus and formatting choice.

    Construct once and call many times when the same configuration is reused
    across many keys (e.g., across rows in a dataset).
    """

    def __init__(
        self,
        franchise: str | Iterable[str] | None = None,
        *,
        entity_type: EntityType | Iterable[EntityType] | None = None,
        affiliation: Affiliation | Iterable[Affiliation] | None = None,
        name_part: NamePart = "full",
        case: Case = "snake",
        suffix: bool = False,
        suffix_length: int = 5,
        separator: str = "_",
    ) -> None:
        self._corpus = _select_corpus(
            franchise, entity_type, affiliation, name_part, case
        )
        if not self._corpus:
            raise ValueError("Selected corpus is empty for the given filters.")
        self.suffix = suffix
        self.suffix_length = suffix_length
        self.separator = separator

    def __call__(self, key: str) -> str:
        digest = _digest(key)
        chosen = self._corpus[int(digest, 16) % len(self._corpus)]
        if self.suffix:
            return f"{chosen}{self.separator}{digest[: self.suffix_length]}"
        return chosen

    @property
    def corpus(self) -> list[str]:
        return list(self._corpus)

    def __len__(self) -> int:
        return len(self._corpus)
