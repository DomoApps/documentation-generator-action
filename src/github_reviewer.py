# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import os
from git import Git 
from pathlib import Path
from ai.chat_gpt import ChatGPT
from openai import OpenAI
from ai.ai_bot import AiBot
from log import Log
from env_vars import EnvVars
from repository.github import GitHub
from repository.repository import RepositoryError

separator = "\n\n----------------------------------------------------------------------\n\n"

def main():
    with open('output.txt', 'a') as log_file:
        vars = EnvVars()
        vars.check_vars()
        model = OpenAI(api_key = vars.chat_gpt_token)
        ai = ChatGPT(model, vars.chat_gpt_model, vars.focus_areas)
        github = GitHub(vars.token, vars.owner, vars.repo, vars.pull_number)

        remote_name = Git.get_remote_name()
        Log.print_green("Remote is", remote_name)
        changed_files = Git.get_diff_files(remote_name=remote_name, head_ref=vars.head_ref, base_ref=vars.base_ref)
        Log.print_green("Found changes in files", changed_files)
        if len(changed_files) == 0: 
            Log.print_red("No changes between branch")

        for file in changed_files:
            Log.print_green("Checking file", file)

            _, file_extension = os.path.splitext(file)
            file_extension = file_extension.lstrip('.')
            if file_extension not in vars.target_extensions:
                Log.print_yellow(f"Skipping, unsuported extension {file_extension} file {file}")
                continue

            try:
                with open(file, 'r') as file_opened:
                    file_content = file_opened.read()
            except FileNotFoundError:
                Log.print_yellow("File was removed. Continue.", file)
                continue

            if len(file_content) == 0: 
                Log.print_red("File is empty")
                continue

            file_diffs = Git.get_diff_in_file(remote_name=remote_name, head_ref=vars.head_ref, base_ref=vars.base_ref, file_path=file)
            if len(file_diffs) == 0: 
                Log.print_red("Diffs are empty")

            Log.print_green(f"Asking AI. Content Len:{len(file_content)} Diff Len: {len(file_diffs)}")
            # take the diff, and add an incrementing number to each line after the hunk header
            formatted_diff = Git.prep_diff_for_ai(file_diffs)
            response = ai.ai_request_diffs(code=file_content, diffs=formatted_diff)

            log_file.write(f"{separator}{file_content}{separator}{formatted_diff}{separator}{response}{separator}")

            Log.print_green("Fetching git diff...")
            Log.print_green(f"Git diff for file {file}:")
            # Log.print_green(formatted_diff)

            Log.print_green("AI response:")
            Log.print_green(response)

            if AiBot.is_no_issues_text(response):
                Log.print_green("File looks good. Continue", file)
            else:
                responses = AiBot.split_ai_response(response)
                if len(responses) == 0:
                    Log.print_red("Responses where not parsed:", responses)

                Log.print_green("Checking if responses are empty...")
                if len(responses) == 0:
                    Log.print_red("Responses are empty. Skipping get_existing_comments.")
                else:
                    Log.print_green("Responses are not empty. Proceeding to fetch existing comments.")
                    # Fetch existing comments from the GitHub repository
                    Log.print_green("Fetching existing comments from GitHub...")
                    existing_comments = github.get_existing_comments()
                    Log.print_green(f"Existing comments fetched: {existing_comments}")
                    existing_positions = {comment['position'] for comment in existing_comments if 'position' in comment}

                    # Filter out responses that have matching positions with existing comments
                    responses = [response for response in responses if response.position not in existing_positions]

                    result = False
                    for response in responses:
                        Log.print_green(f"Processing AI response: position={response.line}, text={response.text}")
                        result = post_line_comment(github=github, file=file, text=response.text, line=response.line)
                        if not result:
                            Log.print_yellow(f"Posting general comment for file {file}")
                            result = post_general_comment(github=github, file=file, text=response.text)
                        if not result:
                            Log.print_red("Failed to post any comments.")
                            raise RepositoryError("Failed to post any comments.")
                    
def post_line_comment(github: GitHub, file: str, text:str, line: int):
    Log.print_green("Posting line", file, line, text)
    try:
        git_response = github.post_comment_to_line(
            text=text, 
            commit_id=Git.get_last_commit_sha(file=file), 
            file_path=file, 
            position=line,
        )
        Log.print_yellow("Posted", git_response)
        return True
    except RepositoryError as e:
        Log.print_red("Failed line comment", e)
        return False

def post_general_comment(github: GitHub, file: str, text:str) -> bool:
    Log.print_green("Posting general", file, text)
    try:
        message = f"{file}\n{text}"
        git_response = github.post_comment_general(message)
        Log.print_yellow("Posted general", git_response)
        return True
    except RepositoryError:
        Log.print_red("Failed general comment")
        return False

if __name__ == "__main__":
    main()