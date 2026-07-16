from __future__ import annotations

import pytest

import namekit
from namekit import (
    AFFILIATIONS,
    CASES,
    ENTITIES,
    ENTITY_TYPES,
    FRANCHISES,
    NAME_PARTS,
    Entity,
    NameKit,
    format_name,
    list_entities,
    list_names,
    name,
)


def _all_formatted(name_part: str = "full", case: str = "snake") -> set[str]:
    return {
        format_name(e, name_part=name_part, case=case)
        for e in ENTITIES
        if not (name_part == "last" and e.last is None)
    }


class TestDeterminism:
    def test_same_key_same_name(self):
        assert name("hello") == name("hello")

    def test_result_is_in_corpus(self):
        assert name("hello") in _all_formatted()

    def test_format_changes_output(self):
        # Same key, different case → potentially different string.
        snake = name("user-42", case="snake")
        title = name("user-42", case="title")
        # They map to the same Entity, so title should be the title-case version
        # of snake (case-insensitive equivalence after strip).
        assert snake.replace("_", "").lower() == title.replace(" ", "").lower()


class TestFranchiseFiltering:
    def test_single_franchise(self):
        result = name("user-42", franchise="lotr")
        lotr_names = _all_formatted_for_franchise("lotr")
        assert result in lotr_names

    def test_multiple_franchises(self):
        union = _all_formatted_for_franchise("lotr") | _all_formatted_for_franchise(
            "starwars"
        )
        for i in range(50):
            assert name(f"key-{i}", franchise=["lotr", "starwars"]) in union

    def test_unknown_franchise_raises(self):
        with pytest.raises(KeyError):
            name("anything", franchise="nope")


def _all_formatted_for_franchise(f: str) -> set[str]:
    return {format_name(e) for e in ENTITIES if e.franchise == f}


class TestEntityTypeFiltering:
    def test_only_places(self):
        place_names = {format_name(e) for e in ENTITIES if e.entity_type == "place"}
        for i in range(50):
            assert name(f"k{i}", entity_type="place") in place_names

    def test_only_characters(self):
        char_names = {format_name(e) for e in ENTITIES if e.entity_type == "character"}
        for i in range(50):
            assert name(f"k{i}", entity_type="character") in char_names

    def test_unknown_entity_type_raises(self):
        with pytest.raises(KeyError):
            name("k", entity_type="creature")

    def test_entity_type_list(self):
        # Both types accepted via a list.
        union = {format_name(e) for e in ENTITIES}
        for i in range(50):
            assert name(f"k{i}", entity_type=["character", "place"]) in union


class TestAffiliationFiltering:
    def test_only_good(self):
        targets = {format_name(e) for e in ENTITIES if e.affiliation == "good"}
        for i in range(50):
            assert name(f"k{i}", affiliation="good") in targets

    def test_only_bad(self):
        targets = {format_name(e) for e in ENTITIES if e.affiliation == "bad"}
        for i in range(50):
            assert name(f"k{i}", affiliation="bad") in targets

    def test_unknown_affiliation_raises(self):
        with pytest.raises(KeyError):
            name("k", affiliation="chaotic-neutral")

    def test_affiliation_list_excludes_villains(self):
        # ["good", "neutral"] should never produce a "bad" entity.
        bad_names = {format_name(e) for e in ENTITIES if e.affiliation == "bad"}
        for i in range(100):
            result = name(f"k{i}", affiliation=["good", "neutral"])
            assert result not in bad_names


class TestCombinedFiltering:
    def test_lotr_villains(self):
        targets = {
            format_name(e)
            for e in ENTITIES
            if e.franchise == "lotr"
            and e.entity_type == "character"
            and e.affiliation == "bad"
        }
        for i in range(30):
            result = name(
                f"k{i}",
                franchise="lotr",
                entity_type="character",
                affiliation="bad",
            )
            assert result in targets

    def test_lotr_strongholds(self):
        targets = {
            format_name(e)
            for e in ENTITIES
            if e.franchise == "lotr"
            and e.entity_type == "place"
            and e.affiliation == "bad"
        }
        assert "mordor" in targets
        assert "isengard" in targets
        assert "mount_doom" in targets
        for i in range(30):
            result = name(
                f"k{i}",
                franchise="lotr",
                entity_type="place",
                affiliation="bad",
            )
            assert result in targets

    def test_empty_filter_raises(self):
        with pytest.raises(ValueError):
            name(
                "k",
                franchise="scientists",
                entity_type="character",
                affiliation="bad",
            )


