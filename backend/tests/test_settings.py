from settings import Settings


def test_ticker_universe_parses_csv_and_uppercases(monkeypatch):
    monkeypatch.setenv("MARKETLENS_TICKER_UNIVERSE", "nvda, aapl , msft")
    settings = Settings()
    assert settings.ticker_universe == ["NVDA", "AAPL", "MSFT"]


def test_cors_origins_not_uppercased(monkeypatch):
    monkeypatch.setenv("MARKETLENS_CORS_ORIGINS", "http://localhost:3000,http://x.dev")
    settings = Settings()
    assert settings.cors_origins == ["http://localhost:3000", "http://x.dev"]


def test_litellm_model_defaults_to_ollama():
    assert Settings().llm.litellm_model.startswith("ollama_chat/")


def test_litellm_model_switches_to_anthropic():
    settings = Settings(llm={"provider": "anthropic", "anthropic_model": "claude-x"})
    assert settings.llm.litellm_model == "anthropic/claude-x"


def test_db_dsn_uses_asyncpg():
    assert Settings().db.dsn.startswith("postgresql+asyncpg://")
