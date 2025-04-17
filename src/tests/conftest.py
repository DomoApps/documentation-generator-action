import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch):
    monkeypatch.setenv("CHAT_GPT_TOKEN", "fake-token")
    monkeypatch.setenv("CHAT_GPT_MODEL", "gpt-4")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-github-token")
    monkeypatch.setenv("GITHUB_OWNER", "fake-owner")
    monkeypatch.setenv("GITHUB_REPO", "fake-repo")
    monkeypatch.setenv("GITHUB_PULL_NUMBER", "1")
    monkeypatch.setenv("HEAD_REF", "main")
    monkeypatch.setenv("BASE_REF", "develop")