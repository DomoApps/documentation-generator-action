#!/usr/bin/env python3
"""
Tests for DocsJsonManager locating the "Product APIs" group.

The group has lived in two places in the hub's docs.json:
  - legacy:  Developer Portal tab -> menu[0].groups[API Reference].pages[Product APIs]
  - current: Developer Portal tab -> pages[...].pages[Product APIs]
"""

import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from docs_json_manager import DocsJsonManager  # noqa: E402

EXISTING = [
    {"group": "AI Services", "pages": ["openapi/product/AI-Services.yaml POST /api/ai/v1/extract"]},
    {"group": "Users", "pages": ["openapi/product/Users.yaml GET /api/users"]},
]


def _legacy_docs():
    return {
        "navigation": {
            "languages": [
                {
                    "language": "en",
                    "tabs": [
                        {"tab": "Guides", "pages": ["guides/intro"]},
                        {
                            "tab": "Developer Portal",
                            "menu": [
                                {
                                    "groups": [
                                        {
                                            "group": "API Reference",
                                            "pages": [{"group": "Product APIs", "pages": copy.deepcopy(EXISTING)}],
                                        }
                                    ]
                                }
                            ],
                        },
                    ],
                }
            ]
        }
    }


def _current_docs():
    return {
        "navigation": {
            "languages": [
                {
                    "language": "en",
                    "tabs": [
                        {"tab": "Guides", "pages": ["guides/intro"]},
                        {
                            "tab": "Developer Portal",
                            "pages": [
                                {"group": "Getting Started", "pages": ["dev/start"]},
                                {
                                    "group": "API Reference",
                                    "pages": [
                                        "dev/api-overview",
                                        "dev/api-auth",
                                        "dev/api-limits",
                                        {"group": "Product APIs", "pages": copy.deepcopy(EXISTING)},
                                    ],
                                },
                            ],
                        },
                    ],
                }
            ]
        }
    }


def _manager(tmp_path, docs):
    path = tmp_path / "docs.json"
    path.write_text(json.dumps(docs))
    manager = DocsJsonManager(str(path))
    manager.load()
    return manager, path


@pytest.mark.parametrize("make_docs", [_legacy_docs, _current_docs], ids=["legacy-menu", "current-pages"])
class TestFindsProductApis:
    def test_lists_existing_groups(self, tmp_path, make_docs):
        manager, _ = _manager(tmp_path, make_docs())
        assert manager.get_existing_groups() == ["AI Services", "Users"]

    def test_inserts_new_group_alphabetically(self, tmp_path, make_docs):
        manager, path = _manager(tmp_path, make_docs())
        entry = {"group": "Documents", "pages": ["openapi/product/Documents.yaml GET /api/documents"]}

        assert manager.insert_multiple_groups([entry]) == 1
        assert manager.get_existing_groups() == ["AI Services", "Documents", "Users"]

        manager.save()
        reloaded = DocsJsonManager(str(path))
        reloaded.load()
        assert reloaded.get_existing_groups() == ["AI Services", "Documents", "Users"]

    def test_replaces_existing_group(self, tmp_path, make_docs):
        manager, _ = _manager(tmp_path, make_docs())
        entry = {"group": "Users", "pages": ["openapi/product/Users.yaml GET /api/v2/users"]}

        assert manager.insert_multiple_groups([entry]) == 1
        assert manager.get_existing_groups() == ["AI Services", "Users"]
        pages = manager.find_product_apis_pages()
        assert pages[1]["pages"] == ["openapi/product/Users.yaml GET /api/v2/users"]

    def test_does_not_touch_other_tabs(self, tmp_path, make_docs):
        manager, _ = _manager(tmp_path, make_docs())
        manager.insert_multiple_groups([{"group": "Documents", "pages": ["x"]}])
        tabs = manager.data["navigation"]["languages"][0]["tabs"]
        assert tabs[0] == {"tab": "Guides", "pages": ["guides/intro"]}


class TestMissingStructure:
    def test_returns_none_without_product_apis(self, tmp_path):
        docs = _current_docs()
        docs["navigation"]["languages"][0]["tabs"][1]["pages"] = [{"group": "Getting Started", "pages": ["a"]}]
        manager, _ = _manager(tmp_path, docs)

        assert manager.find_product_apis_pages() is None
        assert manager.insert_multiple_groups([{"group": "Documents", "pages": ["x"]}]) == 0

    def test_ignores_product_apis_outside_developer_portal(self, tmp_path):
        docs = _current_docs()
        docs["navigation"]["languages"][0]["tabs"][1]["pages"] = []
        docs["navigation"]["languages"][0]["tabs"][0]["pages"].append(
            {"group": "Product APIs", "pages": []}
        )
        manager, _ = _manager(tmp_path, docs)

        assert manager.find_product_apis_pages() is None

    def test_returns_none_without_developer_portal_tab(self, tmp_path):
        docs = _current_docs()
        docs["navigation"]["languages"][0]["tabs"] = [{"tab": "Guides", "pages": ["a"]}]
        manager, _ = _manager(tmp_path, docs)

        assert manager.find_product_apis_pages() is None
