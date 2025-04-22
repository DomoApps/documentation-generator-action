# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

from abc import ABC, abstractmethod
from ai.line_comment import LineComment
from log import Log


class AiBot(ABC):
    
    __no_response = "No critical issues found"
    __chat_gpt_ask_long = """
    Task:
    Review the following diff for issues and provide comments directly in the format required for posting to the GitHub API.

    Instructions:
    1. Focus Areas:
      {focus_areas}

    2. Output Format:
      [
        {{
          "position": <position_in_diff>,
          "body": "<comment_text>"
        }}
      ]

    3. Positioning Rules:
      For the position value, always use the value is indicated by the number at the start of the line being reviewed.
      Do not use the line number with any variations. If you are reviewing line 89, use 89, not 88 or 90.

    4. Output Rules:
      Do not comment on removed (-) or context ( ) lines.
      Be concise and professional in your comments.
      Return a valid JSON array of comments.
      If no issues are found, return an empty array [].
      Do not include any markdown (such as ```json), explanations, or additional text.
      Make one comment per line. If you have multiple recommendations, combine it into a single comment.

    5. Example: Given this diff:
    index b21e242..bee2ab2 100644
    --- a/docs/Getting-Started/overview.md
    +++ b/docs/Getting-Started/overview.md
    @@ -4,61 +4,66 @@ stoplight-id: d01f63a6ba662
    1 
    2 # Some Header
    3 
    4-Some text that was removed.
    5+Some text that was added with a typo
    6 
    7-Some more text that was removed.
    8+Some more text that was added with a clarity issue.
    9 

      A comment on "Some text that was added with a typo" should be:
      [
        {{
          "position": 5,
          "body": "Typo: 'typo' should be corrected."
        }}
      ]

      A comment on "Some more text that was added with a clarity issue" should be:
      [
        {{
          "position": 8,
          "body": "Consider rephrasing for clarity."
        }}
      ]

      Here is the diff to review:
        {diffs}
    """

    @abstractmethod
    def ai_request_diffs(self, code, diffs) -> str:
        """
        Abstract method to request AI feedback on diffs.

        Args:
            code (str): The full code of the file.
            diffs (str): The git diffs to review.

        Returns:
            str: The AI's response.
        """
        pass

    @staticmethod
    def build_ask_text(code, diffs, focus_areas) -> str:
        return AiBot.__chat_gpt_ask_long.format(
            focus_areas=focus_areas,
            diffs=diffs,
            code=code
        )

    @staticmethod
    def is_no_issues_text(source: str) -> bool:
        target = AiBot.__no_response.replace(" ", "")
        source_no_spaces = source.replace(" ", "")
        return source_no_spaces.startswith(target)
    
    @staticmethod
    def split_ai_response(input) -> list[LineComment]:
        """
        Parses the AI response in JSON format and converts it into a list of LineComment objects.

        Args:
            input (str): The AI response in JSON format.

        Returns:
            list[LineComment]: A list of LineComment objects.
        """
        if input is None or not input.strip():
            return []

        if not isinstance(input, str):
            raise ValueError("Input must be a string.")

        import json
        import re

        try:
            comments = json.loads(input)
            return [
                LineComment(line=comment["position"], text=comment["body"])
                for comment in comments
                if "position" in comment and "body" in comment
            ]
        except json.JSONDecodeError as e:
            Log.print_red("JSON Decode error:", input)
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            Log.print_red("AI bot exception:", input)
            raise ValueError(f"Unexpected error while parsing AI response: {e}")
