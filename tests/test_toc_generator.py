#!/usr/bin/env python3
"""
Tests for TOC Generator and Docs JSON Manager.

These tests verify the deterministic TOC generation from OpenAPI specs
and the docs.json manipulation functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from toc_generator import TOCGenerator
from docs_json_manager import DocsJsonManager
from openapi.openapi_parser import EndpointData


# ============================================================================
# TOCGenerator Tests
# ============================================================================

class TestTOCGenerator:
    """Tests for TOCGenerator class."""

    def test_init_default_base_path(self):
        """Test default base path initialization."""
        generator = TOCGenerator()
        assert generator.openapi_base_path == "openapi/product"

    def test_init_custom_base_path(self):
        """Test custom base path initialization."""
        generator = TOCGenerator(openapi_base_path="api/specs")
        assert generator.openapi_base_path == "api/specs"

    def test_init_strips_trailing_slash(self):
        """Test that trailing slashes are stripped from base path."""
        generator = TOCGenerator(openapi_base_path="openapi/product/")
        assert generator.openapi_base_path == "openapi/product"

    def test_format_page_string(self):
        """Test page string formatting."""
        generator = TOCGenerator(openapi_base_path="openapi/product")
        result = generator._format_page_string(
            yaml_filename="filesets.yaml",
            method="get",
            path="/api/files/v1/filesets"
        )
        assert result == "openapi/product/filesets.yaml GET /api/files/v1/filesets"

    def test_format_page_string_uppercase_method(self):
        """Test that methods are uppercased in page strings."""
        generator = TOCGenerator()
        result = generator._format_page_string("api.yaml", "post", "/users")
        assert "POST" in result
        assert "post" not in result

    def test_group_endpoints_by_tag(self):
        """Test grouping endpoints by their first tag."""
        generator = TOCGenerator()

        # Create mock endpoints
        ep1 = EndpointData()
        ep1.tags = ["Users"]
        ep1.path = "/users"
        ep1.method = "get"

        ep2 = EndpointData()
        ep2.tags = ["Users"]
        ep2.path = "/users/{id}"
        ep2.method = "get"

        ep3 = EndpointData()
        ep3.tags = ["Files"]
        ep3.path = "/files"
        ep3.method = "post"

        grouped = generator._group_endpoints_by_tag([ep1, ep2, ep3])

        assert "Users" in grouped
        assert "Files" in grouped
        assert len(grouped["Users"]) == 2
        assert len(grouped["Files"]) == 1

    def test_group_endpoints_untagged(self):
        """Test that endpoints without tags are grouped as 'Untagged'."""
        generator = TOCGenerator()

        ep = EndpointData()
        ep.tags = []
        ep.path = "/health"
        ep.method = "get"

        grouped = generator._group_endpoints_by_tag([ep])

        assert "Untagged" in grouped
        assert len(grouped["Untagged"]) == 1

    def test_sort_endpoints_by_method(self):
        """Test that endpoints are sorted alphabetically by method."""
        generator = TOCGenerator()

        ep_post = EndpointData()
        ep_post.method = "post"
        ep_post.path = "/users"

        ep_get = EndpointData()
        ep_get.method = "get"
        ep_get.path = "/users"

        ep_delete = EndpointData()
        ep_delete.method = "delete"
        ep_delete.path = "/users"

        sorted_eps = generator._sort_endpoints_by_method([ep_post, ep_get, ep_delete])

        methods = [ep.method.upper() for ep in sorted_eps]
        assert methods == ["DELETE", "GET", "POST"]

    def test_sort_endpoints_by_method_then_path(self):
        """Test that endpoints with same method are sorted by path."""
        generator = TOCGenerator()

        ep1 = EndpointData()
        ep1.method = "get"
        ep1.path = "/users/{id}"

        ep2 = EndpointData()
        ep2.method = "get"
        ep2.path = "/users"

        sorted_eps = generator._sort_endpoints_by_method([ep1, ep2])

        paths = [ep.path for ep in sorted_eps]
        assert paths == ["/users", "/users/{id}"]


class TestTOCGeneratorFlattening:
    """Tests for single-tag flattening behavior."""

    @patch('toc_generator.OpenAPIParser')
    def test_flatten_single_tag_matching_title(self, mock_parser_class):
        """Test that single tag matching title produces flat structure."""
        generator = TOCGenerator(openapi_base_path="openapi/product")

        # Create mock endpoints all with same tag as title
        ep1 = EndpointData()
        ep1.tags = ["Documents"]
        ep1.path = "/files"
        ep1.method = "get"

        ep2 = EndpointData()
        ep2.tags = ["Documents"]
        ep2.path = "/files/{id}"
        ep2.method = "delete"

        # Mock the parser
        mock_parser = MagicMock()
        mock_parser.get_api_info.return_value = {"title": "Documents"}
        mock_parser.parse_all_endpoints.return_value = [ep1, ep2]
        mock_parser_class.return_value = mock_parser

        toc = generator.generate_toc_for_file("Documents.yaml")

        # Should be flat - pages are strings, not dicts
        assert toc["group"] == "Documents"
        assert all(isinstance(p, str) for p in toc["pages"])
        assert len(toc["pages"]) == 2
        # Methods should be sorted alphabetically
        assert "DELETE" in toc["pages"][0]
        assert "GET" in toc["pages"][1]

    @patch('toc_generator.OpenAPIParser')
    def test_flatten_single_tag_case_insensitive(self, mock_parser_class):
        """Test that tag matching is case-insensitive."""
        generator = TOCGenerator(openapi_base_path="openapi/product")

        ep = EndpointData()
        ep.tags = ["documents"]  # lowercase tag
        ep.path = "/files"
        ep.method = "get"

        mock_parser = MagicMock()
        mock_parser.get_api_info.return_value = {"title": "Documents"}  # Title case
        mock_parser.parse_all_endpoints.return_value = [ep]
        mock_parser_class.return_value = mock_parser

        toc = generator.generate_toc_for_file("Documents.yaml")

        # Should be flat even with case mismatch
        assert all(isinstance(p, str) for p in toc["pages"])
        assert toc["group"] == "Documents"

    @patch('toc_generator.OpenAPIParser')
    def test_no_flatten_multiple_tags(self, mock_parser_class):
        """Test that multiple tags produce nested structure."""
        generator = TOCGenerator(openapi_base_path="openapi/product")

        ep1 = EndpointData()
        ep1.tags = ["Files"]
        ep1.path = "/files"
        ep1.method = "get"

        ep2 = EndpointData()
        ep2.tags = ["Users"]
        ep2.path = "/users"
        ep2.method = "get"

        mock_parser = MagicMock()
        mock_parser.get_api_info.return_value = {"title": "FileSets API"}
        mock_parser.parse_all_endpoints.return_value = [ep1, ep2]
        mock_parser_class.return_value = mock_parser

        toc = generator.generate_toc_for_file("filesets.yaml")

        # Should be nested - pages contain dicts
        assert toc["group"] == "FileSets API"
        assert all(isinstance(p, dict) for p in toc["pages"])
        assert len(toc["pages"]) == 2

    @patch('toc_generator.OpenAPIParser')
    def test_no_flatten_single_tag_different_from_title(self, mock_parser_class):
        """Test that single tag not matching title produces nested structure."""
        generator = TOCGenerator(openapi_base_path="openapi/product")

        ep = EndpointData()
        ep.tags = ["Files"]
        ep.path = "/files"
        ep.method = "get"

        mock_parser = MagicMock()
        mock_parser.get_api_info.return_value = {"title": "Storage API"}
        mock_parser.parse_all_endpoints.return_value = [ep]
        mock_parser_class.return_value = mock_parser

        toc = generator.generate_toc_for_file("storage.yaml")

        # Should be nested - single tag doesn't match title
        assert toc["group"] == "Storage API"
        assert len(toc["pages"]) == 1
        assert isinstance(toc["pages"][0], dict)
        assert toc["pages"][0]["group"] == "Files"


class TestTOCGeneratorWithRealYAML:
    """Integration tests using real YAML files."""

    @pytest.fixture
    def sample_yaml_path(self):
        """Get path to sample YAML file."""
        return "./samples/Documents.yaml"

    def test_generate_toc_for_file(self, sample_yaml_path):
        """Test generating TOC from a real YAML file.

        Documents.yaml has a single tag 'Documents' matching its title,
        so it should produce a flattened structure (pages are strings, not dicts).
        """
        if not Path(sample_yaml_path).exists():
            pytest.skip("Sample YAML file not found")

        generator = TOCGenerator(openapi_base_path="openapi/product")
        toc = generator.generate_toc_for_file(sample_yaml_path)

        # Verify structure
        assert "group" in toc
        assert "pages" in toc
        assert isinstance(toc["pages"], list)

        # Verify group name comes from YAML title
        assert toc["group"] == "Documents"

        # Documents.yaml has single tag matching title, so should be flattened
        # Pages should be strings, not nested tag groups
        for page in toc["pages"]:
            assert isinstance(page, str), "Expected flat structure (pages as strings)"
            assert page.startswith("openapi/product/Documents.yaml")
            # Should contain METHOD and path
            parts = page.split(" ")
            assert len(parts) >= 3
            assert parts[1] in ["DELETE", "GET", "PATCH", "POST", "PUT", "HEAD", "OPTIONS"]

    def test_generate_toc_endpoints_sorted_by_method(self, sample_yaml_path):
        """Test that endpoints are sorted alphabetically by method.

        Documents.yaml produces flattened output (single tag matches title),
        so pages are strings directly, not nested tag groups.
        """
        if not Path(sample_yaml_path).exists():
            pytest.skip("Sample YAML file not found")

        generator = TOCGenerator()
        toc = generator.generate_toc_for_file(sample_yaml_path)

        # Documents.yaml has flattened structure - pages are strings directly
        methods = []
        for page in toc["pages"]:
            if isinstance(page, str):
                parts = page.split(" ")
                if len(parts) >= 2:
                    methods.append(parts[1])
            else:
                # Nested structure (for other YAML files with multiple tags)
                for nested_page in page.get("pages", []):
                    parts = nested_page.split(" ")
                    if len(parts) >= 2:
                        methods.append(parts[1])

        # Methods should be in alphabetical order
        assert methods == sorted(methods), "Methods not sorted"


# ============================================================================
# DocsJsonManager Tests
# ============================================================================

class TestDocsJsonManager:
    """Tests for DocsJsonManager class."""

    @pytest.fixture
    def sample_docs_json(self):
        """Create a sample docs.json structure matching real Mintlify format."""
        return {
            "navigation": {
                "languages": [
                    {
                        "language": "en",
                        "tabs": [
                            {
                                "tab": "Developer Portal",
                                "menu": [
                                    {
                                        "item": "Developer Portal",
                                        "groups": [
                                            {
                                                "group": "API Reference",
                                                "pages": [
                                                    "portal/API-Reference/overview",
                                                    {
                                                        "group": "Product APIs",
                                                        "pages": [
                                                            {
                                                                "group": "Existing API",
                                                                "pages": [
                                                                    "openapi/product/existing.yaml GET /test"
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

    @pytest.fixture
    def temp_docs_json(self, sample_docs_json):
        """Create a temporary docs.json file."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_docs_json, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_load_docs_json(self, temp_docs_json):
        """Test loading docs.json file."""
        manager = DocsJsonManager(temp_docs_json)
        data = manager.load()

        assert data is not None
        assert "navigation" in data

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        manager = DocsJsonManager("/nonexistent/path/docs.json")

        with pytest.raises(FileNotFoundError):
            manager.load()

    def test_find_product_apis_pages(self, temp_docs_json):
        """Test finding the Product APIs pages array."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        pages = manager.find_product_apis_pages()

        assert pages is not None
        assert len(pages) == 1
        assert pages[0]["group"] == "Existing API"

    def test_find_product_apis_pages_not_loaded(self, temp_docs_json):
        """Test that finding pages raises error if not loaded."""
        manager = DocsJsonManager(temp_docs_json)

        with pytest.raises(ValueError, match="No data loaded"):
            manager.find_product_apis_pages()

    def test_insert_new_group(self, temp_docs_json):
        """Test inserting a new TOC group."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        new_entry = {
            "group": "New API",
            "pages": [
                {
                    "group": "Users",
                    "pages": ["openapi/product/new.yaml GET /users"]
                }
            ]
        }

        result = manager.insert_or_replace_group("New API", new_entry)

        assert result is True
        pages = manager.find_product_apis_pages()
        assert len(pages) == 2
        assert any(p.get("group") == "New API" for p in pages)

    def test_replace_existing_group(self, temp_docs_json):
        """Test replacing an existing TOC group."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        updated_entry = {
            "group": "Existing API",
            "pages": [
                {
                    "group": "Updated Tag",
                    "pages": ["openapi/product/existing.yaml POST /new-endpoint"]
                }
            ]
        }

        result = manager.insert_or_replace_group("Existing API", updated_entry)

        assert result is True
        pages = manager.find_product_apis_pages()
        assert len(pages) == 1  # Should still be 1, not 2
        assert pages[0]["pages"][0]["group"] == "Updated Tag"

    def test_save_docs_json(self, temp_docs_json):
        """Test saving docs.json file."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        new_entry = {
            "group": "Test API",
            "pages": []
        }
        manager.insert_or_replace_group("Test API", new_entry)
        manager.save()

        # Reload and verify
        with open(temp_docs_json, "r") as f:
            saved_data = json.load(f)

        # Navigate to Product APIs
        product_apis = saved_data["navigation"]["languages"][0]["tabs"][0]["menu"][0]["groups"][0]["pages"][1]
        assert len(product_apis["pages"]) == 2

    def test_save_without_load(self, temp_docs_json):
        """Test that saving without loading raises error."""
        manager = DocsJsonManager(temp_docs_json)

        with pytest.raises(ValueError, match="No data loaded"):
            manager.save()

    def test_get_existing_groups(self, temp_docs_json):
        """Test getting list of existing group names."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        groups = manager.get_existing_groups()

        assert "Existing API" in groups

    def test_remove_group(self, temp_docs_json):
        """Test removing a TOC group."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        result = manager.remove_group("Existing API")

        assert result is True
        pages = manager.find_product_apis_pages()
        assert len(pages) == 0

    def test_remove_nonexistent_group(self, temp_docs_json):
        """Test removing a group that doesn't exist."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        result = manager.remove_group("Nonexistent API")

        assert result is False

    def test_insert_multiple_groups(self, temp_docs_json):
        """Test inserting multiple TOC groups at once."""
        manager = DocsJsonManager(temp_docs_json)
        manager.load()

        entries = [
            {"group": "API 1", "pages": []},
            {"group": "API 2", "pages": []},
            {"group": "API 3", "pages": []}
        ]

        count = manager.insert_multiple_groups(entries)

        assert count == 3
        pages = manager.find_product_apis_pages()
        assert len(pages) == 4  # 1 existing + 3 new


# ============================================================================
# Integration Tests
# ============================================================================

class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.fixture
    def sample_docs_json_for_integration(self):
        """Create a realistic docs.json structure."""
        return {
            "navigation": {
                "languages": [
                    {
                        "language": "en",
                        "tabs": [
                            {
                                "tab": "Developer Portal",
                                "menu": [
                                    {
                                        "item": "Developer Portal",
                                        "groups": [
                                            {
                                                "group": "API Reference",
                                                "pages": [
                                                    {
                                                        "group": "Product APIs",
                                                        "pages": []
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

    @pytest.fixture
    def temp_docs_json_integration(self, sample_docs_json_for_integration):
        """Create a temporary docs.json file for integration tests."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False
        ) as f:
            json.dump(sample_docs_json_for_integration, f)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_full_workflow(self, temp_docs_json_integration):
        """Test complete workflow: generate TOC and insert into docs.json."""
        yaml_path = "./samples/Documents.yaml"
        if not Path(yaml_path).exists():
            pytest.skip("Sample YAML file not found")

        # Generate TOC
        generator = TOCGenerator(openapi_base_path="openapi/product")
        toc_entry = generator.generate_toc_for_file(yaml_path)

        # Insert into docs.json
        manager = DocsJsonManager(temp_docs_json_integration)
        manager.load()
        result = manager.insert_or_replace_group(toc_entry["group"], toc_entry)
        manager.save()

        assert result is True

        # Reload and verify
        manager2 = DocsJsonManager(temp_docs_json_integration)
        manager2.load()
        pages = manager2.find_product_apis_pages()

        assert len(pages) == 1
        assert pages[0]["group"] == "Documents"
        # Documents.yaml has flattened structure (single tag matches title)
        # so pages are strings directly, not nested tag groups
        assert len(pages[0]["pages"]) > 0
        assert all(isinstance(p, str) for p in pages[0]["pages"])

    def test_idempotent_updates(self, temp_docs_json_integration):
        """Test that running the workflow twice produces the same result."""
        yaml_path = "./samples/Documents.yaml"
        if not Path(yaml_path).exists():
            pytest.skip("Sample YAML file not found")

        generator = TOCGenerator(openapi_base_path="openapi/product")

        # First run
        toc_entry = generator.generate_toc_for_file(yaml_path)
        manager = DocsJsonManager(temp_docs_json_integration)
        manager.load()
        manager.insert_or_replace_group(toc_entry["group"], toc_entry)
        manager.save()

        # Second run
        toc_entry2 = generator.generate_toc_for_file(yaml_path)
        manager2 = DocsJsonManager(temp_docs_json_integration)
        manager2.load()
        manager2.insert_or_replace_group(toc_entry2["group"], toc_entry2)
        manager2.save()

        # Verify still only one entry
        manager3 = DocsJsonManager(temp_docs_json_integration)
        manager3.load()
        pages = manager3.find_product_apis_pages()

        assert len(pages) == 1
        assert pages[0]["group"] == "Documents"
