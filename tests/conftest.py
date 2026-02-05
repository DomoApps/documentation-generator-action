import os
import pytest
from pathlib import Path


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


@pytest.fixture
def sample_yaml_path():
    """Get path to sample YAML file."""
    return "./samples/Documents.yaml"


@pytest.fixture
def sample_docs_json():
    """Create a sample docs.json structure for testing."""
    return {
        "navigation": {
            "languages": {
                "en": {
                    "tabs": [
                        {
                            "tab": "Documentation",
                            "pages": ["intro", "getting-started"]
                        },
                        {
                            "tab": "API Reference",
                            "pages": []
                        }
                    ]
                }
            }
        }
    }
