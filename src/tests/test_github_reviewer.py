import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import os
from unittest.mock import patch, MagicMock, ANY
import pytest
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
    "TARGET_EXTENSIONS": "py,js"
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