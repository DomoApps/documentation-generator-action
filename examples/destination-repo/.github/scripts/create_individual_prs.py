#!/usr/bin/env python3
"""
Create individual pull requests for each changed YAML file with proper file mapping.

This script:
1. Reads the list of changed YAML files
2. For each file:
   - Checks if an open PR already exists (skip if so)
   - Creates a new branch for the file
   - Runs the sync script to map temp docs to destination paths
   - Commits the changes to the destination paths
   - Creates a PR for the changes
3. Handles git operations, branch management, and PR creation
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class PRCreator:
    """Handles creation of individual PRs with file syncing"""

    def __init__(
        self,
        changed_files_list: str,
        temp_dir: str,
        dest_dir: str,
        mapping_file: str,
        sync_script: str,
        base_branch: str = "master",
        pr_branch_prefix: str = "doc-bot",
        openai_model: str = "gpt-4o",
        max_iterations: str = "3",
        completeness_threshold: str = "90",
        repo: str = None
    ):
        self.changed_files_list = changed_files_list
        self.temp_dir = temp_dir
        self.dest_dir = dest_dir
        self.mapping_file = mapping_file
        self.sync_script = sync_script
        self.base_branch = base_branch
        self.pr_branch_prefix = pr_branch_prefix
        self.openai_model = openai_model
        self.max_iterations = max_iterations
        self.completeness_threshold = completeness_threshold
        self.repo = repo

        self.processed = 0
        self.failed = 0
        self.skipped = 0

    def run_command(self, cmd: List[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"   Error: {e.stderr if e.stderr else e.stdout}")
            raise

    def git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command"""
        return self.run_command(["git"] + args, check=check)

    def gh_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a gh (GitHub CLI) command"""
        return self.run_command(["gh"] + args, check=check)

    def check_pr_exists(self, branch_name: str) -> Optional[int]:
        """Check if an open PR exists for the given branch"""
        try:
            result = self.gh_command([
                "pr", "list",
                "--state", "open",
                "--head", branch_name,
                "--json", "number",
                "--jq", ".[0].number"
            ], check=False)

            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip())
            return None
        except (ValueError, subprocess.CalledProcessError):
            return None

    def create_or_checkout_branch(self, branch_name: str) -> bool:
        """Create or checkout a branch"""
        try:
            # Fetch latest
            self.git_command(["fetch", "origin"], check=False)

            # Checkout base branch first (force to overwrite any conflicts)
            print(f"Returning to base branch...")
            self.git_command(["checkout", "-f", self.base_branch], check=False)

            # Check if branch exists locally
            local_branches = self.git_command(["branch", "--list", branch_name], check=False)
            branch_exists_locally = branch_name in local_branches.stdout

            # Check if branch exists remotely
            result = self.git_command([
                "ls-remote", "--heads", "origin", branch_name
            ], check=False)
            branch_exists_remotely = bool(result.stdout.strip())

            if branch_exists_remotely:
                # Branch exists remotely
                print(f"Branch exists remotely: {branch_name}")

                if branch_exists_locally:
                    # Delete local branch to avoid conflicts
                    print(f"Deleting local branch to refresh from remote...")
                    self.git_command(["branch", "-D", branch_name], check=False)

                # Checkout from remote with tracking (force to overwrite conflicts)
                print(f"Checking out from remote with tracking...")
                self.git_command(["checkout", "-f", "-b", branch_name, f"origin/{branch_name}"])

            else:
                # Create new branch from base
                print(f"Creating new branch: {branch_name}")
                self.git_command(["checkout", "-b", branch_name])

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create/checkout branch: {e}")
            return False

    def sync_file(self, yaml_file: str) -> bool:
        """Run sync script for a single file"""
        # Create temp file list with single file
        temp_file_list = "temp_single_file.txt"
        try:
            with open(temp_file_list, 'w') as f:
                f.write(yaml_file + '\n')

            print(f"🔄 Syncing file to destination with mapping...")
            result = self.run_command([
                "python",
                self.sync_script,
                "--generated", self.temp_dir,
                "--destination", self.dest_dir,
                "--mapping", self.mapping_file,
                "--changed-list", temp_file_list
            ], check=False)

            os.remove(temp_file_list)

            if result.returncode != 0:
                print(f"❌ Sync script failed")
                return False

            return True
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            if os.path.exists(temp_file_list):
                os.remove(temp_file_list)
            return False

    def stage_and_commit(self, yaml_file: str, file_name: str) -> Optional[str]:
        """Stage changes and commit"""
        try:
            # Stage destination directory files
            self.git_command(["add", f"{self.dest_dir}/**/*.md"], check=False)
            self.git_command(["add", f"{self.dest_dir}/*.md"], check=False)

            # Stage mapping file if it was updated
            self.git_command(["add", self.mapping_file], check=False)

            # Check if there are changes to commit
            result = self.git_command([
                "diff", "--cached", "--name-only"
            ], check=False)

            if not result.stdout.strip():
                print(f"ℹ️ No changes to commit for {file_name}")
                return None

            # Get the mapped file name for commit message
            mapped_files = [line for line in result.stdout.strip().split('\n') if line.endswith('.md')]
            mapped_file = mapped_files[0] if mapped_files else "unknown"

            # Configure git
            self.git_command(["config", "user.name", "github-actions[bot]"])
            self.git_command(["config", "user.email", "github-actions[bot]@users.noreply.github.com"])

            # Commit
            self.git_command([
                "commit",
                "-m", f"📚 Update documentation for {file_name}",
                "-m", "Auto-generated from YAML specification",
                "-m", f"Source: {yaml_file}",
                "-m", f"Destination: {mapped_file}"
            ])

            return mapped_file
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Commit failed: {e}")
            return None

    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote"""
        try:
            self.git_command(["push", "-f", "origin", branch_name])
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push failed: {e}")
            return False

    def create_pr(self, branch_name: str, file_name: str, yaml_file: str, mapped_file: str) -> Optional[str]:
        """Create a pull request"""
        try:
            pr_body = f"""## 🤖 Auto-Generated Documentation Update

This PR contains automatically generated documentation for a single API spec.

### 📊 File Details
- **Source File:** `{yaml_file}`
- **Generated File:** `{mapped_file}`
- **AI Model Used:** {self.openai_model}

### 🔄 Process Details
- Generated documentation from OpenAPI/YAML specification
- Applied file mapping configuration
- Max Iterations: {self.max_iterations}
- Quality Threshold: {self.completeness_threshold}%

---
🤖 This PR was created automatically by the documentation sync workflow.

Please review the generated documentation before merging."""

            cmd = [
                "pr", "create",
                "--title", f"📚 Update documentation for {file_name}",
                "--body", pr_body,
                "--head", branch_name,
                "--base", self.base_branch
            ]

            # Add repo flag if specified
            if self.repo:
                cmd.extend(["--repo", self.repo])

            result = self.gh_command(cmd, check=False)

            if result.returncode == 0 and result.stdout.strip().startswith("https://"):
                return result.stdout.strip()
            else:
                print(f"⚠️ PR creation failed: {result.stderr if result.stderr else result.stdout}")
                return None
        except subprocess.CalledProcessError as e:
            print(f"⚠️ PR creation failed: {e}")
            return None

    def return_to_base_branch(self):
        """Return to base branch"""
        try:
            self.git_command(["checkout", self.base_branch], check=False)
        except subprocess.CalledProcessError:
            pass  # Best effort

    def process_file(self, yaml_file: str) -> bool:
        """Process a single file"""
        file_name = os.path.basename(yaml_file)
        file_base = Path(file_name).stem
        branch_name = f"{self.pr_branch_prefix}/{file_base}"
        temp_md = os.path.join(self.temp_dir, f"{file_base}.md")

        print("---")
        print(f"Processing: {file_name}")
        print(f"Branch: {branch_name}")

        # Check if generated file exists
        if not os.path.exists(temp_md):
            print(f"⚠️ Generated file not found: {temp_md}")
            self.failed += 1
            return False

        # Check if PR already exists
        pr_number = self.check_pr_exists(branch_name)
        if pr_number:
            print(f"⏭️ Skipping - PR #{pr_number} already exists")
            self.skipped += 1
            return True

        # Create or checkout branch
        if not self.create_or_checkout_branch(branch_name):
            self.failed += 1
            self.return_to_base_branch()
            return False

        # Run sync script
        if not self.sync_file(yaml_file):
            self.failed += 1
            self.return_to_base_branch()
            return False

        # Stage and commit
        mapped_file = self.stage_and_commit(yaml_file, file_name)
        if not mapped_file:
            self.return_to_base_branch()
            return True  # No changes, not a failure

        # Push
        if not self.push_branch(branch_name):
            self.failed += 1
            self.return_to_base_branch()
            return False

        # Create PR
        pr_url = self.create_pr(branch_name, file_name, yaml_file, mapped_file)
        if pr_url:
            print(f"✅ Created PR: {pr_url}")
            self.processed += 1
        else:
            self.failed += 1

        # Return to base branch
        self.return_to_base_branch()

        return pr_url is not None

    def process_all_files(self) -> Dict[str, int]:
        """Process all files in the changed files list"""
        print("📄 Creating individual PRs with proper file mapping...")

        if not os.path.exists(self.changed_files_list):
            print(f"❌ Changed files list not found: {self.changed_files_list}")
            sys.exit(1)

        with open(self.changed_files_list, 'r') as f:
            files = [line.strip() for line in f if line.strip()]

        if not files:
            print("⚠️ No files to process")
            return {
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0
            }

        for yaml_file in files:
            self.process_file(yaml_file)

        print("")
        print(f"📊 Summary:")
        print(f"  - Total: {len(files)}")
        print(f"  - Processed: {self.processed}")
        print(f"  - Skipped: {self.skipped}")
        print(f"  - Failed: {self.failed}")

        return {
            "processed": self.processed,
            "failed": self.failed,
            "skipped": self.skipped,
            "total": len(files)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Create individual PRs for changed YAML files with file mapping'
    )
    parser.add_argument(
        '--changed-list',
        required=True,
        help='File containing list of changed YAML files'
    )
    parser.add_argument(
        '--temp-dir',
        required=True,
        help='Directory with generated markdown files'
    )
    parser.add_argument(
        '--dest-dir',
        required=True,
        help='Destination directory for markdown files'
    )
    parser.add_argument(
        '--mapping-file',
        required=True,
        help='Path to mapping configuration file'
    )
    parser.add_argument(
        '--sync-script',
        required=True,
        help='Path to sync_to_destination.py script'
    )
    parser.add_argument(
        '--base-branch',
        default='master',
        help='Base branch to create PRs from (default: master)'
    )
    parser.add_argument(
        '--pr-branch-prefix',
        default='doc-bot',
        help='Branch name prefix for PRs (default: doc-bot)'
    )
    parser.add_argument(
        '--openai-model',
        default='gpt-4o',
        help='OpenAI model used for generation (for PR description)'
    )
    parser.add_argument(
        '--max-iterations',
        default='3',
        help='Max iterations used (for PR description)'
    )
    parser.add_argument(
        '--completeness-threshold',
        default='90',
        help='Completeness threshold used (for PR description)'
    )
    parser.add_argument(
        '--repo',
        default=None,
        help='GitHub repository in owner/repo format (e.g., DomoApps/domo-developer-portal)'
    )

    args = parser.parse_args()

    creator = PRCreator(
        changed_files_list=args.changed_list,
        temp_dir=args.temp_dir,
        dest_dir=args.dest_dir,
        mapping_file=args.mapping_file,
        sync_script=args.sync_script,
        base_branch=args.base_branch,
        pr_branch_prefix=args.pr_branch_prefix,
        openai_model=args.openai_model,
        max_iterations=args.max_iterations,
        completeness_threshold=args.completeness_threshold,
        repo=args.repo
    )

    results = creator.process_all_files()

    # Exit with error if any failed
    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
