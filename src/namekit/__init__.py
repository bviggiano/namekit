"""namekit: deterministic pop-culture name generator."""

from __future__ import annotations

from namekit._core import (
    CASES,
    NAME_PARTS,
    Case,
    NameKit,
    NamePart,
    format_name,
    list_entities,
    list_names,
    name,
    name_from_mapping,
    to_key,
)
from namekit._data import (
    AFFILIATIONS,
    ENTITIES,
    ENTITY_TYPES,
    FRANCHISES,
    Affiliation,
    Entity,
    EntityType,
)

__version__ = "0.1.3"
__all__ = [
    "AFFILIATIONS",
    "Affiliation",
    "CASES",
    "Case",
    "ENTITIES",
    "ENTITY_TYPES",
    "Entity",
    "EntityType",
    "FRANCHISES",
    "NAME_PARTS",
    "NameKit",
    "NamePart",
    "__version__",
    "format_name",
    "list_entities",
    "list_names",
    "name",
    "name_from_mapping",
    "to_key",
]
