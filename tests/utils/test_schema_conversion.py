"""Tests for SQL DDL to MongoDB schema conversion."""

from __future__ import annotations

import json
import unittest

from src.utils.schema_conversion import derive_mongo_schema, derive_mongo_schema_json


FILM_DDL = """CREATE TABLE film (
  film_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  release_year SMALLINT,
  language_id SMALLINT NOT NULL,
  rental_duration SMALLINT NOT NULL,
  rental_rate NUMERIC(4,2) NOT NULL,
  length SMALLINT,
  replacement_cost NUMERIC(5,2) NOT NULL,
  rating VARCHAR(10),
  special_features TEXT[],
  last_update TIMESTAMP NOT NULL,
  fulltext TSVECTOR NOT NULL,
  PRIMARY KEY (film_id),
  FOREIGN KEY (language_id) REFERENCES language(language_id)
);"""


class SchemaConversionTest(unittest.TestCase):
    def test_postgres_ddl_uses_clean_field_names(self) -> None:
        schema = derive_mongo_schema(FILM_DDL)
        fields = schema["film"]

        self.assertEqual(fields["_id"], "ObjectId")
        self.assertEqual(fields["title"], "string")
        self.assertEqual(fields["film_id"], "number")
        self.assertEqual(fields["rental_rate"], "number")
        self.assertEqual(fields["replacement_cost"], "number")
        self.assertEqual(fields["fulltext"], "string")

        for key in fields:
            if key == "_id":
                continue
            self.assertNotIn("NOT", key)
            self.assertNotIn("FOREIGN KEY", key)
            self.assertNotIn("REFERENCES", key)

    def test_postgres_ddl_json_output(self) -> None:
        parsed = json.loads(derive_mongo_schema_json(FILM_DDL))
        self.assertIn("title", parsed["film"])
        self.assertNotIn("title VARCHAR(255) NOT", parsed["film"])


if __name__ == "__main__":
    unittest.main()