class TestNamePart:
    def test_first_only(self):
        result = name("user-42", franchise="lotr", name_part="first")
        firsts = {e.first.lower() for e in ENTITIES if e.franchise == "lotr"}
        assert result in firsts

    def test_last_only_filters(self):
        # All results when name_part="last" must come from entities with last names.
        for i in range(30):
            result = name(f"k{i}", franchise="lotr", name_part="last")
            lotr_lasts = {
                format_name(e, name_part="last")
                for e in ENTITIES
                if e.franchise == "lotr" and e.last is not None
            }
            assert result in lotr_lasts

    def test_last_with_singletons_only_raises(self):
        # Pokemon and avatar have many singletons; force a tiny pool.
        # Use scientists who all have last names, so this should NOT raise.
        result = name("k", franchise="scientists", name_part="last")
        assert result  # arbitrary scientist last name

    def test_last_when_corpus_has_no_lasts(self):
        # Pokemon characters are all single-name; name_part="last" → empty.
        with pytest.raises(ValueError):
            name(
                "k",
                franchise="pokemon",
                entity_type="character",
                name_part="last",
            )

    def test_full_default(self):
        # Default name_part is "full".
        assert name("k") == name("k", name_part="full")


class TestCase:
    def test_snake_default(self):
        # Default case is snake.
        assert name("k") == name("k", case="snake")

    def test_title_has_spaces_when_multipart(self):
        kit = NameKit(franchise="lotr", case="title")
        # At least one of the LOTR names is multi-part (e.g., Frodo Baggins).
        assert any(" " in s for s in kit.corpus)

    def test_snake_uses_underscores(self):
        kit = NameKit(franchise="lotr", case="snake")
        assert any("_" in s for s in kit.corpus)
        assert not any(" " in s for s in kit.corpus)

    def test_compact_no_separators(self):
        kit = NameKit(franchise="lotr", case="compact")
        for s in kit.corpus:
            assert "_" not in s
            assert " " not in s
            assert "-" not in s

    def test_kebab_uses_hyphens(self):
        kit = NameKit(franchise="lotr", case="kebab")
        assert any("-" in s for s in kit.corpus)
        assert not any("_" in s for s in kit.corpus)

    def test_unknown_case_raises(self):
        with pytest.raises(ValueError):
            name("k", case="screaming")

    def test_unknown_name_part_raises(self):
        with pytest.raises(ValueError):
            name("k", name_part="middle")


class TestFormatName:
    def test_frodo_baggins_formats(self):
        e = next(x for x in ENTITIES if x.parts == ("Frodo", "Baggins"))
        assert format_name(e, name_part="full", case="title") == "Frodo Baggins"
        assert format_name(e, name_part="full", case="snake") == "frodo_baggins"
        assert format_name(e, name_part="full", case="compact") == "frodobaggins"
        assert format_name(e, name_part="full", case="kebab") == "frodo-baggins"
        assert format_name(e, name_part="first", case="title") == "Frodo"
        assert format_name(e, name_part="last", case="title") == "Baggins"
        assert format_name(e, name_part="last", case="snake") == "baggins"

    def test_single_part_with_internal_space(self):
        # "King Boo" is a single name, not first+last — encoded as one part.
        e = next(x for x in ENTITIES if x.parts == ("King Boo",))
        assert format_name(e, case="title") == "King Boo"
        assert format_name(e, case="snake") == "king_boo"
        assert format_name(e, case="compact") == "kingboo"
        assert format_name(e, case="kebab") == "king-boo"
        # Single-part: no last name
        with pytest.raises(ValueError):
            format_name(e, name_part="last")

    def test_apostrophes_stripped_in_non_title(self):
        e = next(x for x in ENTITIES if x.parts == ("King's Landing",))
        assert format_name(e, case="title") == "King's Landing"
        assert format_name(e, case="snake") == "kings_landing"
        assert format_name(e, case="compact") == "kingslanding"
        assert format_name(e, case="kebab") == "kings-landing"

    def test_hyphenated_part_in_first_last(self):
        # Obi-Wan Kenobi: hyphenated first name, real last name.
        # Internal hyphen becomes _ in snake (-, "" in kebab/compact).
        e = next(x for x in ENTITIES if x.parts == ("Obi-Wan", "Kenobi"))
        assert format_name(e, case="title") == "Obi-Wan Kenobi"
        assert format_name(e, case="snake") == "obi_wan_kenobi"
        assert format_name(e, case="compact") == "obiwankenobi"
        assert format_name(e, case="kebab") == "obi-wan-kenobi"

    def test_three_word_single_part(self):
        # "Ba Sing Se" is one place name, encoded as one part.
        e = next(x for x in ENTITIES if x.parts == ("Ba Sing Se",))
        assert format_name(e, case="title") == "Ba Sing Se"
        assert format_name(e, case="snake") == "ba_sing_se"
        assert format_name(e, case="compact") == "basingse"
        assert format_name(e, case="kebab") == "ba-sing-se"

    def test_first_last_only_for_real_names(self):
        # King Boo, Iron Man, Mount Doom etc. are single-part — no "last".
        for parts in [
            ("King Boo",),
            ("Iron Man",),
            ("Mount Doom",),
            ("No-Face",),
            ("Bowser Jr",),
            ("Pallet Town",),
        ]:
            entries = [e for e in ENTITIES if e.parts == parts]
            assert len(entries) == 1, f"missing or duplicated: {parts}"
            assert entries[0].last is None

    def test_singleton_entity_first_equals_full(self):
        e = next(x for x in ENTITIES if x.parts == ("Yoda",))
        assert format_name(e, name_part="first") == "yoda"
        assert format_name(e, name_part="full") == "yoda"

    def test_singleton_entity_last_raises(self):
        e = next(x for x in ENTITIES if x.parts == ("Yoda",))
        with pytest.raises(ValueError):
            format_name(e, name_part="last")


