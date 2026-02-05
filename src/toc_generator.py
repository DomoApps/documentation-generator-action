# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

"""
TOC Generator - Generates Mintlify-compatible TOC JSON from OpenAPI YAML files.

This module provides deterministic generation of table of contents entries
for Mintlify documentation from OpenAPI specifications.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from log import Log
from openapi.openapi_parser import OpenAPIParser, EndpointData


class TOCGenerator:
    """
    Generates Mintlify-compatible TOC JSON from OpenAPI YAML files.

    The generated TOC structure follows the Mintlify docs.json format:
    {
        "group": "API Title from YAML",
        "pages": [
            {
                "group": "Tag Name",
                "pages": [
                    "openapi/product/filename.yaml METHOD /path"
                ]
            }
        ]
    }
    """

    def __init__(self, openapi_base_path: str = "openapi/product"):
        """
        Initialize the TOC generator.

        Args:
            openapi_base_path: Base path prefix for OpenAPI references in page strings.
                             Example: "openapi/product" results in pages like
                             "openapi/product/api.yaml GET /users"
        """
        self.openapi_base_path = openapi_base_path.rstrip("/")
        Log.print_green(f"TOCGenerator initialized with base path: {self.openapi_base_path}")

    def generate_toc_for_file(self, yaml_path: str) -> Dict[str, Any]:
        """
        Generate a TOC entry for a single OpenAPI YAML file.

        Args:
            yaml_path: Path to the OpenAPI YAML file

        Returns:
            Dictionary representing the TOC entry with group and pages
        """
        Log.print_green(f"Generating TOC for: {yaml_path}")

        # Parse the OpenAPI spec
        parser = OpenAPIParser(yaml_path)
        api_info = parser.get_api_info()
        endpoints = parser.parse_all_endpoints()

        # Get the filename for page references
        yaml_filename = Path(yaml_path).name

        # Group endpoints by tag
        endpoints_by_tag = self._group_endpoints_by_tag(endpoints)
        api_title = api_info.get("title", yaml_filename)

        # Check for single-tag scenario that matches title (case-insensitive)
        tag_names = list(endpoints_by_tag.keys())
        should_flatten = (
            len(tag_names) == 1 and
            tag_names[0].lower() == api_title.lower()
        )

        if should_flatten:
            # Flatten: put endpoints directly under the group (no nested tag group)
            all_endpoints = endpoints_by_tag[tag_names[0]]
            sorted_endpoints = self._sort_endpoints_by_method(all_endpoints)
            pages = [
                self._format_page_string(yaml_filename, ep.method, ep.path)
                for ep in sorted_endpoints
            ]
            toc_entry = {
                "group": api_title,
                "pages": pages
            }
            Log.print_green(f"Generated flattened TOC with {len(pages)} endpoints (single tag matching title)")
        else:
            # Normal: nested tag groups
            toc_entry = {
                "group": api_title,
                "pages": []
            }

            # Sort tags alphabetically for consistent output
            for tag in sorted(endpoints_by_tag.keys()):
                tag_endpoints = endpoints_by_tag[tag]

                # Sort endpoints by method (alphabetically)
                sorted_endpoints = self._sort_endpoints_by_method(tag_endpoints)

                # Format page strings
                pages = [
                    self._format_page_string(yaml_filename, ep.method, ep.path)
                    for ep in sorted_endpoints
                ]

                tag_group = {
                    "group": tag,
                    "pages": pages
                }
                toc_entry["pages"].append(tag_group)

            Log.print_green(f"Generated TOC with {len(toc_entry['pages'])} tag groups")

        return toc_entry

    def generate_toc_for_directory(self, yaml_dir: str) -> List[Dict[str, Any]]:
        """
        Generate TOC entries for all YAML files in a directory.

        Args:
            yaml_dir: Path to directory containing YAML files

        Returns:
            List of TOC entries, one per YAML file
        """
        yaml_dir_path = Path(yaml_dir)
        if not yaml_dir_path.exists():
            Log.print_red(f"Directory not found: {yaml_dir}")
            return []

        toc_entries = []
        yaml_files = list(yaml_dir_path.glob("*.yaml")) + list(yaml_dir_path.glob("*.yml"))

        Log.print_green(f"Found {len(yaml_files)} YAML files in {yaml_dir}")

        for yaml_file in sorted(yaml_files):
            try:
                toc_entry = self.generate_toc_for_file(str(yaml_file))
                toc_entries.append(toc_entry)
            except Exception as e:
                Log.print_red(f"Error processing {yaml_file}: {e}")
                continue

        return toc_entries

    def generate_toc_for_files(self, yaml_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Generate TOC entries for a specific list of YAML files.

        Args:
            yaml_paths: List of paths to YAML files

        Returns:
            List of TOC entries, one per YAML file
        """
        toc_entries = []

        Log.print_green(f"Processing {len(yaml_paths)} YAML files")

        for yaml_path in sorted(yaml_paths):
            try:
                toc_entry = self.generate_toc_for_file(yaml_path)
                toc_entries.append(toc_entry)
            except Exception as e:
                Log.print_red(f"Error processing {yaml_path}: {e}")
                continue

        return toc_entries

    def _group_endpoints_by_tag(self, endpoints: List[EndpointData]) -> Dict[str, List[EndpointData]]:
        """
        Group endpoints by their first tag.

        Args:
            endpoints: List of EndpointData objects

        Returns:
            Dictionary mapping tag names to lists of endpoints
        """
        grouped: Dict[str, List[EndpointData]] = {}

        for endpoint in endpoints:
            # Use first tag, or "Untagged" if no tags
            tag = endpoint.tags[0] if endpoint.tags else "Untagged"

            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(endpoint)

        return grouped

    def _sort_endpoints_by_method(self, endpoints: List[EndpointData]) -> List[EndpointData]:
        """
        Sort endpoints alphabetically by HTTP method, then by path.

        Args:
            endpoints: List of EndpointData objects

        Returns:
            Sorted list of endpoints
        """
        # Sort by method (alphabetically: DELETE, GET, PATCH, POST, PUT)
        # Then by path for consistent ordering
        return sorted(endpoints, key=lambda ep: (ep.method.upper(), ep.path))

    def _format_page_string(self, yaml_filename: str, method: str, path: str) -> str:
        """
        Format a page string for Mintlify docs.json.

        Args:
            yaml_filename: Name of the YAML file (e.g., "filesets.yaml")
            method: HTTP method (e.g., "get", "post")
            path: API path (e.g., "/api/files/v1/filesets")

        Returns:
            Formatted page string like "openapi/product/filesets.yaml GET /api/files/v1/filesets"
        """
        return f"{self.openapi_base_path}/{yaml_filename} {method.upper()} {path}"
