"""Unit tests for SettingsStore."""

from tool.core.settings_store import AppSettings, DatabaseConnection, MongoConnection, SettingsStore


def test_settings_round_trip(settings_store: SettingsStore, sample_connection: DatabaseConnection):
    settings = AppSettings(connections=[sample_connection], active_connection_id=sample_connection.id)
    settings_store.save(settings)
    loaded = settings_store.load()
    assert loaded.active_connection_id == sample_connection.id
    assert len(loaded.connections) == 1
    assert loaded.connections[0].name == "Test DB"
    assert loaded.fastapi.model == "codegen-text2sql"


def test_add_and_delete_connection(settings_store: SettingsStore, sample_connection: DatabaseConnection):
    settings = AppSettings()
    settings_store.add_connection(settings, sample_connection)
    loaded = settings_store.load()
    assert len(loaded.connections) == 1

    settings_store.delete_connection(loaded, sample_connection.id)
    loaded = settings_store.load()
    assert loaded.connections == []
    assert loaded.active_connection_id is None


def test_connection_sqlalchemy_url(sample_connection: DatabaseConnection):
    url = sample_connection.to_sqlalchemy_url()
    assert url.startswith("postgresql+psycopg://")
    assert "testdb" in url


def test_mongo_connection_round_trip(settings_store: SettingsStore):
    conn = MongoConnection(
        id="mongo-test",
        name="Test Mongo",
        host="localhost",
        port=27017,
        database="dvd",
        username="tend",
        password="secret",
    )
    settings = AppSettings(mongo_connections=[conn], active_mongo_connection_id=conn.id)
    settings_store.save(settings)
    loaded = settings_store.load()
    assert loaded.active_mongo_connection_id == conn.id
    assert loaded.mongo_connections[0].database == "dvd"
