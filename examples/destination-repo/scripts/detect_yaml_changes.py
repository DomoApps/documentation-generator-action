#!/usr/bin/env python3
"""
Detect changed YAML files in source repository and determine which need regeneration.

This script:
1. Compares source YAML files with destination markdown files
2. Checks file modification times and content hashes
3. Outputs list of files that need regeneration
4. Creates summary of changes for PR description
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file content"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}", file=sys.stderr)
        return ""


def load_mapping_config(mapping_file: str) -> Dict:
    """Load the file mapping configuration"""
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            return json.load(f)
    else:
        # Return default structure if config doesn't exist
        return {
            "source_base": "api-docs/public",
            "dest_base": "docs/API-Reference/Product-APIs",
            "file_mappings": {},
            "default_rule": {
                "pattern": "*.yaml",
                "output": "{basename}.md"
            }
        }


def get_destination_path(source_file: str, mapping_config: Dict, source_base: str) -> str:
    """Determine destination path for a source file based on mapping config"""
    # Get relative path from source base
    rel_path = os.path.relpath(source_file, source_base)
    base_name = Path(rel_path).stem

    # Check if explicit mapping exists
    if rel_path in mapping_config.get("file_mappings", {}):
        return mapping_config["file_mappings"][rel_path]

    # Apply default rule
    default_rule = mapping_config.get("default_rule", {})
    output_pattern = default_rule.get("output", "{basename}.md")
    return output_pattern.replace("{basename}", base_name)


def find_yaml_files(source_dir: str) -> List[str]:
    """Find all YAML files in source directory"""
    yaml_files = []
    source_path = Path(source_dir)

    for ext in ['*.yaml', '*.yml']:
        yaml_files.extend(source_path.glob(f"**/{ext}"))

    return [str(f) for f in yaml_files]


def detect_changes(
    source_dir: str,
    dest_dir: str,
    mapping_config: Dict,
    force: bool = False
) -> Tuple[List[str], Dict[str, str]]:
    """
    Detect which YAML files need regeneration

    Returns:
        Tuple of (changed_files, summary_dict)
    """
    changed_files = []
    summary = {
        "new_files": [],
        "modified_files": [],
        "unchanged_files": []
    }

    yaml_files = find_yaml_files(source_dir)
    print(f"Found {len(yaml_files)} YAML files in source")

    for yaml_file in yaml_files:
        rel_path = os.path.relpath(yaml_file, source_dir)
        dest_file_name = get_destination_path(yaml_file, mapping_config, source_dir)
        dest_file_path = os.path.join(dest_dir, dest_file_name)

        # Check if destination exists
        if not os.path.exists(dest_file_path):
            print(f"NEW: {rel_path} -> {dest_file_name}")
            changed_files.append(yaml_file)
            summary["new_files"].append(rel_path)
            continue

        # If force flag set, mark all as changed
        if force:
            print(f"FORCE: {rel_path}")
            changed_files.append(yaml_file)
            summary["modified_files"].append(rel_path)
            continue

        # Compare modification times
        source_mtime = os.path.getmtime(yaml_file)
        dest_mtime = os.path.getmtime(dest_file_path)

        if source_mtime > dest_mtime:
            print(f"MODIFIED: {rel_path} (source newer than dest)")
            changed_files.append(yaml_file)
            summary["modified_files"].append(rel_path)
        else:
            print(f"UNCHANGED: {rel_path}")
            summary["unchanged_files"].append(rel_path)

    return changed_files, summary


def create_summary_markdown(summary: Dict[str, List[str]]) -> str:
    """Create markdown summary of changes"""
    lines = []

    total_changes = len(summary["new_files"]) + len(summary["modified_files"])
    lines.append(f"**Total files requiring update:** {total_changes}")
    lines.append("")

    if summary["new_files"]:
        lines.append(f"**New Files ({len(summary['new_files'])}):**")
        for f in summary["new_files"]:
            lines.append(f"- 🆕 `{f}`")
        lines.append("")

    if summary["modified_files"]:
        lines.append(f"**Modified Files ({len(summary['modified_files'])}):**")
        for f in summary["modified_files"]:
            lines.append(f"- 📝 `{f}`")
        lines.append("")

    if summary["unchanged_files"]:
        lines.append(f"**Unchanged Files ({len(summary['unchanged_files'])}):**")
        lines.append(f"_{len(summary['unchanged_files'])} files are already up-to-date_")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Detect changed YAML files')
    parser.add_argument('--source', required=True, help='Source directory with YAML files')
    parser.add_argument('--dest', required=True, help='Destination directory with markdown files')
    parser.add_argument('--mapping', required=True, help='Path to mapping configuration file')
    parser.add_argument('--force', default='false', help='Force regenerate all files')

    args = parser.parse_args()
    force = args.force.lower() == 'true'

    # Load mapping configuration
    mapping_config = load_mapping_config(args.mapping)

    # Detect changes
    changed_files, summary = detect_changes(
        args.source,
        args.dest,
        mapping_config,
        force=force
    )

    # Write changed files list to file for next step
    with open('changed_files.txt', 'w') as f:
        for file_path in changed_files:
            f.write(f"{file_path}\n")

    # Write changed files as newline-separated string for GitHub Actions
    changed_files_str = "\n".join(changed_files)
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"changed_files<<EOF\n{changed_files_str}\nEOF\n")

    # Create and output summary
    summary_md = create_summary_markdown(summary)
    with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
        f.write(f"summary<<EOF\n{summary_md}\nEOF\n")

    print(f"\n{'='*60}")
    print(f"Detection complete: {len(changed_files)} files need regeneration")
    print(f"{'='*60}")

    # Exit with appropriate code
    sys.exit(0 if changed_files else 1)


if __name__ == "__main__":
    main()
