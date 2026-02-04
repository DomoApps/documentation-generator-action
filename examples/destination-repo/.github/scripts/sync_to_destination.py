#!/usr/bin/env python3
"""
Sync enhanced YAML files to destination paths preserving relative structure.

This script:
1. Reads the list of changed YAML files
2. Copies enhanced YAML files from temp directory to destination
3. Maintains the same relative paths and filenames
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List


def sync_files(
    source_yaml_dir: str,
    enhanced_yaml_dir: str,
    destination_dir: str,
    changed_list_file: str
) -> List[str]:
    """
    Sync enhanced YAML files to destination maintaining structure

    Args:
        source_yaml_dir: Original source directory (for calculating relative paths)
        enhanced_yaml_dir: Directory with enhanced YAML files
        destination_dir: Destination directory for enhanced YAML files
        changed_list_file: File containing list of changed YAML files

    Returns:
        List of synced files
    """
    synced_files = []

    # Read list of changed YAML files
    if not os.path.exists(changed_list_file):
        print(f"Changed list file not found: {changed_list_file}")
        return synced_files

    with open(changed_list_file, 'r') as f:
        changed_yaml_files = [line.strip() for line in f if line.strip()]

    print(f"Syncing {len(changed_yaml_files)} files...")

    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    for yaml_file in changed_yaml_files:
        # Get the filename
        yaml_filename = os.path.basename(yaml_file)

        # Find enhanced file in temp directory
        enhanced_yaml = os.path.join(enhanced_yaml_dir, yaml_filename)

        if not os.path.exists(enhanced_yaml):
            print(f"WARNING: Enhanced file not found: {enhanced_yaml}")
            continue

        # Determine destination path (preserve relative structure if needed)
        # For now, keep flat structure - all YAML files go to dest_dir root
        dest_path = os.path.join(destination_dir, yaml_filename)

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy file to destination
        shutil.copy2(enhanced_yaml, dest_path)
        print(f"SYNCED: {enhanced_yaml} -> {dest_path}")
        synced_files.append(dest_path)

    return synced_files


def main():
    parser = argparse.ArgumentParser(description='Sync enhanced YAML files to destination')
    parser.add_argument('--source', required=True, help='Source YAML directory (for relative paths)')
    parser.add_argument('--enhanced', required=True, help='Directory with enhanced YAML files')
    parser.add_argument('--destination', required=True, help='Destination directory for YAML files')
    parser.add_argument('--changed-list', required=True, help='File containing list of changed YAML files')

    args = parser.parse_args()

    # Sync files
    synced_files = sync_files(
        args.source,
        args.enhanced,
        args.destination,
        args.changed_list
    )

    print(f"\n{'='*60}")
    print(f"Sync complete: {len(synced_files)} file(s) synced")
    print(f"{'='*60}")

    for file in synced_files:
        print(f"  ✓ {file}")


if __name__ == "__main__":
    main()
