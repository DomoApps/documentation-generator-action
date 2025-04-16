# Apache License
# Version 2.0, January 2004
# Author: Eugene Tkachenko

import subprocess
from typing import List
from log import Log

class Git:

    @staticmethod
    def __run_subprocess(options):
        Log.print_green(options)
        result = subprocess.run(options, stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            Log.print_red(options)
            raise Exception(f"Error running {options}: {result.stderr}")

    @staticmethod
    def get_remote_name() -> str:
        command = ["git", "remote", "-v"]
        result = Git.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0]

    @staticmethod
    def get_last_commit_sha(file) -> str:
        command = ["git", "log", "-1", "--format=\"%H\"", "--", file]
        result = Git.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0].replace('"', "")
        
    @staticmethod
    def get_diff_files(remote_name, head_ref, base_ref) -> List[str]:
        command = ["git", "diff", "--name-only", f"{remote_name}/{base_ref}", f"{remote_name}/{head_ref}"]
        result = Git.__run_subprocess(command)
        return result.strip().splitlines()
        
    @staticmethod
    def get_diff_in_file(remote_name, head_ref, base_ref, file_path) -> str:
        command = ["git", "diff", f"{remote_name}/{base_ref}", f"{remote_name}/{head_ref}", "--", file_path]
        return Git.__run_subprocess(command)

    @staticmethod
    def prep_diff_for_ai(diff: str) -> str:
        lines = diff.splitlines()
        processed_lines = []
        line_number = 1
        inside_diff = False

        for line in lines:
            # Skip headers above the actual diff
            if not inside_diff:
                if line.startswith('@@'):
                    inside_diff = True
                continue

            # Skip hunk headers
            if line.startswith('@@'):
                continue

            # Handle empty lines explicitly as a single space for context lines
            if not line.strip():
                processed_lines.append(f"{line_number} ")  # Single space for empty lines
            else:
                # Prepend each line with an incrementing number without modifying the content
                processed_lines.append(f"{line_number}{line}")
            line_number += 1

        return '\n'.join(processed_lines)