import pytest
from unittest.mock import patch, MagicMock
from repository.github import GitHub, RepositoryError

@pytest.fixture
def github_instance():
    return GitHub(token="fake-token", repo_owner="fake-owner", repo_name="fake-repo", pull_number=1)

@patch("repository.github.requests.post")
def test_post_comment_to_line(mock_post, github_instance):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": 12345}

    response = github_instance.post_comment_to_line(
        text="Test comment",
        commit_id="abc123",
        file_path="test_file.py",
        position=10
    )

    assert response["id"] == 12345
    mock_post.assert_called_once()

@patch("repository.github.requests.post")
def test_post_comment_to_line_error(mock_post, github_instance):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"

    with pytest.raises(RepositoryError, match="Error with line comment 400 : Bad Request"):
        github_instance.post_comment_to_line(
            text="Test comment",
            commit_id="abc123",
            file_path="test_file.py",
            position=10
        )

@patch("repository.github.requests.post")
def test_post_comment_general(mock_post, github_instance):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"id": 67890}

    response = github_instance.post_comment_general(text="General comment")

    assert response["id"] == 67890
    mock_post.assert_called_once()

@patch("repository.github.requests.post")
def test_post_comment_general_error(mock_post, github_instance):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"

    with pytest.raises(RepositoryError, match="Error with general comment 400 : Bad Request"):
        github_instance.post_comment_general(text="General comment")

@patch("repository.github.requests.get")
def test_get_existing_comments(mock_get, github_instance):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"id": 1, "body": "Existing comment"}]

    comments = github_instance.get_existing_comments()

    assert len(comments) == 1
    assert comments[0]["body"] == "Existing comment"
    mock_get.assert_called_once()

@patch("repository.github.requests.get")
def test_get_existing_comments_error(mock_get, github_instance):
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"

    with pytest.raises(RepositoryError, match="Error fetching comments 500 : Internal Server Error"):
        github_instance.get_existing_comments()