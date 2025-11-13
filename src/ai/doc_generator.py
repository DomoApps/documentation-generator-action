# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import json
import yaml
from openai import OpenAI
from .ai_bot import AiBot
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from log import Log
from openapi.openapi_parser import OpenAPIParser, EndpointData


class DocGenerator(AiBot):
    def __init__(self, client, model):
        self.__client = client
        self.__model = model
        self.current_iteration = 0

    def process_openapi_to_markdown_deterministic(
        self, yaml_path: str, template_content: str, max_iterations: int = 3, completeness_threshold: int = 90
    ) -> str:
        """
        Process OpenAPI spec path-by-path using schema-based parsing with AI validation

        This hybrid approach:
        1. Uses prance to resolve all $refs
        2. Parses each endpoint deterministically
        3. Extracts parameters directly from schemas
        4. Generates examples from schema types
        5. Uses AI to fill the template
        6. **NEW: Validates output with AI and refines if needed**

        Args:
            yaml_path: Path to OpenAPI YAML file
            template_content: Template for rendering documentation
            max_iterations: Maximum refinement iterations (default: 3)
            completeness_threshold: Quality score threshold for completion (default: 90)

        Returns:
            Complete markdown documentation
        """
        Log.print_green("=== Starting HYBRID (Deterministic + Validation) OpenAPI processing ===")

        # Parse OpenAPI spec deterministically
        parser = OpenAPIParser(yaml_path)
        api_info = parser.get_api_info()
        endpoints = parser.parse_all_endpoints()

        # Load original YAML for validation context
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        Log.print_green(f"Found {len(endpoints)} endpoints to document")

        # Build documentation for each endpoint
        endpoint_docs = []
        for i, endpoint in enumerate(endpoints, 1):
            Log.print_green(
                f"Processing endpoint {i}/{len(endpoints)}: {endpoint.method.upper()} {endpoint.path}"
            )

            # Generate documentation for this endpoint
            doc = self._generate_endpoint_documentation(
                endpoint, template_content, parser
            )
            endpoint_docs.append(doc)

        # Combine all endpoint documentation
        full_doc = self._combine_endpoint_docs(api_info, endpoint_docs)

        # **NEW: Validation and refinement loop**
        self.current_iteration = 0
        while self.current_iteration < max_iterations:
            self.current_iteration += 1
            Log.print_green(f"Validation iteration {self.current_iteration}/{max_iterations}")

            # Validate the deterministically-generated documentation
            validation_result = self._validate_documentation(full_doc, yaml_content)

            # Log validation scores
            scores = validation_result.get("scores", {})
            Log.print_green(f"  Overall: {scores.get('overall', 0)}/100")
            Log.print_green(f"  Completeness: {scores.get('completeness', 0)}/100")
            Log.print_green(f"  Template Coverage: {scores.get('template_coverage', 0)}/100")
            Log.print_green(f"  Code Quality: {scores.get('code_quality', 0)}/100")
            Log.print_green(f"  Markdown Syntax: {scores.get('markdown_syntax', 0)}/100")

            # Check if quality threshold met
            if self._should_exit(validation_result, completeness_threshold):
                Log.print_green(f"Quality threshold met after {self.current_iteration} iteration(s)")
                break

            # If not meeting threshold and iterations remaining, refine
            if self.current_iteration < max_iterations:
                Log.print_green("Refining documentation based on validation feedback...")
                full_doc = self._refine_documentation(full_doc, yaml_content, validation_result)
            else:
                Log.print_red(f"Max iterations reached. Final score: {scores.get('overall', 0)}/100")

        Log.print_green("=== HYBRID processing complete ===")
        return full_doc

    def _generate_endpoint_documentation(
        self, endpoint: EndpointData, template: str, parser: OpenAPIParser
    ) -> str:
        """
        Generate documentation for a single endpoint using structured data

        AI's job is now much simpler: just polish the already-structured data
        """
        # Build parameter tables
        path_params_table = self._build_parameter_table(
            endpoint.path_parameters, parser
        )
        query_params_table = self._build_parameter_table(
            endpoint.query_parameters, parser
        )
        request_body_table = self._build_parameter_table(
            endpoint.request_body_parameters, parser
        )

        # Generate nested object tables for request body parameters
        nested_object_tables = self._generate_nested_object_tables(
            endpoint.request_body_parameters, parser
        )

        # Format examples
        request_example = (
            parser.format_example_as_json(endpoint.request_body_example)
            if endpoint.request_body_example
            else None
        )
        response_example = (
            parser.format_example_as_json(endpoint.success_response_example)
            if endpoint.success_response_example
            else None
        )

        # Build error responses section
        error_responses = self._build_error_responses(endpoint.responses)

        # Prepare structured data for the AI
        structured_data = {
            "API_NAME": endpoint.summary or "API Endpoint",
            "ENDPOINT_NAME": endpoint.summary
            or f"{endpoint.method.upper()} {endpoint.path}",
            "HTTP_METHOD": endpoint.method.upper(),
            "ENDPOINT_PATH": endpoint.path,
            "API_DESCRIPTION": endpoint.description,
            "OPERATION_ID": endpoint.operation_id,
            # Parameter tables (already formatted as markdown)
            "PATH_PARAMETERS_TABLE": path_params_table,
            "QUERY_PARAMETERS_TABLE": query_params_table,
            "REQUEST_BODY_TABLE": request_body_table,
            # Nested object tables
            "NESTED_OBJECT_TABLES": nested_object_tables,
            # Request body schema description (important context!)
            "REQUEST_BODY_DESCRIPTION": endpoint.request_body_description,
            # Raw parameter lists (for custom formatting)
            "PATH_PARAMETERS": json.dumps(endpoint.path_parameters, indent=2),
            "QUERY_PARAMETERS": json.dumps(endpoint.query_parameters, indent=2),
            "REQUEST_BODY_PARAMETERS": json.dumps(
                endpoint.request_body_parameters, indent=2
            ),
            # Examples
            "REQUEST_BODY_EXAMPLE": request_example or "N/A",
            "RESPONSE_EXAMPLE": response_example or "{}",
            "SUCCESS_STATUS_CODE": endpoint.success_status_code or "200",
            # Additional sections
            "ERROR_RESPONSES": error_responses,
        }

        prompt = f"""
Task: Generate API documentation by filling in this template with the provided structured data.

TEMPLATE TO FILL:
{template}

STRUCTURED DATA (all validated and extracted from OpenAPI spec):
{json.dumps(structured_data, indent=2)}

CRITICAL INSTRUCTIONS:
1. Follow the template structure EXACTLY - preserve all markdown formatting, headers, tables, code blocks
2. Replace placeholders like {{{{ENDPOINT_NAME}}}} with data from STRUCTURED DATA
3. For code examples (JavaScript, Python, cURL):
   - Generate realistic, working examples
   - Use the actual HTTP_METHOD and ENDPOINT_PATH
   - Include the REQUEST_BODY_EXAMPLE in the request if it exists
   - Show the RESPONSE_EXAMPLE as the expected response
4. Preserve all HTML comments for tabs (<!-- type: tab -->, <!-- type: tab-end -->)
   - IMPORTANT: Every tab section MUST end with <!-- type: tab-end -->
5. If a placeholder is not in STRUCTURED DATA, use reasonable defaults

FORMATTING REQUIREMENTS:
6. Add a blank line after every </details> closing tag
7. Use consistent bullet format: Use hyphens (-) for all bullet lists, not asterisks (*)
8. Parameter descriptions should end with a period
9. Remove any trailing spaces from table cells
10. DO NOT add horizontal rules (---) at the end of the output - they will be added automatically
11. DO NOT include markdown code fences (```) around the entire output
12. DO NOT include template headers or comments
13. Output ONLY the filled template content, no wrapper, no explanations

Generate the documentation now:
        """

        return self._make_ai_request(prompt)

    def _build_parameter_table(self, parameters: list, parser=None) -> str:
        """Build a markdown table for parameters"""
        if not parameters:
            return "_None_"

        table = "| Parameter | Type | Required | Description |\n"
        table += "|-----------|------|----------|-------------|\n"

        for param in parameters:
            name = param.get("name", "")
            param_type = param.get("type", "string")
            required = "✓ Yes" if param.get("required") else "No"
            description = param.get("description", "").replace("\n", " ").strip()

            # Add schema reference link for object types
            if param_type == "object" or "object" in param_type:
                schema_ref = param.get("schema_ref")
                if schema_ref and not schema_ref.startswith("inline_"):
                    schema_name = schema_ref.split("/")[-1]
                    # Create friendly name by removing _Nullable suffix
                    friendly_name = schema_name.replace("_Nullable", "")
                    # Create a link to the schema dropdown
                    schema_link = f"[{friendly_name}](#schema-{schema_name.lower().replace('_', '-')})"
                    param_type = schema_link

            # Add default value if present
            if param.get("default") is not None:
                description += f" (Default: `{param['default']}`)"

            # Add enum values if present
            if param.get("enum"):
                enum_values = ", ".join([f"`{v}`" for v in param["enum"][:5]])
                description += f" Allowed values: {enum_values}"

            table += f"| `{name}` | {param_type} | {required} | {description} |\n"

        return table

    def _build_error_responses(self, responses: dict) -> str:
        """Build error responses table (template provides the heading)"""
        error_codes = [code for code in responses.keys() if not code.startswith("2")]

        if not error_codes:
            return "_None_"

        # Just build the table - template already has the "### Error Responses" heading
        table = "| Status Code | Description |\n"
        table += "|-------------|-------------|\n"

        for code in sorted(error_codes):
            description = responses[code].get("description", "Error")
            table += f"| `{code}` | {description} |\n"

        return table

    def _generate_nested_object_tables(
        self, parameters: list, parser, processed_schemas: set = None
    ) -> str:
        """
        Recursively generate tables for nested objects to avoid duplication.

        Args:
            parameters: List of parameter dictionaries
            parser: OpenAPIParser instance for resolving schemas
            processed_schemas: Set of already processed schema names to avoid duplicates

        Returns:
            Markdown string containing all nested object tables in dropdowns
        """
        if processed_schemas is None:
            processed_schemas = set()

        nested_tables = []

        for param in parameters:
            param_type = param.get("type", "")
            param_name = param.get("name", "")

            # Check if this is an object type that might have nested properties
            if param_type == "object" or "object" in param_type:
                # Try to get the schema for this parameter
                schema = self._get_parameter_schema(param, parser)

                if schema and schema.get("properties"):
                    schema_name = self._get_schema_name(param, parser)

                    # Avoid processing the same schema multiple times
                    if schema_name and schema_name not in processed_schemas:
                        processed_schemas.add(schema_name)

                        # Generate table for this nested object
                        nested_table = self._build_nested_object_table(
                            schema, schema_name, parser, processed_schemas
                        )
                        if nested_table:
                            # Create friendly name by removing _Nullable suffix
                            friendly_name = schema_name.replace("_Nullable", "")
                            # Wrap in markdown dropdown
                            dropdown_id = (
                                f"schema-{schema_name.lower().replace('_', '-')}"
                            )
                            dropdown = f"""<details>
<summary><strong>{friendly_name} Object</strong></summary>

{nested_table}

</details>"""
                            nested_tables.append(dropdown)

        return "\n\n".join(nested_tables) if nested_tables else ""

    def _get_parameter_schema(self, param: dict, parser) -> dict:
        """Extract the schema for a parameter if it's an object type"""
        # Try to resolve from schema reference first
        schema_ref = param.get("schema_ref")
        if schema_ref:
            if schema_ref.startswith("inline_"):
                return param.get("schema")
            else:
                resolved_schema = parser._resolve_ref(schema_ref)

                # Check if this is a _Nullable schema, resolve the base schema
                if "_Nullable" in schema_ref:
                    base_schema_name = schema_ref.split("/")[-1].replace(
                        "_Nullable", ""
                    )
                    base_schema_ref = f"#/components/schemas/{base_schema_name}"
                    base_schema = parser._resolve_ref(base_schema_ref)
                    return base_schema

                # Check if this is an allOf schema with a $ref
                if "allOf" in resolved_schema and len(resolved_schema["allOf"]) > 0:
                    allof_item = resolved_schema["allOf"][0]
                    if "$ref" in allof_item:
                        nested_ref = allof_item["$ref"]
                        nested_schema = parser._resolve_ref(nested_ref)
                        return nested_schema

                return resolved_schema

        # Fallback to stored schema if no ref
        if param.get("schema"):
            return param["schema"]

        return None

    def _get_schema_name(self, param: dict, parser) -> str:
        """Get the schema name for a parameter"""
        schema_ref = param.get("schema_ref")
        if schema_ref:
            if schema_ref.startswith("inline_"):
                return schema_ref.replace("inline_", "")
            else:
                # Extract schema name from reference
                return schema_ref.split("/")[-1]

        # Fallback to parameter name
        return param.get("name", "Unknown")

    def _build_nested_object_table(
        self, schema: dict, schema_name: str, parser, processed_schemas: set
    ) -> str:
        """Build a table for a nested object schema"""
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        if not properties:
            return ""

        # Build the table header (no heading since it's in the dropdown)
        table = "| Parameter | Type | Required | Description |\n"
        table += "|-----------|------|----------|-------------|\n"

        # Process each property
        for prop_name, prop_schema in properties.items():
            # Handle $ref in properties
            if "$ref" in prop_schema:
                ref_path = prop_schema["$ref"]
                if "_Nullable" in ref_path:
                    type_name = ref_path.split("/")[-1].replace("_Nullable", "")
                    prop_schema = {
                        "type": "object",
                        "description": f"Optional {type_name} object (nullable)",
                    }
                else:
                    prop_schema = parser._resolve_ref(ref_path)

            param_type = prop_schema.get("type", "string")
            param_format = prop_schema.get("format", "")
            if param_format:
                param_type = f"{param_type} ({param_format})"

            required = "✓ Yes" if prop_name in required_fields else "No"
            description = prop_schema.get("description", "").replace("\n", " ").strip()

            table += f"| `{prop_name}` | {param_type} | {required} | {description} |\n"

            # Recursively process nested objects
            if param_type == "object" or "object" in param_type:
                nested_schema = prop_schema
                if nested_schema and nested_schema.get("properties"):
                    nested_schema_name = f"{schema_name}.{prop_name}"
                    if nested_schema_name not in processed_schemas:
                        processed_schemas.add(nested_schema_name)
                        nested_table = self._build_nested_object_table(
                            nested_schema, nested_schema_name, parser, processed_schemas
                        )
                        if nested_table:
                            table += f"\n{nested_table}"

        return table

    def _combine_endpoint_docs(self, api_info: dict, endpoint_docs: list) -> str:
        """Combine individual endpoint docs into a single document"""
        # Build table of contents
        toc = "## Table of Contents\n\n"
        for i, doc in enumerate(endpoint_docs, 1):
            # Extract endpoint title from doc (first # heading)
            lines = doc.split("\n")
            for line in lines:
                if line.startswith("## "):
                    toc += f"{i}. [{line[3:]}](#{line[3:].lower().replace(' ', '-')})\n"
                    break

        # Combine everything
        full_doc = f"""# {api_info['title']} API

> **Version:** {api_info['version']}
>
> {api_info['description']}

{toc}

---

"""

        for i, doc in enumerate(endpoint_docs):
            # Strip any trailing whitespace and separators from the doc
            doc_cleaned = doc.rstrip()
            # Remove trailing --- if present
            if doc_cleaned.endswith("---"):
                doc_cleaned = doc_cleaned[:-3].rstrip()

            full_doc += doc_cleaned + "\n\n---\n\n"

        return full_doc

    def process_yaml_to_markdown(
        self,
        yaml_content: str,
        template_content: str,
        max_iterations: int = 10,
        completeness_threshold: int = 90,
    ) -> str:
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
            current_markdown = self._generate_markdown(
                yaml_content, template_content, analysis_result
            )

            # Step 3: Validate quality and completeness
            validation_result = self._validate_documentation(
                current_markdown, yaml_content
            )

            # Step 4: Check exit conditions
            if self._should_exit(validation_result, completeness_threshold):
                Log.print_green(
                    f"Documentation complete after {self.current_iteration} iterations"
                )
                break

            # Step 5: If not complete, refine based on feedback
            if self.current_iteration < max_iterations:
                current_markdown = self._refine_documentation(
                    current_markdown, yaml_content, validation_result
                )

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
            Log.print_red(f"Extracted JSON preview: {json_str[:200]}...")

            # Try one more time with a more aggressive cleanup
            fallback_json = self._create_fallback_analysis()
            Log.print_red("Using fallback analysis structure")
            return fallback_json

    def _generate_markdown(
        self, yaml_content: str, template_content: str, analysis_data: dict
    ) -> str:
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
            Log.print_red(f"Extracted JSON preview: {json_str[:200]}...")

            # Return sensible fallback for validation
            Log.print_red("Using fallback validation structure")
            return {
                "scores": {
                    "overall": 75,
                    "completeness": 75,
                    "template_coverage": 75,
                    "code_quality": 75,
                    "markdown_syntax": 75,
                },
                "missing_placeholders": [],
                "improvement_suggestions": [
                    "JSON parsing failed, using fallback validation"
                ],
                "exit_criteria_met": True,  # Allow processing to continue
            }

    def _refine_documentation(
        self, current_markdown: str, yaml_content: str, validation_result: dict
    ) -> str:
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

        placeholders = re.findall(r"\{\{([^}]+)\}\}", template_content)
        return list(set(placeholders))

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from AI response that might contain markdown or extra text"""
        import re
        import json as json_lib

        # Strategy 1: Extract from markdown code blocks
        json_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE
        )
        if json_match:
            candidate = json_match.group(1).strip()
            if self._is_valid_json(candidate):
                return candidate

        # Strategy 2: Find balanced JSON object with proper bracket counting
        json_candidate = self._extract_balanced_json(response)
        if json_candidate and self._is_valid_json(json_candidate):
            return json_candidate

        # Strategy 3: Try to clean and fix common JSON issues
        cleaned_response = self._clean_json_response(response)
        if self._is_valid_json(cleaned_response):
            return cleaned_response

        # Strategy 4: Return original as fallback
        return response.strip()

    def _extract_balanced_json(self, text: str) -> str:
        """Extract JSON using balanced bracket counting"""
        start_idx = text.find("{")
        if start_idx == -1:
            return ""

        bracket_count = 0
        in_string = False
        escape_next = False

        for i, char in enumerate(text[start_idx:], start_idx):
            if escape_next:
                escape_next = False
                continue

            if char == "\\" and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        return text[start_idx : i + 1]

        return ""

    def _clean_json_response(self, response: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove any text before first {
        start_idx = response.find("{")
        if start_idx == -1:
            return response

        # Remove any text after last }
        end_idx = response.rfind("}")
        if end_idx == -1:
            return response

        cleaned = response[start_idx : end_idx + 1]

        # Fix common issues
        cleaned = cleaned.replace("\n", "\\n")  # Escape newlines in strings
        cleaned = cleaned.replace("\t", "\\t")  # Escape tabs

        return cleaned

    def _is_valid_json(self, text: str) -> bool:
        """Check if string is valid JSON"""
        import json as json_lib

        try:
            json_lib.loads(text)
            return True
        except (json_lib.JSONDecodeError, ValueError):
            return False

    def _create_fallback_analysis(self) -> dict:
        """Create a basic analysis structure when JSON parsing fails"""
        return {
            "API_NAME": "API Documentation",
            "API_DESCRIPTION": "Generated API documentation",
            "ENDPOINTS": [
                {
                    "ENDPOINT_NAME": "API Endpoint",
                    "ENDPOINT_PATH": "/api/endpoint",
                    "HTTP_METHOD": "GET",
                    "description": "API endpoint description",
                    "parameters": [],
                }
            ],
            "note": "Fallback structure used due to JSON parsing error",
        }

    def generate_pr_title(self, changed_files: list, yaml_summaries: dict) -> str:
        """Generate an AI-powered PR title based on changed files and their content"""
        if not changed_files:
            return "📚 Update API documentation"

        # Create summary of changes for AI
        changes_summary = self._create_changes_summary(changed_files, yaml_summaries)

        prompt = f"""
        Task: Generate a concise, descriptive pull request title for API documentation updates

        Requirements:
        - Maximum 60 characters
        - Start with emoji (📚, 🔄, ✨, 🐛, 🚀, etc.)
        - Be specific about what changed
        - Use active voice
        - Professional tone

        Changes made:
        {changes_summary}

        Examples of good titles:
        - "📚 Add user authentication endpoints"
        - "🔄 Update FileSet API responses"
        - "✨ New AI text summarization API"
        - "🐛 Fix payment API parameter docs"
        - "🚀 Enhanced search API with filters"

        Generate only the title (no explanation):
        """

        try:
            title = self._make_ai_request(prompt).strip()
            # Clean up response and ensure it's reasonable
            title = title.replace('"', "").strip()
            if len(title) > 60:
                title = title[:57] + "..."
            return title if title else "📚 Update API documentation"
        except Exception as e:
            Log.print_red(f"Failed to generate PR title: {e}")
            return self._create_fallback_pr_title(changed_files)

    def _create_changes_summary(self, changed_files: list, yaml_summaries: dict) -> str:
        """Create a summary of changes for PR title generation"""
        summary_parts = []

        for file_path in changed_files:
            file_name = (
                file_path.split("/")[-1].replace(".yaml", "").replace(".yml", "")
            )

            if file_path in yaml_summaries:
                yaml_info = yaml_summaries[file_path]
                api_name = yaml_info.get("info", {}).get("title", file_name)
                summary_parts.append(f"- {api_name} API ({file_name})")
            else:
                summary_parts.append(f"- {file_name} API")

        return "\n".join(summary_parts)

    def _create_fallback_pr_title(self, changed_files: list) -> str:
        """Create fallback PR title when AI generation fails"""
        if len(changed_files) == 1:
            file_name = (
                changed_files[0].split("/")[-1].replace(".yaml", "").replace(".yml", "")
            )
            return f"📚 Update {file_name} API docs"
        else:
            return f"📚 Update {len(changed_files)} API specifications"

    def _make_ai_request(self, prompt: str) -> str:
        """Make request to AI model"""
        try:
            response = self.__client.chat.completions.create(
                model=self.__model, messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            Log.print_red(f"AI request failed: {e}")
            return ""

    def ai_request_diffs(self, code, diffs) -> str:
        """Required by parent class but not used in doc generation"""
        return "Not applicable for documentation generation"
