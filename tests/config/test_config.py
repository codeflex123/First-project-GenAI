from __future__ import annotations

import os

from src.config import load_config


def test_load_config_defaults(monkeypatch):
    # Ensure environment variables are not set so defaults are used.
    for var in ["APP_ENV", "APP_PORT", "LOG_LEVEL", "HF_TOKEN", "HUGGINGFACE_TOKEN", "GEMINI_API_KEY"]:
        monkeypatch.delenv(var, raising=False)

    cfg = load_config()

    assert cfg.env == "development"
    assert cfg.port == 8000
    assert cfg.log_level == "INFO"
    assert cfg.hf_token is None
    assert cfg.gemini_api_key is None


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("HF_TOKEN", "fake-hf-token")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-gemini-key")

    cfg = load_config()

    assert cfg.env == "production"
    assert cfg.port == 9000
    assert cfg.log_level == "DEBUG"
    assert cfg.hf_token == "fake-hf-token"
    assert cfg.gemini_api_key == "fake-gemini-key"

