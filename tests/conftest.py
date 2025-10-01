import os
import pytest
from pathlib import Path
from unittest.mock import patch


def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Don't override existing environment variables
                    if key not in os.environ:
                        os.environ[key] = value


# Load .env file before running any tests
load_env_file()


@pytest.fixture(autouse=True)
def mock_environment_variables(monkeypatch, request):
    # Skip mocking for integration tests (marked with @pytest.mark.integration)
    if 'integration' in request.keywords:
        return

    # Mock variables for unit tests
    monkeypatch.setenv("CHAT_GPT_TOKEN", "fake-token")
    monkeypatch.setenv("CHAT_GPT_MODEL", "gpt-4")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-github-token")
    monkeypatch.setenv("GITHUB_OWNER", "fake-owner")
    monkeypatch.setenv("GITHUB_REPO", "fake-repo")
    monkeypatch.setenv("GITHUB_PULL_NUMBER", "1")
    monkeypatch.setenv("HEAD_REF", "main")
    monkeypatch.setenv("BASE_REF", "develop")