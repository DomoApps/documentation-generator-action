#!/usr/bin/env python3
"""
Sync generated markdown files to destination paths based on mapping configuration.

This script:
1. Reads the mapping configuration
2. Maps each generated markdown file to its destination
3. Auto-updates mapping config for new files
4. Copies files to destination maintaining structure
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List


def load_mapping_config(mapping_file: str) -> Dict:
    """Load the file mapping configuration"""
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            return json.load(f)
    else:
        # Return default structure
        return {
            "source_base": "api-docs/public",
            "dest_base": "docs/API-Reference/Product-APIs",
            "file_mappings": {},
            "default_rule": {
                "pattern": "*.yaml",
                "output": "{basename}.md"
            }
        }


def save_mapping_config(mapping_file: str, config: Dict):
    """Save updated mapping configuration"""
    with open(mapping_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Updated mapping configuration: {mapping_file}")


def get_yaml_to_md_mapping(yaml_file: str, mapping_config: Dict, source_base: str) -> str:
    """Determine markdown destination for a YAML source file"""
    # Get relative path from source base
    rel_path = os.path.relpath(yaml_file, source_base)
    base_name = Path(rel_path).stem

    # Check if explicit mapping exists
    if rel_path in mapping_config.get("file_mappings", {}):
        return mapping_config["file_mappings"][rel_path]

    # Apply default rule
    default_rule = mapping_config.get("default_rule", {})
    output_pattern = default_rule.get("output", "{basename}.md")
    return output_pattern.replace("{basename}", base_name)


def sync_files(
    generated_dir: str,
    destination_dir: str,
    mapping_config: Dict,
    changed_list_file: str
) -> List[str]:
    """
    Sync generated markdown files to destination

    Returns:
        List of newly added mappings
    """
    new_mappings = []
    source_base = mapping_config.get("source_base", "api-docs/public")

    # Read list of changed YAML files
    if not os.path.exists(changed_list_file):
        print(f"Changed list file not found: {changed_list_file}")
        return new_mappings

    with open(changed_list_file, 'r') as f:
        changed_yaml_files = [line.strip() for line in f if line.strip()]

    print(f"Syncing {len(changed_yaml_files)} files...")

    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    for yaml_file in changed_yaml_files:
        # Get the generated markdown file name (basename only, in generated_dir)
        yaml_basename = Path(yaml_file).stem
        generated_md = os.path.join(generated_dir, f"{yaml_basename}.md")

        if not os.path.exists(generated_md):
            print(f"WARNING: Generated file not found: {generated_md}")
            continue

        # Determine destination based on mapping
        dest_filename = get_yaml_to_md_mapping(yaml_file, mapping_config, source_base)
        dest_path = os.path.join(destination_dir, dest_filename)

        # Check if this is a new mapping
        yaml_rel_path = os.path.relpath(yaml_file, source_base) if source_base else os.path.basename(yaml_file)
        if yaml_rel_path not in mapping_config.get("file_mappings", {}):
            # Add new mapping
            if "file_mappings" not in mapping_config:
                mapping_config["file_mappings"] = {}
            mapping_config["file_mappings"][yaml_rel_path] = dest_filename
            new_mappings.append((yaml_rel_path, dest_filename))
            print(f"NEW MAPPING: {yaml_rel_path} -> {dest_filename}")

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy file to destination
        shutil.copy2(generated_md, dest_path)
        print(f"SYNCED: {generated_md} -> {dest_path}")

    return new_mappings


def main():
    parser = argparse.ArgumentParser(description='Sync generated docs to destination')
    parser.add_argument('--generated', required=True, help='Directory with generated markdown files')
    parser.add_argument('--destination', required=True, help='Destination directory for markdown files')
    parser.add_argument('--mapping', required=True, help='Path to mapping configuration file')
    parser.add_argument('--changed-list', required=True, help='File containing list of changed YAML files')

    args = parser.parse_args()

    # Load mapping configuration
    mapping_config = load_mapping_config(args.mapping)

    # Sync files
    new_mappings = sync_files(
        args.generated,
        args.destination,
        mapping_config,
        args.changed_list
    )

    # Save updated configuration if new mappings were added
    if new_mappings:
        save_mapping_config(args.mapping, mapping_config)
        print(f"\nAdded {len(new_mappings)} new mapping(s):")
        for source, dest in new_mappings:
            print(f"  - {source} -> {dest}")

    print(f"\n{'='*60}")
    print(f"Sync complete: {len(new_mappings)} new mappings added")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