class TestSuffix:
    def test_suffix_appended(self):
        result = name("user-42", suffix=True)
        assert "_" in result  # snake-case default + _ separator
        # Last 5 chars after the final underscore should be hex.
        suf = result.rsplit("_", 1)[1]
        assert len(suf) == 5
        assert all(c in "0123456789abcdef" for c in suf)

    def test_suffix_is_deterministic(self):
        assert name("k", suffix=True) == name("k", suffix=True)


class TestNameKit:
    def test_callable(self):
        kit = NameKit(franchise="lotr")
        assert kit("user-42") in {
            format_name(e) for e in ENTITIES if e.franchise == "lotr"
        }

    def test_matches_function(self):
        kit = NameKit(franchise="lotr", case="title")
        assert kit("u-7") == name("u-7", franchise="lotr", case="title")

    def test_filters_compose_with_format(self):
        kit = NameKit(franchise="lotr", name_part="last", case="title")
        targets = {
            format_name(e, name_part="last", case="title")
            for e in ENTITIES
            if e.franchise == "lotr" and e.last is not None
        }
        for i in range(20):
            assert kit(f"k{i}") in targets

    def test_corpus_property_is_a_copy(self):
        kit = NameKit(franchise="harrypotter")
        c = kit.corpus
        c.append("dummy")
        assert "dummy" not in kit.corpus

    def test_empty_corpus_raises(self):
        with pytest.raises(ValueError):
            NameKit(
                franchise="pokemon",
                entity_type="character",
                name_part="last",
            )


class TestListing:
    def test_list_names_dedupes(self):
        all_names = list_names()
        assert len(all_names) == len(set(all_names))

    def test_list_entities_does_not_dedupe(self):
        thors = [e for e in list_entities() if e.parts == ("Thor",)]
        assert len(thors) == 2  # marvel and norse

    def test_list_entities_filtered(self):
        results = list_entities(franchise="lotr", entity_type="place")
        assert all(e.franchise == "lotr" and e.entity_type == "place" for e in results)
        assert len(results) > 0

    def test_list_entities_name_part_last_filters_singletons(self):
        # Pokemon characters are all single-name; filtering to last leaves none.
        results = list_entities(
            franchise="pokemon", entity_type="character", name_part="last"
        )
        assert results == []


class TestPackage:
    def test_franchises_exposed(self):
        assert "lotr" in FRANCHISES
        assert "starwars" in FRANCHISES

    def test_constants(self):
        assert set(ENTITY_TYPES) == {"character", "place"}
        assert set(AFFILIATIONS) == {"good", "bad", "neutral"}
        assert set(NAME_PARTS) == {"first", "last", "full"}
        assert set(CASES) == {"snake", "title", "compact", "kebab"}

    def test_version(self):
        assert namekit.__version__ == "0.1.2"

    def test_no_duplicate_entries_within_franchise_and_type(self):
        seen: set[tuple[tuple[str, ...], str, str]] = set()
        for e in ENTITIES:
            key = (e.parts, e.franchise, e.entity_type)
            assert key not in seen, f"duplicate: {key}"
            seen.add(key)

    def test_entity_is_frozen(self):
        e: Entity = ENTITIES[0]
        with pytest.raises(Exception):
            e.parts = ("X",)  # type: ignore[misc]

    def test_frances_arnold_present(self):
        match = [e for e in ENTITIES if e.parts == ("Frances", "Arnold")]
        assert len(match) == 1
        assert match[0].franchise == "scientists"


# ---- to_key / name_from_mapping -------------------------------------------


def test_to_key_is_order_independent():
    assert namekit.to_key({"a": 1, "b": 2}) == namekit.to_key({"b": 2, "a": 1})


def test_to_key_excludes_top_level_keys():
    assert namekit.to_key(
        {"a": 1, "device": "cpu"}, exclude=("device",)
    ) == namekit.to_key({"a": 1})


def test_to_key_sorts_sets_and_is_compact():
    assert namekit.to_key({"s": {3, 1, 2}}) == '{"s":[1,2,3]}'


def test_name_from_mapping_is_stable_and_matches_to_key():
    m = {"lr": 0.5, "model": "esm2"}
    assert namekit.name_from_mapping(m) == namekit.name(namekit.to_key(m))
    assert namekit.name_from_mapping(m) == namekit.name_from_mapping(
        dict(reversed(list(m.items())))
    )


def test_name_from_mapping_excludes_and_forwards_kwargs():
    m = {"lr": 0.5, "model": "esm2", "device": "cpu"}
    without = {"lr": 0.5, "model": "esm2"}
    assert namekit.name_from_mapping(
        m, exclude=("device",), suffix=True
    ) == namekit.name_from_mapping(without, suffix=True)
    assert namekit.name_from_mapping(m, suffix=True).count("_") >= 1  # suffix appended
