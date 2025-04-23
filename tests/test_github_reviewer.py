import sys
import os
sys.path.append('../src')

import os
from unittest.mock import patch, MagicMock, ANY
from github_reviewer import main
from unittest.mock import mock_open

@patch.dict(os.environ, {
    "REPO_OWNER": "fake-owner",
    "REPO_NAME": "fake-repo",
    "PULL_NUMBER": "1",
    "GITHUB_TOKEN": "fake-token",
    "GITHUB_BASE_REF": "main",
    "GITHUB_HEAD_REF": "develop",
    "CHATGPT_KEY": "fake-chatgpt-key",
    "CHATGPT_MODEL": "gpt-4",
    "TARGET_EXTENSIONS": "py,js",
    "FOCUS_AREAS": "performance,security",
})
@patch("github_reviewer.Git")
@patch("github_reviewer.GitHub")
@patch("github_reviewer.ChatGPT")
@patch("builtins.open", new_callable=mock_open, read_data="print('Hello')")
def test_main(mock_file, mock_chat_gpt, mock_github, mock_git):
    # Mock Git methods
    mock_git.get_remote_name.return_value = "origin"
    mock_git.get_diff_files.return_value = ["example.py"]
    mock_git.get_diff_in_file.return_value = "@@ -1 +1 @@\n-print('Hello')\n+print('Hello, world!')"
    mock_git.get_last_commit_sha.return_value = "abc123"

    main()

    # Ensure file operations are completed within the block
    assert mock_file.call_count == 2  # Adjusted to expect 2 calls

    # Assertions
    mock_git.get_diff_in_file.assert_called_once_with(
        remote_name="origin", head_ref=ANY, base_ref=ANY, file_path="example.py"
    )

@patch.dict(os.environ, {
    "REPO_OWNER": "fake-owner",
    "REPO_NAME": "fake-repo",
    "PULL_NUMBER": "1",
    "GITHUB_TOKEN": "fake-token",
    "GITHUB_BASE_REF": "main",
    "GITHUB_HEAD_REF": "develop",
    "CHATGPT_KEY": "fake-chatgpt-key",
    "CHATGPT_MODEL": "gpt-4",
    "TARGET_EXTENSIONS": "py,js",
    "FOCUS_AREAS": "performance,security",
})
@patch("github_reviewer.Git")
@patch("github_reviewer.GitHub")
@patch("github_reviewer.ChatGPT")
@patch("builtins.open", new_callable=mock_open, read_data="print('Hello')")
def test_filter_existing_comments(mock_file, mock_chat_gpt, mock_github, mock_git):
    # Mock Git methods
    mock_git.get_remote_name.return_value = "origin"
    mock_git.get_diff_files.return_value = ["example.py"]
    mock_git.get_diff_in_file.return_value = "@@ -1 +1 @@\n-print('Hello')\n+print('Hello, world!')"
    mock_git.get_last_commit_sha.return_value = "abc123"

    # Mock GitHub methods
    mock_github_instance = mock_github.return_value
    mock_github_instance.get_existing_comments.return_value = [
        {"position": 1, "body": "Existing comment"}
    ]

    # Mock ChatGPT response to ensure non-empty response
    mock_chat_gpt_instance = mock_chat_gpt.return_value
    mock_chat_gpt_instance.ai_request_diffs.return_value = """
    1: Suggested change for line 1\n2: Suggested change for line 2
    """

    # Mock AiBot split_ai_response to return responses with positions
    with patch("github_reviewer.AiBot.split_ai_response", return_value=[
        MagicMock(position=1, text="Suggested change for line 1", line=1),
        MagicMock(position=2, text="Suggested change for line 2", line=2)
    ]):
        main()

    # Ensure existing comments are fetched
    mock_github_instance.get_existing_comments.assert_called_once()

    # Ensure comments with matching positions are filtered out
    mock_github_instance.post_comment_to_line.assert_called_once_with(
        text="Suggested change for line 2",
        commit_id="abc123",
        file_path="example.py",
        position=2
    )