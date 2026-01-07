"""
YAML Preserver Module

Handles loading, modifying, and saving YAML files while preserving:
- Comments (inline and block)
- Formatting (indentation, line breaks)
- Key ordering
- Anchors and aliases ($ref structures)

Uses ruamel.yaml for comment-preserving operations.
"""

import sys
import os
from typing import Any, Optional
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

sys.path.insert(0, os.path.dirname(__file__))
from log import Log


class YAMLPreserver:
    """
    Handles YAML modifications while preserving structure, comments, and formatting.
    """

    def __init__(self):
        """Initialize the YAML preserver with ruamel.yaml configuration."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 4096  # Prevent line wrapping
        self.yaml.indent(mapping=2, sequence=2, offset=0)

    def load_with_comments(self, yaml_path: str) -> Optional[CommentedMap]:
        """
        Load YAML file preserving all comments and structure.

        Args:
            yaml_path: Path to the YAML file

        Returns:
            CommentedMap object representing the YAML structure, or None if loading fails

        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            Exception: If YAML parsing fails
        """
        try:
            path = Path(yaml_path)
            if not path.exists():
                Log.print_red(f"YAML file not found: {yaml_path}")
                raise FileNotFoundError(f"YAML file not found: {yaml_path}")

            with open(yaml_path, 'r', encoding='utf-8') as file:
                data = self.yaml.load(file)

            Log.print_green(f"Successfully loaded YAML with comments: {yaml_path}")
            return data

        except Exception as e:
            Log.print_red(f"Error loading YAML file {yaml_path}: {e}")
            raise

    def set_value_at_path(self, yaml_obj: CommentedMap, path: str, value: Any) -> bool:
        """
        Set a value at a specific YAML path without disturbing formatting or order.

        Supports dot notation for nested paths:
        - "info.description" -> yaml_obj['info']['description']
        - "tags.0.description" -> yaml_obj['tags'][0]['description']

        Args:
            yaml_obj: The CommentedMap object to modify
            path: Dot-separated path (e.g., "info.description", "tags.0.name")
            value: The value to set

        Returns:
            True if successful, False otherwise
        """
        try:
            path_parts = path.split('.')
            current = yaml_obj

            # Navigate to the parent of the target field
            for i, part in enumerate(path_parts[:-1]):
                # Handle array indices
                if part.isdigit():
                    current = current[int(part)]
                else:
                    # Create intermediate objects if they don't exist
                    if part not in current:
                        current[part] = CommentedMap()
                    current = current[part]

            # Set the final value
            final_key = path_parts[-1]
            if final_key.isdigit():
                current[int(final_key)] = value
            else:
                current[final_key] = value

            Log.print_green(f"Successfully set value at path: {path}")
            return True

        except (KeyError, IndexError, TypeError) as e:
            Log.print_red(f"Error setting value at path '{path}': {e}")
            return False

    def get_value_at_path(self, yaml_obj: CommentedMap, path: str) -> Optional[Any]:
        """
        Get a value at a specific YAML path.

        Args:
            yaml_obj: The CommentedMap object to query
            path: Dot-separated path (e.g., "info.description")

        Returns:
            The value at the path, or None if not found
        """
        try:
            path_parts = path.split('.')
            current = yaml_obj

            for part in path_parts:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]

            return current

        except (KeyError, IndexError, TypeError):
            return None

    def save_with_preservation(self, yaml_obj: CommentedMap, output_path: str) -> bool:
        """
        Save YAML preserving all original formatting, comments, and structure.

        Args:
            yaml_obj: The CommentedMap object to save
            output_path: Path where the YAML should be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as file:
                self.yaml.dump(yaml_obj, file)

            Log.print_green(f"Successfully saved YAML with preservation: {output_path}")
            return True

        except Exception as e:
            Log.print_red(f"Error saving YAML file {output_path}: {e}")
            return False

    def apply_enhancements(
        self,
        yaml_path: str,
        enhancements: dict[str, Any],
        output_path: Optional[str] = None
    ) -> bool:
        """
        Apply multiple enhancements to a YAML file while preserving structure.

        Args:
            yaml_path: Path to the source YAML file
            enhancements: Dictionary mapping YAML paths to new values
                         e.g., {"info.description": "New description", "info.title": "New title"}
            output_path: Optional output path (defaults to yaml_path for in-place modification)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the YAML
            yaml_obj = self.load_with_comments(yaml_path)
            if yaml_obj is None:
                return False

            # Apply all enhancements
            success_count = 0
            for path, value in enhancements.items():
                if self.set_value_at_path(yaml_obj, path, value):
                    success_count += 1

            if success_count == 0:
                Log.print_yellow("No enhancements were successfully applied")
                return False

            # Save the enhanced YAML
            save_path = output_path if output_path else yaml_path
            result = self.save_with_preservation(yaml_obj, save_path)

            if result:
                Log.print_green(
                    f"Successfully applied {success_count}/{len(enhancements)} enhancements to {save_path}"
                )

            return result

        except Exception as e:
            Log.print_red(f"Error applying enhancements: {e}")
            return False

    def validate_yaml_structure(self, yaml_path: str) -> bool:
        """
        Validate that a YAML file can be loaded and has valid structure.

        Args:
            yaml_path: Path to the YAML file

        Returns:
            True if valid, False otherwise
        """
        try:
            yaml_obj = self.load_with_comments(yaml_path)
            return yaml_obj is not None
        except Exception:
            return False
