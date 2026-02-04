#!/usr/bin/env python3
"""
Create individual pull requests for each enhanced YAML file.

This script:
1. Reads the list of changed YAML files
2. For each file:
   - Checks if an open PR already exists (skip if so)
   - Creates a new branch for the file
   - Syncs the enhanced YAML to destination (same filename)
   - Commits the changes
   - Creates a PR for the changes
3. Handles git operations, branch management, and PR creation
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class PRCreator:
    """Handles creation of individual PRs for enhanced YAML files"""

    def __init__(
        self,
        changed_files_list: str,
        temp_dir: str,
        dest_dir: str,
        base_branch: str = "master",
        pr_branch_prefix: str = "yaml-enhance",
        openai_model: str = "gpt-4o",
        max_iterations: str = "3",
        quality_threshold: str = "85",
        repo: str = None
    ):
        self.changed_files_list = changed_files_list
        self.temp_dir = temp_dir
        self.dest_dir = dest_dir
        self.base_branch = base_branch
        self.pr_branch_prefix = pr_branch_prefix
        self.openai_model = openai_model
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
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

    def sync_file(self, yaml_file: str, yaml_filename: str) -> Optional[str]:
        """Copy enhanced YAML file to destination"""
        try:
            # Source: enhanced YAML in temp directory
            enhanced_yaml = os.path.join(self.temp_dir, yaml_filename)

            if not os.path.exists(enhanced_yaml):
                print(f"❌ Enhanced file not found: {enhanced_yaml}")
                return None

            # Destination: same filename in destination directory
            dest_path = os.path.join(self.dest_dir, yaml_filename)

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copy file
            shutil.copy2(enhanced_yaml, dest_path)
            print(f"🔄 Synced: {enhanced_yaml} -> {dest_path}")

            return dest_path
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return None

    def stage_and_commit(self, yaml_file: str, file_name: str, dest_path: str) -> bool:
        """Stage changes and commit"""
        try:
            # Stage destination file
            self.git_command(["add", dest_path])

            # Check if there are changes to commit
            result = self.git_command([
                "diff", "--cached", "--name-only"
            ], check=False)

            if not result.stdout.strip():
                print(f"ℹ️ No changes to commit for {file_name}")
                return False

            # Configure git
            self.git_command(["config", "user.name", "github-actions[bot]"])
            self.git_command(["config", "user.email", "github-actions[bot]@users.noreply.github.com"])

            # Commit
            self.git_command([
                "commit",
                "-m", f"📝 Enhance YAML specification: {file_name}",
                "-m", "AI-enhanced OpenAPI specification with improved descriptions",
                "-m", f"Source: {yaml_file}",
                "-m", f"Destination: {dest_path}"
            ])

            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Commit failed: {e}")
            return False

    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote"""
        try:
            self.git_command(["push", "-f", "origin", branch_name])
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push failed: {e}")
            return False

    def create_pr(self, branch_name: str, file_name: str, yaml_file: str, dest_path: str) -> Optional[str]:
        """Create a pull request"""
        try:
            pr_body = f"""## 📝 AI-Enhanced OpenAPI Specification

This PR contains an AI-enhanced OpenAPI YAML specification with improved descriptions.

### 📊 File Details
- **Source File:** `{yaml_file}`
- **Enhanced File:** `{dest_path}`
- **AI Model Used:** {self.openai_model}

### 🎯 Enhancements Applied
- Missing info.description fields
- Parameter descriptions
- Schema descriptions
- Property descriptions
- Tag descriptions

### 🔄 Process Details
- Enhanced with AI-generated contextual descriptions
- Original YAML structure, comments, and formatting preserved
- Quality Threshold: {self.quality_threshold}%
- Max Iterations: {self.max_iterations}

---
🤖 This PR was created automatically by the YAML enhancement workflow.

All enhancements have been validated for quality and accuracy. Please review before merging."""

            cmd = [
                "pr", "create",
                "--title", f"📝 Enhance OpenAPI spec: {file_name}",
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

        print("---")
        print(f"Processing: {file_name}")
        print(f"Branch: {branch_name}")

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

        # Sync enhanced YAML file
        dest_path = self.sync_file(yaml_file, file_name)
        if not dest_path:
            self.failed += 1
            self.return_to_base_branch()
            return False

        # Stage and commit
        if not self.stage_and_commit(yaml_file, file_name, dest_path):
            self.return_to_base_branch()
            return True  # No changes, not a failure

        # Push
        if not self.push_branch(branch_name):
            self.failed += 1
            self.return_to_base_branch()
            return False

        # Create PR
        pr_url = self.create_pr(branch_name, file_name, yaml_file, dest_path)
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
        print("📄 Creating individual PRs for enhanced YAML files...")

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
        description='Create individual PRs for enhanced YAML files'
    )
    parser.add_argument(
        '--changed-list',
        required=True,
        help='File containing list of changed YAML files'
    )
    parser.add_argument(
        '--temp-dir',
        required=True,
        help='Directory with enhanced YAML files'
    )
    parser.add_argument(
        '--dest-dir',
        required=True,
        help='Destination directory for YAML files'
    )
    parser.add_argument(
        '--base-branch',
        default='master',
        help='Base branch to create PRs from (default: master)'
    )
    parser.add_argument(
        '--pr-branch-prefix',
        default='yaml-enhance',
        help='Branch name prefix for PRs (default: yaml-enhance)'
    )
    parser.add_argument(
        '--openai-model',
        default='gpt-4o',
        help='OpenAI model used for enhancement (for PR description)'
    )
    parser.add_argument(
        '--max-iterations',
        default='3',
        help='Max iterations used (for PR description)'
    )
    parser.add_argument(
        '--quality-threshold',
        default='85',
        help='Quality threshold used (for PR description)'
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
        base_branch=args.base_branch,
        pr_branch_prefix=args.pr_branch_prefix,
        openai_model=args.openai_model,
        max_iterations=args.max_iterations,
        quality_threshold=args.quality_threshold,
        repo=args.repo
    )

    results = creator.process_all_files()

    # Exit with error if any failed
    if results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
