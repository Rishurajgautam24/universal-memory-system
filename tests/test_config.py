
from ums.config import Settings, settings


def test_settings_defaults():
    s = Settings()
    assert s.host == "0.0.0.0"
    assert s.port == 8000
    assert s.workers == 1
    assert s.reload is False
    assert s.log_level == "INFO"
    assert s.database_url == "sqlite+aiosqlite://data/ums.db"
    assert s.embedding_model == "openai/text-embedding-3-small"


def test_settings_override_from_env(monkeypatch):
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9000")
    s = Settings()
    assert s.host == "127.0.0.1"
    assert s.port == 9000


def test_settings_module_loaded():
    assert settings.host == "0.0.0.0"
