"""Curated demo prompts for the web UI."""

from __future__ import annotations

from agent.web.schemas import ExampleItem

CAPSTONE_EXAMPLES: list[ExampleItem] = [
    ExampleItem(
        id="D1",
        label="Albums with artists",
        message="List album titles with artist names.",
        intent="text2sql",
    ),
    ExampleItem(
        id="D3",
        label="Artist with most albums",
        message="Which artist has the most albums?",
        intent="text2sql",
    ),
    ExampleItem(
        id="D6",
        label="Tracks per genre",
        message="How many tracks are in each genre?",
        intent="text2sql",
    ),
    ExampleItem(
        id="D5",
        label="Top spending customer",
        message="Which customer has the highest total spending?",
        intent="text2sql",
    ),
    ExampleItem(
        id="S1",
        label="SQL → Mongo (2 tables)",
        message="Convert this SQL to MongoDB",
        intent="sql2nosql",
        sql=(
            'SELECT ar."Name" AS artist, COUNT(al."AlbumId") AS album_count '
            'FROM "Artist" ar JOIN "Album" al ON ar."ArtistId" = al."ArtistId" '
            'GROUP BY ar."Name" ORDER BY album_count DESC LIMIT 5;'
        ),
    ),
    ExampleItem(
        id="N1",
        label="Document a join query",
        message=(
            'Document this SQL: SELECT ar."Name" AS artist, COUNT(al."AlbumId") '
            'FROM "Artist" ar JOIN "Album" al ON ar."ArtistId" = al."ArtistId" '
            'GROUP BY ar."Name"'
        ),
        intent="nosql2doc",
    ),
]


def list_examples() -> list[ExampleItem]:
    return CAPSTONE_EXAMPLES
