"""
Tests for YAMLPreserver module

Tests YAML structure preservation including:
- Comment preservation
- Key ordering
- Formatting (indentation, line breaks)
- Nested structures
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.yaml_preserver import YAMLPreserver


@pytest.fixture
def yaml_preserver():
    """Create a YAMLPreserver instance for testing."""
    return YAMLPreserver()


@pytest.fixture
def sample_yaml_with_comments(tmp_path):
    """Create a sample YAML file with comments for testing."""
    yaml_content = """# OpenAPI specification
openapi: 3.1.0
info:
  # API metadata
  title: 'Test API'
  description: 'Original description'  # inline comment
  version: '1.0.0'
servers:
  - url: https://example.com
tags:
  - name: Users
    description: User operations
  - name: Products
    # TODO: Add description
paths:
  /users:
    get:
      summary: Get users
      description: Retrieve all users
"""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


@pytest.fixture
def sample_yaml_nested(tmp_path):
    """Create a sample YAML file with nested structures."""
    yaml_content = """openapi: 3.1.0
info:
  title: 'Nested Test'
  version: '1.0.0'
  contact:
    name: 'API Support'
    email: 'support@example.com'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
"""
    yaml_file = tmp_path / "nested.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


class TestYAMLPreserver:
    """Test suite for YAMLPreserver class."""

    def test_load_with_comments_success(self, yaml_preserver, sample_yaml_with_comments):
        """Test loading YAML file with comments."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)

        assert yaml_obj is not None
        assert yaml_obj['openapi'] == '3.1.0'
        assert yaml_obj['info']['title'] == 'Test API'
        assert yaml_obj['info']['description'] == 'Original description'

    def test_load_with_comments_file_not_found(self, yaml_preserver):
        """Test loading non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            yaml_preserver.load_with_comments('/nonexistent/file.yaml')

    def test_set_value_at_path_simple(self, yaml_preserver, sample_yaml_with_comments):
        """Test setting a value at a simple path."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)

        result = yaml_preserver.set_value_at_path(
            yaml_obj,
            'info.description',
            'Enhanced description'
        )

        assert result is True
        assert yaml_obj['info']['description'] == 'Enhanced description'

    def test_set_value_at_path_nested(self, yaml_preserver, sample_yaml_nested):
        """Test setting a value at a nested path."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_nested)

        result = yaml_preserver.set_value_at_path(
            yaml_obj,
            'info.contact.name',
            'New Support Team'
        )

        assert result is True
        assert yaml_obj['info']['contact']['name'] == 'New Support Team'

    def test_set_value_at_path_create_intermediate(self, yaml_preserver, sample_yaml_nested):
        """Test setting a value creates intermediate objects if needed."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_nested)

        result = yaml_preserver.set_value_at_path(
            yaml_obj,
            'info.license.name',
            'MIT'
        )

        assert result is True
        assert yaml_obj['info']['license']['name'] == 'MIT'

    def test_get_value_at_path_success(self, yaml_preserver, sample_yaml_with_comments):
        """Test getting a value at a path."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)

        value = yaml_preserver.get_value_at_path(yaml_obj, 'info.title')

        assert value == 'Test API'

    def test_get_value_at_path_not_found(self, yaml_preserver, sample_yaml_with_comments):
        """Test getting a value at a non-existent path."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)

        value = yaml_preserver.get_value_at_path(yaml_obj, 'info.nonexistent')

        assert value is None

    def test_save_with_preservation(self, yaml_preserver, sample_yaml_with_comments, tmp_path):
        """Test saving YAML with preservation."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)
        output_path = str(tmp_path / "output.yaml")

        result = yaml_preserver.save_with_preservation(yaml_obj, output_path)

        assert result is True
        assert os.path.exists(output_path)

        # Verify the saved file can be loaded
        loaded_obj = yaml_preserver.load_with_comments(output_path)
        assert loaded_obj['info']['title'] == yaml_obj['info']['title']

    def test_comments_preserved_after_modification(
        self,
        yaml_preserver,
        sample_yaml_with_comments,
        tmp_path
    ):
        """Test that comments are preserved after modification."""
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)

        # Modify a value
        yaml_preserver.set_value_at_path(yaml_obj, 'info.description', 'New description')

        # Save to a new file
        output_path = str(tmp_path / "modified.yaml")
        yaml_preserver.save_with_preservation(yaml_obj, output_path)

        # Read the raw content and check for comments
        with open(output_path, 'r') as f:
            content = f.read()

        assert '# OpenAPI specification' in content
        assert '# API metadata' in content

    def test_key_ordering_preserved(self, yaml_preserver, sample_yaml_with_comments, tmp_path):
        """Test that key ordering is preserved."""
        # Load original
        original_content = Path(sample_yaml_with_comments).read_text()
        original_keys = []
        for line in original_content.split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                key = line.split(':')[0].strip()
                if key and not key.startswith('-'):
                    original_keys.append(key)

        # Modify and save
        yaml_obj = yaml_preserver.load_with_comments(sample_yaml_with_comments)
        yaml_preserver.set_value_at_path(yaml_obj, 'info.description', 'Modified')
        output_path = str(tmp_path / "ordered.yaml")
        yaml_preserver.save_with_preservation(yaml_obj, output_path)

        # Check ordering in output
        modified_content = Path(output_path).read_text()
        modified_keys = []
        for line in modified_content.split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                key = line.split(':')[0].strip()
                if key and not key.startswith('-'):
                    modified_keys.append(key)

        # At least the top-level keys should be in the same order
        assert original_keys[:3] == modified_keys[:3]  # openapi, info, servers

    def test_apply_enhancements_multiple(
        self,
        yaml_preserver,
        sample_yaml_with_comments,
        tmp_path
    ):
        """Test applying multiple enhancements at once."""
        enhancements = {
            'info.description': 'Enhanced API description',
            'info.version': '2.0.0',
            'tags.0.description': 'Enhanced user operations'
        }

        output_path = str(tmp_path / "enhanced.yaml")
        result = yaml_preserver.apply_enhancements(
            sample_yaml_with_comments,
            enhancements,
            output_path
        )

        assert result is True

        # Verify enhancements were applied
        yaml_obj = yaml_preserver.load_with_comments(output_path)
        assert yaml_obj['info']['description'] == 'Enhanced API description'
        assert yaml_obj['info']['version'] == '2.0.0'
        assert yaml_obj['tags'][0]['description'] == 'Enhanced user operations'

    def test_apply_enhancements_in_place(self, yaml_preserver, sample_yaml_with_comments):
        """Test applying enhancements in-place (no output path)."""
        enhancements = {
            'info.description': 'In-place enhancement'
        }

        # Create a copy for in-place modification
        temp_file = sample_yaml_with_comments + '.copy'
        import shutil
        shutil.copy(sample_yaml_with_comments, temp_file)

        result = yaml_preserver.apply_enhancements(temp_file, enhancements)

        assert result is True

        # Verify enhancement was applied to the same file
        yaml_obj = yaml_preserver.load_with_comments(temp_file)
        assert yaml_obj['info']['description'] == 'In-place enhancement'

        # Clean up
        os.remove(temp_file)

    def test_validate_yaml_structure_valid(self, yaml_preserver, sample_yaml_with_comments):
        """Test validation of valid YAML structure."""
        result = yaml_preserver.validate_yaml_structure(sample_yaml_with_comments)
        assert result is True

    def test_validate_yaml_structure_invalid(self, yaml_preserver, tmp_path):
        """Test validation of invalid YAML structure."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: structure: bad:")

        result = yaml_preserver.validate_yaml_structure(str(invalid_yaml))
        assert result is False

    def test_validate_yaml_structure_nonexistent(self, yaml_preserver):
        """Test validation of non-existent file."""
        result = yaml_preserver.validate_yaml_structure('/nonexistent/file.yaml')
        assert result is False
