# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import json
import yaml
from openai import OpenAI
from ai.ai_bot import AiBot
from log import Log

class DocGenerator(AiBot):
    def __init__(self, client, model):
        self.__client = client
        self.__model = model
        self.current_iteration = 0

    def process_yaml_to_markdown(self, yaml_content: str, template_content: str, max_iterations: int = 10, completeness_threshold: int = 90) -> str:
        """
        Main process loop for converting YAML to Markdown documentation
        """
        self.current_iteration = 0
        current_markdown = ""

        while self.current_iteration < max_iterations:
            self.current_iteration += 1
            Log.print_green(f"Starting iteration {self.current_iteration}")

            # Step 1: Analyze YAML and extract template data
            analysis_result = self._analyze_yaml(yaml_content, template_content)

            # Step 2: Generate/update markdown using template
            current_markdown = self._generate_markdown(yaml_content, template_content, analysis_result)

            # Step 3: Validate quality and completeness
            validation_result = self._validate_documentation(current_markdown, yaml_content)

            # Step 4: Check exit conditions
            if self._should_exit(validation_result, completeness_threshold):
                Log.print_green(f"Documentation complete after {self.current_iteration} iterations")
                break

            # Step 5: If not complete, refine based on feedback
            if self.current_iteration < max_iterations:
                current_markdown = self._refine_documentation(current_markdown, yaml_content, validation_result)

        return current_markdown

    def _analyze_yaml(self, yaml_content: str, template_content: str) -> dict:
        """Extract data mapping from YAML for template population"""
        prompt = f"""
        Task: Extract template variables from YAML for documentation generation

        Instructions:
        1. Parse the YAML and identify all template placeholders from the template
        2. Map YAML data to template variables like {{{{API_NAME}}}}, {{{{ENDPOINT_PATH}}}}, etc.
        3. Extract parameter arrays for {{{{#each}}}} blocks
        4. Generate realistic code examples
        5. Output valid JSON only

        Template placeholders to fill:
        {self._extract_template_placeholders(template_content)}

        YAML Content:
        {yaml_content}
        """

        response = self._make_ai_request(prompt)
        Log.print_green(f"AI Analysis Response: {response[:200]}...")

        # Extract JSON from response
        json_str = self._extract_json_from_response(response)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            Log.print_red(f"Failed to parse analysis result as JSON: {e}")
            Log.print_red(f"Extracted JSON: {json_str}")
            Log.print_red(f"Raw response: {response}")
            return {}

    def _generate_markdown(self, yaml_content: str, template_content: str, analysis_data: dict) -> str:
        """Generate markdown by populating template with extracted data"""
        prompt = f"""
        Task: Fill template placeholders with YAML-extracted data

        Instructions:
        1. Replace ALL {{{{placeholder}}}} variables with values from analysis_data
        2. Handle {{{{#if}}}} conditionals based on data presence
        3. Process {{{{#each}}}} loops for parameter tables
        4. Generate realistic, functional code examples for JavaScript and Python
        5. Ensure all markdown syntax is valid
        6. Output only the final markdown content

        Template:
        {template_content}

        Data to use:
        {json.dumps(analysis_data, indent=2)}
        """

        return self._make_ai_request(prompt)

    def _validate_documentation(self, markdown_content: str, yaml_content: str) -> dict:
        """Validate documentation quality and completeness"""
        prompt = f"""
        Task: Validate documentation quality and identify gaps

        Evaluation criteria:
        - Completeness: All YAML elements documented (0-100)
        - Template Coverage: All placeholders filled (0-100)
        - Code Quality: Realistic, functional examples (0-100)
        - Markdown Syntax: Valid formatting (0-100)

        Output JSON format:
        {{
          "scores": {{
            "completeness": 0-100,
            "template_coverage": 0-100,
            "code_quality": 0-100,
            "markdown_syntax": 0-100,
            "overall": 0-100
          }},
          "missing_placeholders": ["list", "of", "unfilled", "placeholders"],
          "improvement_suggestions": ["specific", "improvement", "items"],
          "exit_criteria_met": true/false
        }}

        Documentation to validate:
        {markdown_content}

        Original YAML:
        {yaml_content}
        """

        response = self._make_ai_request(prompt)
        Log.print_green(f"AI Validation Response: {response[:200]}...")

        # Extract JSON from response
        json_str = self._extract_json_from_response(response)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            Log.print_red(f"Failed to parse validation result as JSON: {e}")
            Log.print_red(f"Extracted JSON: {json_str}")
            Log.print_red(f"Raw response: {response}")
            return {"scores": {"overall": 0}, "exit_criteria_met": False}

    def _refine_documentation(self, current_markdown: str, yaml_content: str, validation_result: dict) -> str:
        """Refine documentation based on validation feedback"""
        improvements = validation_result.get("improvement_suggestions", [])
        missing_placeholders = validation_result.get("missing_placeholders", [])

        prompt = f"""
        Task: Improve documentation based on validation feedback

        Priority fixes needed:
        1. Fill missing placeholders: {missing_placeholders}
        2. Address improvements: {improvements}
        3. Maintain existing strengths
        4. Output only the improved markdown

        Current documentation:
        {current_markdown}

        YAML reference:
        {yaml_content}
        """

        return self._make_ai_request(prompt)

    def _should_exit(self, validation_result: dict, threshold: int) -> bool:
        """Determine if exit conditions are met"""
        overall_score = validation_result.get("scores", {}).get("overall", 0)
        exit_criteria_met = validation_result.get("exit_criteria_met", False)

        return overall_score >= threshold and exit_criteria_met

    def _extract_template_placeholders(self, template_content: str) -> list:
        """Extract all template placeholders for reference"""
        import re
        placeholders = re.findall(r'\{\{([^}]+)\}\}', template_content)
        return list(set(placeholders))

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from AI response that might contain markdown or extra text"""
        # Remove markdown code blocks
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        if json_match:
            return json_match.group(1).strip()

        # Look for JSON object starting with { and ending with }
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()

        # Return original if no patterns found
        return response.strip()

    def _make_ai_request(self, prompt: str) -> str:
        """Make request to AI model"""
        try:
            response = self.__client.chat.completions.create(
                model=self.__model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            Log.print_red(f"AI request failed: {e}")
            return ""

    def ai_request_diffs(self, code, diffs) -> str:
        """Required by parent class but not used in doc generation"""
        return "Not applicable for documentation generation"