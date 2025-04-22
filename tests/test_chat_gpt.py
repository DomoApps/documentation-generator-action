import sys
import os
sys.path.append('../src')

from unittest.mock import patch, ANY, MagicMock
from ai.chat_gpt import ChatGPT
from ai.ai_bot import AiBot
from log import Log

@patch("openai.ChatCompletion.create")
def test_ai_request_diffs(mock_chat_completion_create):
    # Mock the response from the OpenAI API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response content"))]
    mock_chat_completion_create.return_value = mock_response

    # Mock the nested structure of the OpenAI client
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_chat_completion_create
    focus_areas = "performance,security"

    ai = ChatGPT(client=mock_client, model="gpt-4", focus_areas=focus_areas)
    code = "def example_function():\n    pass"
    diffs = "- def example_function():\n+ def example_function(param):\n    pass"

    # Call the ai_request_diffs function
    response = ai.ai_request_diffs(code, diffs)

    # Assert the response content
    assert response == "Mocked response content", f"Expected 'Mocked response content', but got {response}"

    # Assert that the OpenAI API was called with the correct payload
    mock_chat_completion_create.assert_called_once_with(
        messages=[
            {
                "role": "user",
                "content": ai.build_ask_text(code=code, diffs=diffs, focus_areas=focus_areas),
            }
        ],
        model="gpt-4"
    )

@patch("openai.ChatCompletion.create")
def test_build_request_payload(mock_chat_completion_create):
    ai = ChatGPT(client=mock_chat_completion_create, model="gpt-4", focus_areas="performance,security")
    code = "def example_function():\n    pass"
    diffs = "- def example_function():\n+ def example_function(param):\n    pass"

    payload = ai.build_request_payload(code, diffs)

    # Assert the payload structure
    assert payload["model"] == "gpt-4"
    assert "messages" in payload
    assert payload["messages"][0]["role"] == "user"
    assert "content" in payload["messages"][0]

@patch("openai.ChatCompletion.create")
def test_ai_request_diffs_strips_formatting(mock_chat_completion_create):
    # Mock the response from the OpenAI API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="```json\n[{\"key\": \"value\"}]\n```"))]
    mock_chat_completion_create.return_value = mock_response

    # Mock the nested structure of the OpenAI client
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_chat_completion_create
    focus_areas = "performance,security"

    ai = ChatGPT(client=mock_client, model="gpt-4", focus_areas=focus_areas)
    code = "def example_function():\n    pass"
    diffs = "- def example_function():\n+ def example_function(param):\n    pass"

    # Call the ai_request_diffs function
    response = ai.ai_request_diffs(code, diffs)

    # Assert the response content is stripped of markdown formatting
    assert response == "[{\"key\": \"value\"}]", f"Expected '[{{\"key\": \"value\"}}]', but got {response}"

    # Assert that the OpenAI API was called with the correct payload
    mock_chat_completion_create.assert_called_once_with(
        messages=[
            {
                "role": "user",
                "content": ai.build_ask_text(code=code, diffs=diffs, focus_areas=focus_areas),
            }
        ],
        model="gpt-4"
    )