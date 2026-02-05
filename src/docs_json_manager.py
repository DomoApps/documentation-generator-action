# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

"""
Docs JSON Manager - Handles reading, modifying, and writing Mintlify docs.json files.

This module manages the insertion and replacement of TOC entries in docs.json,
specifically targeting the Product APIs group in the navigation structure.
"""

import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from log import Log


class ExpandedJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that always expands arrays to one element per line.

    Python's default json.dump() collapses single-element arrays onto one line:
        "pages": ["s/article/000005139"]

    This encoder ensures arrays are always expanded:
        "pages": [
          "s/article/000005139"
        ]
    """

    def encode(self, obj: Any) -> str:
        return self._encode(obj, 0)

    def _encode(self, obj: Any, level: int) -> str:
        indent = "  " * level
        next_indent = "  " * (level + 1)

        if isinstance(obj, dict):
            if not obj:
                return "{}"
            items = [
                f'{next_indent}"{k}": {self._encode(v, level + 1)}'
                for k, v in obj.items()
            ]
            return "{\n" + ",\n".join(items) + f"\n{indent}}}"

        elif isinstance(obj, list):
            if not obj:
                return "[]"
            items = [f"{next_indent}{self._encode(v, level + 1)}" for v in obj]
            return "[\n" + ",\n".join(items) + f"\n{indent}]"

        return json.dumps(obj, ensure_ascii=False)


class DocsJsonManager:
    """
    Manages Mintlify docs.json file operations.

    Navigates to: Developer Portal → menu → groups → API Reference → pages → Product APIs → pages
    """

    def __init__(self, docs_json_path: str):
        """
        Initialize the docs.json manager.

        Args:
            docs_json_path: Path to the docs.json file
        """
        self.docs_json_path = Path(docs_json_path)
        self._data: Optional[Dict[str, Any]] = None
        Log.print_green(f"DocsJsonManager initialized for: {docs_json_path}")

    def load(self) -> Dict[str, Any]:
        """Load the docs.json file."""
        if not self.docs_json_path.exists():
            raise FileNotFoundError(f"docs.json not found at: {self.docs_json_path}")

        Log.print_green(f"Loading docs.json from: {self.docs_json_path}")

        with open(self.docs_json_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        return self._data

    def save(self) -> None:
        """Save the current data back to docs.json."""
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        Log.print_green(f"Saving docs.json to: {self.docs_json_path}")

        with open(self.docs_json_path, "w", encoding="utf-8") as f:
            f.write(ExpandedJSONEncoder().encode(self._data))
            f.write("\n")

        Log.print_green("docs.json saved successfully")

    def _find_in_list(self, items: List[Any], key: str, value: str) -> Optional[Dict[str, Any]]:
        """Find a dict in a list where dict[key] == value."""
        for item in items:
            if isinstance(item, dict) and item.get(key) == value:
                return item
        return None

    def find_product_apis_pages(self, language: str = "en") -> Optional[List[Any]]:
        """
        Find the pages array within the Product APIs group.

        Path: navigation.languages[lang].tabs[Developer Portal].menu[0].groups[API Reference].pages[Product APIs].pages

        Args:
            language: Language code (default: "en")

        Returns:
            The pages list from Product APIs, or None if not found
        """
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        try:
            navigation = self._data.get("navigation", {})
            languages = navigation.get("languages", [])

            # Find language config (array format)
            lang_config = None
            if isinstance(languages, list):
                lang_config = self._find_in_list(languages, "language", language)
            elif isinstance(languages, dict):
                lang_config = languages.get(language)

            if not lang_config:
                Log.print_red(f"Language config not found for: {language}")
                return None

            # Find Developer Portal tab
            tabs = lang_config.get("tabs", [])
            dev_portal_tab = self._find_in_list(tabs, "tab", "Developer Portal")
            if not dev_portal_tab:
                Log.print_red("Developer Portal tab not found")
                return None

            # Navigate through menu → groups → API Reference
            menu = dev_portal_tab.get("menu", [])
            if not menu:
                Log.print_red("No menu found in Developer Portal tab")
                return None

            # First menu item contains groups
            menu_item = menu[0] if menu else None
            if not menu_item:
                Log.print_red("No menu item found")
                return None

            groups = menu_item.get("groups", [])
            api_ref = self._find_in_list(groups, "group", "API Reference")
            if not api_ref:
                Log.print_red("API Reference group not found")
                return None

            # Find Product APIs within API Reference
            api_ref_pages = api_ref.get("pages", [])
            product_apis = self._find_in_list(api_ref_pages, "group", "Product APIs")
            if not product_apis:
                Log.print_red("Product APIs group not found")
                return None

            pages = product_apis.get("pages", [])
            Log.print_green(f"Found Product APIs with {len(pages)} existing entries")
            return pages

        except (KeyError, TypeError, IndexError) as e:
            Log.print_red(f"Error navigating docs.json structure: {e}")
            return None

    def insert_or_replace_group(
        self,
        group_name: str,
        toc_entry: Dict[str, Any],
        language: str = "en"
    ) -> bool:
        """
        Insert a new TOC group or replace an existing one with the same name.

        Args:
            group_name: The name of the group to insert/replace
            toc_entry: The TOC entry dictionary to insert
            language: Language code (default: "en")

        Returns:
            True if successful, False otherwise
        """
        pages = self.find_product_apis_pages(language)
        if pages is None:
            Log.print_red("Cannot insert group: Product APIs not found")
            return False

        # Look for existing group with the same name
        for i, page in enumerate(pages):
            if isinstance(page, dict) and page.get("group") == group_name:
                Log.print_green(f"Replacing existing group: {group_name}")
                pages[i] = toc_entry
                return True

        # No existing group found, append new one
        Log.print_green(f"Adding new group: {group_name}")
        pages.append(toc_entry)
        return True

    def insert_multiple_groups(
        self,
        toc_entries: List[Dict[str, Any]],
        language: str = "en"
    ) -> int:
        """
        Insert or replace multiple TOC groups.

        Args:
            toc_entries: List of TOC entry dictionaries to insert
            language: Language code (default: "en")

        Returns:
            Number of groups successfully inserted/replaced
        """
        successful = 0
        for entry in toc_entries:
            group_name = entry.get("group", "Unknown")
            if self.insert_or_replace_group(group_name, entry, language):
                successful += 1

        Log.print_green(f"Successfully processed {successful}/{len(toc_entries)} groups")
        return successful

    def remove_group(self, group_name: str, language: str = "en") -> bool:
        """Remove a TOC group by name."""
        pages = self.find_product_apis_pages(language)
        if pages is None:
            return False

        for i, page in enumerate(pages):
            if isinstance(page, dict) and page.get("group") == group_name:
                Log.print_green(f"Removing group: {group_name}")
                pages.pop(i)
                return True

        Log.print_yellow(f"Group not found: {group_name}")
        return False

    def get_existing_groups(self, language: str = "en") -> List[str]:
        """Get a list of existing group names in Product APIs."""
        pages = self.find_product_apis_pages(language)
        if pages is None:
            return []

        groups = []
        for page in pages:
            if isinstance(page, dict) and "group" in page:
                groups.append(page["group"])

        return groups

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """Get the current loaded data."""
        return self._data
