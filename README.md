# namekit

Deterministic pop-culture name generator. Map any string key to a stable,
memorable name. Filter by franchise, entity type, or affiliation; choose how
the name is formatted.

```bash
pip install namekit
```

```python
import namekit

namekit.name("user-42")                              # 'fred_weasley'
namekit.name("user-42", franchise="lotr")            # 'gollum'
namekit.name("user-42", case="title")                # 'Fred Weasley'
namekit.name("user-42", name_part="last")            # 'weasley'
namekit.name("user-42", suffix=True)                 # 'fred_weasley_6d894'
```

The same key always produces the same name. The mapping is stable across
processes, machines, and Python versions because it uses SHA-256 rather than
Python's salted built-in `hash()`.

## Install

```bash
pip install namekit
```

Or, from source:

```bash
pip install -e .
```

## Why namekit?

Common use cases:

- Naming training runs, experiments, or sweeps from a config hash, so the same
  config always lands on the same name.
- Generating friendly identifiers for users, sessions, or test fixtures.
- Replacing opaque hashes with human-readable labels in logs and dashboards.

## Filtering

Three independent filters compose freely.

Each filter accepts a single value, a list/tuple of values, or `None`
(no filter).

| Filter        | Values                                                                                  |
| ------------- | --------------------------------------------------------------------------------------- |
| `franchise`   | one or more from `FRANCHISES`, e.g., `"lotr"` or `["lotr", "ghibli"]`                   |
| `entity_type` | one or more of `"character"`, `"place"`, e.g., `"place"` or `["character", "place"]`    |
| `affiliation` | one or more of `"good"`, `"bad"`, `"neutral"`, e.g., `["good", "neutral"]` (no villains)|

```python
from namekit import name, list_names

# A villain from Game of Thrones (rendered Title Case)
name("user-1", franchise="got", affiliation="bad", case="title")
# 'Petyr Baelish'

# LOTR strongholds (the bad guys' places)
list_names(franchise="lotr", entity_type="place", affiliation="bad", case="title")
# ['Mordor', 'Isengard', 'Mount Doom']

# Disney villains
list_names(franchise="disney", affiliation="bad", case="title")
# ['Scar', 'Ursula', 'Gaston', 'Jafar']
```

If a filter combination yields no entries (e.g., bad scientists), `name()`
raises `ValueError`.

## Format options

Two more knobs control the *shape* of the returned string.

### `name_part` — which slice of the name

| `name_part` | Returns                       | Notes                                                        |
| ----------- | ----------------------------- | ------------------------------------------------------------ |
| `"full"`    | All parts joined (default)    | "Frodo Baggins", "Yoda", "Ba Sing Se"                        |
| `"first"`   | First part only               | "Frodo", "Yoda", "Ba"                                        |
| `"last"`    | Last part only                | "Baggins"; entities with no last name are filtered out       |

```python
list_names(franchise="scientists", name_part="last", case="title")[:8]
# ['Newton', 'Einstein', 'Curie', 'Darwin', 'Galilei', 'Tesla', 'Feynman', 'Hawking']
```

### `case` — how the parts are joined

| `case`      | Example                  |
| ----------- | ------------------------ |
| `"snake"`   | `frodo_baggins` (default)|
| `"title"`   | `Frodo Baggins`          |
| `"compact"` | `frodobaggins`           |
| `"kebab"`   | `frodo-baggins`          |

Apostrophes and hyphens are preserved in `title` only; other cases strip them
(e.g., `King's Landing` → `kings_landing` / `kingslanding` / `kings-landing`).

## Hash suffix for uniqueness

A short hex suffix makes collisions vanishingly rare while keeping the prefix
readable.

```python
name("config-v3", suffix=True)
# 'aragorn_8c1d2'

name("config-v3", suffix=True, suffix_length=8, separator="-")
# 'aragorn-8c1d24a9'
```

## Reusable namer

When you call the namer many times with the same configuration, build a
`NameKit` once.

```python
from namekit import NameKit

kit = NameKit(
    franchise=["lotr", "ghibli"],
    affiliation="good",
    case="title",
    suffix=True,
)
for user_id in user_ids:
    print(kit(user_id))
```

## Inspecting the corpus

```python
from namekit import (
    FRANCHISES, ENTITY_TYPES, AFFILIATIONS, NAME_PARTS, CASES,
    ENTITIES, list_names, list_entities, format_name,
)

FRANCHISES                              # ('avatar', 'starwars', 'lotr', ...)
ENTITY_TYPES                            # ('character', 'place')
AFFILIATIONS                            # ('good', 'bad', 'neutral')
NAME_PARTS                              # ('first', 'last', 'full')
CASES                                   # ('snake', 'title', 'compact', 'kebab')

list_names(franchise="harrypotter", affiliation="good", case="title")
list_entities(entity_type="place")      # full Entity dataclasses

# Format a single Entity yourself
e = ENTITIES[0]
format_name(e, name_part="last", case="title")
```

Each `Entity` is a frozen dataclass:

```python
from namekit import Entity
Entity(parts=("Frodo", "Baggins"), franchise="lotr",
       entity_type="character", affiliation="good")
```

The `parts` tuple holds Title Case word pieces. `entity.first` and
`entity.last` are convenience properties (`last` is `None` when there is only
one part).

## Bundled franchises

`avatar`, `starwars`, `lotr`, `pokemon`, `harrypotter`, `marvel`, `got`,
`ghibli`, `mario`, `zelda`, `disney`, `greek`, `norse`, `scientists`,
`philosophers`.

The corpus has 434 entries (~430 unique formatted names) across 361
characters and 73 places. Affiliation tags are best-effort labels for casual
filtering; places default to neutral and only explicit villain strongholds
(Mordor, Bowser's Castle, etc.) are tagged bad.

## Notes on collisions

Without a suffix, the chance of two different keys producing the same name is
roughly `1 / len(corpus)`. For the default corpus that's about 0.23% per pair.
If uniqueness matters, pass `suffix=True`; with the default 5-char hex suffix,
collisions become astronomically unlikely.

## Development

```bash
pip install -e '.[dev]'
pytest
```

## License

MIT
