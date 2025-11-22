#!/usr/bin/env python3
"""
Check if a PR already exists for a specific file.

This script prevents duplicate PRs by checking if an open PR already exists
for the given branch name pattern.

Usage:
    python check_existing_prs.py --file-name filesets.yaml --branch-prefix docs/update-api-docs
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_branch_name_for_file(file_path: str, branch_prefix: str) -> str:
    """Generate a consistent branch name for a file."""
    # Extract just the filename without extension
    file_name = Path(file_path).stem
    # Create a branch name like: docs/update-api-docs-filesets
    return f"{branch_prefix}-{file_name}"


def check_existing_pr(branch_name: str) -> dict:
    """
    Check if a PR already exists for the given branch name.

    Returns:
        dict with keys:
            - exists: bool - True if PR exists
            - number: int - PR number if exists
            - title: str - PR title if exists
            - url: str - PR URL if exists
    """
    try:
        # Query GitHub for open PRs with this branch name
        result = subprocess.run(
            [
                'gh', 'pr', 'list',
                '--state', 'open',
                '--head', branch_name,
                '--json', 'number,title,url',
                '--limit', '1'
            ],
            capture_output=True,
            text=True,
            check=True
        )

        prs = json.loads(result.stdout)

        if prs:
            pr = prs[0]
            return {
                'exists': True,
                'number': pr['number'],
                'title': pr['title'],
                'url': pr['url']
            }
        else:
            return {'exists': False}

    except subprocess.CalledProcessError as e:
        print(f"Error checking for existing PRs: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        # If gh command fails, assume no PR exists to allow creation
        return {'exists': False}
    except json.JSONDecodeError as e:
        print(f"Error parsing GitHub CLI output: {e}", file=sys.stderr)
        return {'exists': False}


def main():
    parser = argparse.ArgumentParser(
        description='Check if a PR already exists for a specific file'
    )
    parser.add_argument(
        '--file-name',
        required=True,
        help='Name of the file (e.g., filesets.yaml)'
    )
    parser.add_argument(
        '--branch-prefix',
        default='docs/update-api-docs',
        help='Branch name prefix (default: docs/update-api-docs)'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )

    args = parser.parse_args()

    # Generate branch name for this file
    branch_name = get_branch_name_for_file(args.file_name, args.branch_prefix)

    # Check if PR exists
    pr_info = check_existing_pr(branch_name)

    # Output results
    if args.output_format == 'json':
        print(json.dumps({
            'branch_name': branch_name,
            'pr_exists': pr_info['exists'],
            'pr_info': pr_info
        }))
    else:
        if pr_info['exists']:
            print(f"✓ PR already exists for {args.file_name}")
            print(f"  Branch: {branch_name}")
            print(f"  PR #{pr_info['number']}: {pr_info['title']}")
            print(f"  URL: {pr_info['url']}")
            sys.exit(1)  # Exit with error code to signal PR exists
        else:
            print(f"✗ No PR exists for {args.file_name}")
            print(f"  Branch: {branch_name}")
            sys.exit(0)  # Exit with success to signal no PR exists


if __name__ == '__main__':
    main()
