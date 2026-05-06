"""Entity corpus organized by franchise, entity type, and affiliation.

Each entry is an `Entity` whose `parts` tuple holds Title Case word pieces.
Multi-part entries are reserved for genuine first+last name pairs (e.g.,
("Frodo", "Baggins"), ("Tyrion", "Lannister")). Single-name identifiers that
happen to span multiple words ("King Boo", "Iron Man", "Mount Doom",
"King's Landing") are stored as one part with internal whitespace; the
formatter collapses them to "king_boo" / "kingboo" / "king-boo" as needed.

Affiliation tags are best-effort labels for casual filtering, not authoritative
ontology. Places default to "neutral"; only explicit villain strongholds are
"bad".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

EntityType = Literal["character", "place"]
Affiliation = Literal["good", "bad", "neutral"]

ENTITY_TYPES: tuple[EntityType, ...] = ("character", "place")
AFFILIATIONS: tuple[Affiliation, ...] = ("good", "bad", "neutral")


@dataclass(frozen=True)
class Entity:
    """A single entry in the corpus.

    `parts` holds Title Case word pieces. Multi-part entries are reserved for
    real first+last name pairs (e.g. ("Frodo", "Baggins")). Single-name
    multi-word identifiers ("King Boo", "Mount Doom") are stored as one part
    with internal whitespace.
    """

    parts: tuple[str, ...]
    franchise: str
    entity_type: EntityType
    affiliation: Affiliation

    @property
    def first(self) -> str:
        """First word of the name."""
        return self.parts[0]

    @property
    def last(self) -> str | None:
        """Last word of the name, or None for single-part entries."""
        return self.parts[-1] if len(self.parts) > 1 else None


ENTITIES: list[Entity] = []


def _add(
    franchise: str,
    entity_type: EntityType,
    affiliation: Affiliation,
    entries: Sequence[str | tuple[str, ...] | list[str]],
) -> None:
    for entry in entries:
        if isinstance(entry, str):
            parts: tuple[str, ...] = (entry,)
        else:
            parts = tuple(entry)
        ENTITIES.append(Entity(parts, franchise, entity_type, affiliation))


# Avatar: The Last Airbender
_add("avatar", "character", "good", [
    "Aang", "Katara", "Sokka", ("Toph", "Beifong"), "Iroh", "Zuko",
    "Suki", "Appa", "Momo", "Roku", "Kyoshi",
])
_add("avatar", "character", "bad", ["Azula", "Ozai"])
_add("avatar", "place", "bad", ["Fire Nation Capital"])
_add("avatar", "place", "neutral", [
    "Ba Sing Se", "Omashu", "Kyoshi Island", "North Pole", "South Pole",
])

# Star Wars
_add("starwars", "character", "good", [
    ("Luke", "Skywalker"), ("Leia", "Organa"), ("Han", "Solo"), "Yoda",
    ("Obi-Wan", "Kenobi"), ("Qui-Gon", "Jinn"), ("Padme", "Amidala"),
    ("Mace", "Windu"), "Chewbacca", "R2-D2", "C-3PO",
    ("Anakin", "Skywalker"), ("Ahsoka", "Tano"),
])
_add("starwars", "character", "bad", [
    "Palpatine", ("Darth", "Sidious"), ("Darth", "Vader"),
    ("Boba", "Fett"), "Jabba", ("Jango", "Fett"), "Grievous",
    "Dooku", ("Darth", "Maul"),
])
_add("starwars", "place", "bad", ["Mustafar"])
_add("starwars", "place", "neutral", [
    "Naboo", "Endor", "Dagobah", "Tatooine", "Hoth", "Coruscant",
    "Jakku", "Kamino",
])

# Lord of the Rings
_add("lotr", "character", "good", [
    ("Frodo", "Baggins"), ("Sam", "Gamgee"), "Gandalf", "Aragorn",
    "Legolas", "Gimli", "Boromir", "Faramir", "Eowyn",
    ("Bilbo", "Baggins"), "Theoden", "Galadriel", "Treebeard",
    ("Pippin", "Took"), ("Merry", "Brandybuck"), "Elrond", "Arwen",
    ("Thorin", "Oakenshield"), "Gloin",
])
_add("lotr", "character", "bad", [
    "Saruman", "Sauron", "Witch-King", "Smaug", "Balrog",
])
_add("lotr", "character", "neutral", ["Gollum", "Smeagol", "Denethor"])
_add("lotr", "place", "bad", ["Mordor", "Isengard", "Mount Doom"])
_add("lotr", "place", "neutral", [
    "Rivendell", "Hobbiton", "Gondor", "Rohan", "Lothlorien",
    "Shire", "Helm's Deep", "Minas Tirith", "Edoras",
])

# Pokemon
_add("pokemon", "character", "neutral", [
    "Pikachu", "Charizard", "Bulbasaur", "Squirtle", "Mewtwo", "Mew",
    "Gyarados", "Eevee", "Vaporeon", "Jolteon", "Flareon", "Espeon",
    "Umbreon", "Leafeon", "Glaceon", "Lugia", "Entei", "Suicune",
    "Raikou", "Zapdos", "Articuno", "Moltres", "Rayquaza", "Kyogre",
    "Groudon", "Latias", "Latios", "Deoxys", "Dialga", "Palkia",
    "Giratina", "Arceus", "Darkrai", "Cresselia", "Gengar", "Alakazam",
    "Machamp", "Golem", "Onix", "Snorlax", "Lapras", "Dragonite",
])
_add("pokemon", "place", "neutral", [
    "Kanto", "Johto", "Hoenn", "Sinnoh", "Pallet Town",
])

# Harry Potter
_add("harrypotter", "character", "good", [
    ("Harry", "Potter"), ("Hermione", "Granger"), ("Ron", "Weasley"),
    ("Albus", "Dumbledore"), ("Rubeus", "Hagrid"),
    ("Minerva", "McGonagall"), "Dobby", "Hedwig",
    ("Sirius", "Black"), ("Remus", "Lupin"),
    ("Neville", "Longbottom"), ("Luna", "Lovegood"),
    ("Ginny", "Weasley"), ("Fred", "Weasley"), ("George", "Weasley"),
    ("Alastor", "Moody"), ("Severus", "Snape"),
])
_add("harrypotter", "character", "bad", [
    "Voldemort", ("Draco", "Malfoy"), ("Bellatrix", "Lestrange"),
])
_add("harrypotter", "place", "neutral", [
    "Hogwarts", "Diagon Alley", "Hogsmeade", "Gringotts", "Azkaban",
])

# Marvel
_add("marvel", "character", "good", [
    "Iron Man", "Spider-Man", "Captain America", "Thor", "Hulk",
    "Black Widow", "Hawkeye", "Doctor Strange", "Star-Lord", "Groot",
    "Rocket", "Gamora", "Drax", ("Wanda", "Maximoff"), "Vision",
    "Ant-Man", "Wasp", "Black Panther", "Scarlet Witch", "Professor X",
    "Wolverine", "Daredevil", "Falcon", "Winter Soldier",
    ("Nick", "Fury"), "Rogue", "Storm", "Cyclops",
])
_add("marvel", "character", "bad", [
    "Magneto", "Thanos", "Doctor Doom",
])
_add("marvel", "character", "neutral", ["Loki", "Deadpool", "Gambit", "Venom"])
_add("marvel", "place", "neutral", [
    "Wakanda", "Asgard", "Sakaar", "Knowhere", "Titan",
])

# Game of Thrones
_add("got", "character", "good", [
    ("Jon", "Snow"), ("Daenerys", "Targaryen"), ("Tyrion", "Lannister"),
    ("Arya", "Stark"), ("Sansa", "Stark"), ("Bran", "Stark"),
    ("Ned", "Stark"), ("Robb", "Stark"), "Brienne",
    ("Davos", "Seaworth"), ("Samwell", "Tarly"), "Gilly",
    ("Podrick", "Payne"),
])
_add("got", "character", "bad", [
    ("Cersei", "Lannister"), ("Joffrey", "Baratheon"),
    ("Ramsay", "Bolton"), ("Gregor", "Clegane"),
    ("Petyr", "Baelish"),
])
_add("got", "character", "neutral", [
    ("Jaime", "Lannister"), ("Tormund", "Giantsbane"),
    ("Theon", "Greyjoy"), "Varys", ("Sandor", "Clegane"), "Bronn",
    "Melisandre", ("Stannis", "Baratheon"), ("Khal", "Drogo"),
    "Drogon", "Viserion", "Rhaegal",
])
_add("got", "place", "neutral", [
    "Winterfell", "Dragonstone", "Braavos", "King's Landing", "Meereen",
])

# Studio Ghibli
_add("ghibli", "character", "good", [
    "Totoro", "Chihiro", "Haku", "Ponyo", "Kiki", "Howl",
    ("Sophie", "Hatter"), "Ashitaka", "San", "Nausicaa", "Calcifer",
    "Jiji", "Satsuki", "Mei", "Marnie", "Arrietty",
    ("Porco", "Rosso"), "Mononoke",
])
_add("ghibli", "character", "neutral", ["No-Face", "Fujimoto"])

# Mario
_add("mario", "character", "good", [
    "Mario", "Luigi", "Peach", "Yoshi", "Toad", "Rosalina", "Daisy",
    "Donkey Kong", "Toadette",
])
_add("mario", "character", "bad", [
    "Bowser", "Wario", "Waluigi", "King Boo", "Kamek", "Bowser Jr",
])
_add("mario", "place", "bad", ["Bowser's Castle"])
_add("mario", "place", "neutral", [
    "Mushroom Kingdom", "Peach's Castle",
])

# Zelda
_add("zelda", "character", "good", [
    "Link", "Zelda", "Sheik", "Midna", "Impa", "Navi", "Fi", "Hilda",
    "Ravio",
])
_add("zelda", "character", "bad", [
    "Ganon", "Ganondorf", "Vaati", "Skull Kid",
])
_add("zelda", "character", "neutral", ["Tingle"])
_add("zelda", "place", "neutral", [
    "Hyrule", "Kakariko", "Lon Lon", "Gerudo Valley", "Death Mountain",
])

# Disney (excluding Marvel and Star Wars)
_add("disney", "character", "good", [
    "Mickey Mouse", "Minnie Mouse", "Donald Duck", "Goofy", "Pluto",
    "Simba", "Mufasa", "Nala", "Timon", "Pumbaa", "Ariel", "Sebastian",
    "Flounder", "Belle", "Beast", "Lumiere", "Elsa", "Anna", "Olaf",
    "Kristoff", "Sven", "Moana", "Maui", "Stitch", "Lilo",
    ("Buzz", "Lightyear"), "Woody", "Jessie", "Rex", "Hamm", "Slinky",
    "Mulan", "Mushu", "Hercules", "Megara", "Aladdin", "Jasmine",
    "Genie", "Rapunzel", "Flynn Rider", "Tiana", "Naveen",
])
_add("disney", "character", "bad", ["Scar", "Ursula", "Gaston", "Jafar"])
_add("disney", "place", "neutral", [
    "Arendelle", "Atlantica", "Neverland", "Agrabah",
])

# Greek mythology
_add("greek", "character", "good", [
    "Athena", "Apollo", "Artemis", "Hermes", "Demeter", "Hestia",
    "Hephaestus", "Aphrodite", "Dionysus", "Achilles", "Odysseus",
    "Hercules", "Perseus", "Theseus", "Prometheus", "Helios", "Eros",
    "Persephone", "Orpheus", "Jason",
])
_add("greek", "character", "bad", ["Ares", "Medusa", "Agamemnon"])
_add("greek", "character", "neutral", [
    "Zeus", "Hera", "Poseidon", "Hades", "Atlas", "Pandora", "Icarus",
])
_add("greek", "place", "neutral", [
    "Olympus", "Athens", "Ithaca", "Troy", "Atlantis",
])

# Norse mythology
_add("norse", "character", "good", [
    "Thor", "Freya", "Frigg", "Baldur", "Tyr", "Heimdall", "Sif",
    "Idun", "Mimir",
])
_add("norse", "character", "bad", [
    "Loki", "Fenrir", "Jormungandr", "Hel", "Ymir",
])
_add("norse", "character", "neutral", ["Odin", "Ragnar", "Sleipnir"])
_add("norse", "place", "neutral", [
    "Asgard", "Midgard", "Valhalla", "Niflheim", "Jotunheim",
])

# Real-world scientists
_add("scientists", "character", "good", [
    ("Isaac", "Newton"), ("Albert", "Einstein"), ("Marie", "Curie"),
    ("Charles", "Darwin"), ("Galileo", "Galilei"),
    ("Nikola", "Tesla"), ("Richard", "Feynman"),
    ("Stephen", "Hawking"), ("Alan", "Turing"), ("Niels", "Bohr"),
    ("Werner", "Heisenberg"), ("Michael", "Faraday"),
    ("Carl", "Sagan"), ("Jane", "Goodall"), ("Rosalind", "Franklin"),
    ("John", "Wheeler"), ("John", "Jumper"),
    ("Emmanuelle", "Charpentier"), ("Jennifer", "Doudna"),
    ("James", "Watson"), ("Francis", "Crick"), ("Linus", "Pauling"),
    ("Gregor", "Mendel"), ("Frances", "Arnold"),
])

# Real-world philosophers
_add("philosophers", "character", "neutral", [
    "Plato", "Aristotle", "Confucius", ("Rene", "Descartes"),
    ("Immanuel", "Kant"), ("David", "Hume"),
    ("Friedrich", "Nietzsche"), "Socrates", ("John", "Locke"),
    ("Thomas", "Hobbes"),
])


FRANCHISES: tuple[str, ...] = tuple(
    dict.fromkeys(e.franchise for e in ENTITIES)
)
