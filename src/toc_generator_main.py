#!/usr/bin/env python3
# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

"""
TOC Generator Main Entry Point

Generates Mintlify-compatible TOC entries from OpenAPI YAML files
and inserts them into docs.json navigation structure.
"""

import os
import sys
import shutil
from pathlib import Path

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from log import Log
from env_vars import EnvVars
from toc_generator import TOCGenerator
from docs_json_manager import DocsJsonManager


def main():
    """Main entry point for TOC generation."""
    Log.print_blue("=" * 60)
    Log.print_blue("TOC Generator - Mintlify docs.json Navigation Builder")
    Log.print_blue("=" * 60)

    try:
        # Load and validate environment variables
        env = EnvVars()
        env.check_vars()

        # Get YAML files to process
        yaml_files = env.get_yaml_files_to_process()

        if not yaml_files:
            Log.print_yellow("No YAML files to process. Exiting.")
            return 0

        Log.print_green(f"Processing {len(yaml_files)} YAML file(s)")

        # Initialize TOC generator
        generator = TOCGenerator(openapi_base_path=env.openapi_base_path)

        # Generate TOC entries for all YAML files
        toc_entries = generator.generate_toc_for_files(yaml_files)

        if not toc_entries:
            Log.print_red("No TOC entries generated. Check YAML files for errors.")
            return 1

        Log.print_green(f"Generated {len(toc_entries)} TOC entries")

        # Load docs.json and insert TOC entries
        manager = DocsJsonManager(env.docs_json_path)
        manager.load()

        groups_updated = manager.insert_multiple_groups(toc_entries)

        # Save updated docs.json
        manager.save()

        Log.print_green(f"Updated {groups_updated} groups in docs.json")

        # Optionally copy YAML files to destination
        if env.yaml_copy_destination:
            copy_yaml_files(yaml_files, env.yaml_copy_destination)

        # Set GitHub Actions outputs if running in CI
        set_github_outputs(len(yaml_files), groups_updated)

        Log.print_blue("=" * 60)
        Log.print_green("TOC generation complete!")
        Log.print_blue(f"  Files processed: {len(yaml_files)}")
        Log.print_blue(f"  Groups updated: {groups_updated}")
        Log.print_blue("=" * 60)

        return 0

    except FileNotFoundError as e:
        Log.print_red(f"File not found: {e}")
        return 1
    except ValueError as e:
        Log.print_red(f"Configuration error: {e}")
        return 1
    except Exception as e:
        Log.print_red(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def copy_yaml_files(yaml_files: list, destination: str) -> int:
    """
    Copy YAML files to a destination directory.

    Args:
        yaml_files: List of YAML file paths
        destination: Destination directory path

    Returns:
        Number of files copied
    """
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)

    copied = 0
    for yaml_file in yaml_files:
        src = Path(yaml_file)
        dst = dest_path / src.name

        try:
            shutil.copy2(src, dst)
            Log.print_green(f"Copied: {src.name} -> {destination}")
            copied += 1
        except Exception as e:
            Log.print_red(f"Failed to copy {src.name}: {e}")

    Log.print_green(f"Copied {copied}/{len(yaml_files)} YAML files to {destination}")
    return copied


def set_github_outputs(files_processed: int, groups_updated: int):
    """
    Set GitHub Actions outputs if running in CI.

    Args:
        files_processed: Number of YAML files processed
        groups_updated: Number of groups updated in docs.json
    """
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        try:
            with open(github_output, "a") as f:
                f.write(f"files_processed={files_processed}\n")
                f.write(f"groups_updated={groups_updated}\n")
            Log.print_green("Set GitHub Actions outputs")
        except Exception as e:
            Log.print_yellow(f"Could not set GitHub outputs: {e}")


if __name__ == "__main__":
    sys.exit(main())
