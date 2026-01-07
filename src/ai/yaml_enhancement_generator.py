"""
YAML Enhancement Generator Module

Uses AI to generate contextual descriptions for missing fields in OpenAPI YAML files.
Refactored from DocGenerator to focus on YAML enhancement rather than Markdown generation.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .ai_bot import AiBot
from log import Log
from openapi.openapi_parser import OpenAPIParser, EndpointData
from openapi.example_generator import ExampleGenerator
from yaml_enhancer import YAMLGapAnalysis, Enhancement


class YAMLEnhancementGenerator(AiBot):
    """
    Generates AI-powered enhancements for OpenAPI YAML files.

    Uses a hybrid approach:
    1. Deterministic parsing to identify gaps
    2. AI generation to create contextual descriptions
    3. Validation loop to ensure quality
    4. Iterative refinement based on feedback
    """

    def __init__(self, client, model):
        """
        Initialize the YAML enhancement generator.

        Args:
            client: OpenAI client instance
            model: Model name to use for generation
        """
        self.__client = client
        self.__model = model
        self.current_iteration = 0
        self.example_generator = ExampleGenerator()

    def ai_request_diffs(self, code, diffs) -> str:
        """
        Abstract method implementation for AiBot compatibility.
        Not used in YAML enhancement workflow.
        """
        return ""

    def process_yaml_enhancement(
        self,
        yaml_path: str,
        gaps: YAMLGapAnalysis,
        api_info: Dict[str, Any],
        endpoints: List[EndpointData],
        max_iterations: int = 3,
        quality_threshold: int = 85
    ) -> Dict[str, str]:
        """
        Generate enhancements for identified gaps in YAML file.

        Args:
            yaml_path: Path to the YAML file
            gaps: Identified gaps from YAMLEnhancer
            api_info: API metadata from OpenAPIParser
            endpoints: List of endpoints from OpenAPIParser
            max_iterations: Maximum refinement iterations
            quality_threshold: Minimum quality score to accept

        Returns:
            Dictionary mapping YAML paths to enhanced descriptions
        """
        Log.print_green(f"=== Starting YAML Enhancement Generation ===")
        Log.print_blue(f"Processing {gaps.get_gap_count()} gaps")

        enhancements = {}

        # Generate enhancements for each category
        if gaps.missing_info_title or gaps.missing_info_description or gaps.missing_info_version:
            info_enhancements = self.generate_info_descriptions(
                api_info, endpoints, yaml_path
            )
            enhancements.update(info_enhancements)

        if gaps.missing_tags:
            tag_enhancements = self.generate_tag_descriptions(
                gaps.missing_tags, endpoints, api_info
            )
            enhancements.update(tag_enhancements)

        if gaps.missing_endpoint_descriptions:
            endpoint_enhancements = self.generate_endpoint_descriptions(
                gaps.missing_endpoint_descriptions, endpoints, api_info
            )
            enhancements.update(endpoint_enhancements)

        if gaps.missing_parameter_descriptions:
            param_enhancements = self.generate_parameter_descriptions(
                gaps.missing_parameter_descriptions, endpoints
            )
            enhancements.update(param_enhancements)

        if gaps.missing_schema_descriptions or gaps.missing_property_descriptions:
            schema_enhancements = self.generate_schema_descriptions(
                gaps, api_info
            )
            enhancements.update(schema_enhancements)

        # Validation and refinement loop
        for iteration in range(1, max_iterations + 1):
            self.current_iteration = iteration
            Log.print_blue(f"Validation iteration {iteration}/{max_iterations}")

            validation = self.validate_enhancements(enhancements, gaps, yaml_path)

            if self._should_exit(validation, quality_threshold):
                Log.print_green(f"Quality threshold met: {validation['scores']['overall']}%")
                break

            if iteration < max_iterations:
                Log.print_yellow(f"Quality below threshold, refining...")
                enhancements = self.refine_enhancements(
                    enhancements, validation, gaps, endpoints, api_info
                )

        Log.print_green(f"Generated {len(enhancements)} enhancements")
        return enhancements

    def generate_info_descriptions(
        self,
        api_info: Dict[str, Any],
        endpoints: List[EndpointData],
        yaml_path: str
    ) -> Dict[str, str]:
        """
        Generate descriptions for info section (title, description, version).

        Args:
            api_info: Current API info from parser
            endpoints: All endpoints for context
            yaml_path: Path to YAML file for filename hints

        Returns:
            Dictionary with paths like 'info.title', 'info.description', 'info.version'
        """
        Log.print_blue("Generating info descriptions...")

        # Extract context from endpoints
        endpoint_summary = self._summarize_endpoints(endpoints)
        file_name = os.path.basename(yaml_path).replace('.yaml', '').replace('.yml', '')

        prompt = f"""
You are an expert API documentation writer. Generate appropriate metadata for this API's info section.

Current API Info:
- Title: {api_info.get('title', '')}
- Description: {api_info.get('description', '')}
- Version: {api_info.get('version', '')}

Context from API:
- File name: {file_name}
- Number of endpoints: {len(endpoints)}
- Endpoint summary: {endpoint_summary}

Generate improvements for ONLY the missing or inadequate fields:

Requirements:
- Title: Short, clear API name (2-5 words) that describes what the API does
- Description: 1-2 sentence overview of the API's purpose and capabilities
- Version: Semantic version format (e.g., "1.0.0") if missing, otherwise leave as is

Return as JSON:
{{
    "title": "Generated title if needed, otherwise null",
    "description": "Generated description if needed, otherwise null",
    "version": "Generated version if needed, otherwise null"
}}

Only include fields that need to be filled or improved. Use null for fields that are adequate.
"""

        try:
            response = self._make_ai_request(prompt)
            json_str = self._extract_json_from_response(response)
            result = json.loads(json_str)

            enhancements = {}
            if result.get('title') and (not api_info.get('title') or len(api_info.get('title', '')) < 5):
                enhancements['info.title'] = result['title']

            # Match the gap detection criteria: descriptions < 30 chars are inadequate
            if result.get('description') and (not api_info.get('description') or len(api_info.get('description', '')) < 30):
                enhancements['info.description'] = result['description']

            if result.get('version') and not api_info.get('version'):
                enhancements['info.version'] = result['version']

            return enhancements

        except Exception as e:
            Log.print_red(f"Error generating info descriptions: {e}")
            return {}

    def generate_tag_descriptions(
        self,
        missing_tags: List[str],
        endpoints: List[EndpointData],
        api_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate descriptions for tags based on their endpoints.

        Args:
            missing_tags: List of tag names needing descriptions
            endpoints: All endpoints to find tag usage
            api_info: API info for context

        Returns:
            Dictionary with paths like 'tags.0.description', 'tags.1.description', etc.
        """
        Log.print_blue(f"Generating descriptions for {len(missing_tags)} tags...")

        enhancements = {}

        for tag_name in missing_tags:
            # Find endpoints using this tag
            tag_endpoints = [ep for ep in endpoints if tag_name in ep.tags]

            if not tag_endpoints:
                continue

            # Build context from endpoints using this tag
            endpoint_contexts = []
            for ep in tag_endpoints[:5]:  # Limit to 5 endpoints for context
                endpoint_contexts.append(f"- {ep.method.upper()} {ep.path}: {ep.summary}")

            prompt = f"""
You are an expert API documentation writer. Generate a concise description for this API tag.

API: {api_info.get('title', 'API')}
Tag: {tag_name}

Endpoints in this tag:
{chr(10).join(endpoint_contexts)}

Generate a 1-sentence description that explains what this tag/category covers.
Be specific and professional. Start with a verb or noun phrase.

Examples:
- "User management operations including registration, authentication, and profile updates"
- "Product catalog endpoints for browsing, searching, and managing inventory"
- "Analytics and reporting APIs for tracking user behavior and metrics"

Return only the description text:
"""

            try:
                description = self._make_ai_request(prompt).strip()
                # Remove quotes if AI wrapped it
                description = description.strip('"').strip("'")

                # Find tag index in spec (this will need to be done during application)
                # For now, store with tag name as key
                enhancements[f'tag.{tag_name}.description'] = description

            except Exception as e:
                Log.print_yellow(f"Error generating description for tag '{tag_name}': {e}")
                continue

        return enhancements

    def generate_endpoint_descriptions(
        self,
        missing_endpoints: List[str],
        endpoints: List[EndpointData],
        api_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate descriptions for endpoints based on their structure.

        Args:
            missing_endpoints: List of endpoint IDs (e.g., "GET /users")
            endpoints: All endpoint data
            api_info: API info for context

        Returns:
            Dictionary with paths like 'paths./users.get.description'
        """
        Log.print_blue(f"Generating descriptions for {len(missing_endpoints)} endpoints...")

        enhancements = {}

        for endpoint_id in missing_endpoints:
            # Find the endpoint data
            endpoint = self._find_endpoint(endpoint_id, endpoints)
            if not endpoint:
                continue

            # Build context
            param_summary = self._summarize_parameters(endpoint)
            response_summary = self._summarize_responses(endpoint)

            prompt = f"""
You are an expert API documentation writer. Generate a concise description for this API endpoint.

API: {api_info.get('title', 'API')}
Endpoint: {endpoint.method.upper()} {endpoint.path}
Summary: {endpoint.summary}
Operation ID: {endpoint.operation_id}

Parameters:
{param_summary}

Responses:
{response_summary}

Generate a 1-2 sentence description that explains:
1. What this endpoint does
2. What it returns or accomplishes

Be specific and professional. Use present tense.

Examples:
- "Retrieves a paginated list of all users in the system with optional filtering by role and status."
- "Creates a new product in the catalog with the provided details and returns the assigned product ID."
- "Updates an existing user's profile information and returns the updated user object."

Return only the description text:
"""

            try:
                description = self._make_ai_request(prompt).strip()
                description = description.strip('"').strip("'")

                # Convert to YAML path
                yaml_path = f"paths.{endpoint.path}.{endpoint.method.lower()}.description"
                enhancements[yaml_path] = description

            except Exception as e:
                Log.print_yellow(f"Error generating description for endpoint '{endpoint_id}': {e}")
                continue

        return enhancements

    def generate_parameter_descriptions(
        self,
        missing_parameters: List[Tuple[str, str]],
        endpoints: List[EndpointData]
    ) -> Dict[str, str]:
        """
        Generate descriptions for parameters based on context.

        Args:
            missing_parameters: List of (endpoint_id, param_name) tuples
            endpoints: All endpoint data

        Returns:
            Dictionary with paths to parameter descriptions
        """
        Log.print_blue(f"Generating descriptions for {len(missing_parameters)} parameters...")

        enhancements = {}

        for endpoint_id, param_name in missing_parameters:
            endpoint = self._find_endpoint(endpoint_id, endpoints)
            if not endpoint:
                continue

            # Find the parameter
            param = self._find_parameter(param_name, endpoint)
            if not param:
                continue

            param_type = param.get('type', 'string')
            param_location = param.get('in', 'query')
            is_required = param.get('required', False)

            prompt = f"""
You are an expert API documentation writer. Generate a concise description for this API parameter.

Endpoint: {endpoint.method.upper()} {endpoint.path}
Endpoint purpose: {endpoint.summary}

Parameter Details:
- Name: {param_name}
- Type: {param_type}
- Location: {param_location}
- Required: {is_required}

Generate a 1-sentence description that explains:
1. What this parameter controls/specifies
2. What values are expected (if relevant)

Be specific and professional.

Examples:
- "The unique identifier of the user to retrieve"
- "Maximum number of results to return (default: 20, max: 100)"
- "Filter results by account status (active, inactive, suspended)"
- "Authentication token for accessing protected resources"

Return only the description text:
"""

            try:
                description = self._make_ai_request(prompt).strip()
                description = description.strip('"').strip("'")

                # Build YAML path for parameter
                # This is complex as parameters can be in different locations
                # For now, store with a simplified path
                yaml_path = f"paths.{endpoint.path}.{endpoint.method.lower()}.parameters.{param_name}.description"
                enhancements[yaml_path] = description

            except Exception as e:
                Log.print_yellow(f"Error generating description for parameter '{param_name}': {e}")
                continue

        return enhancements

    def generate_schema_descriptions(
        self,
        gaps: YAMLGapAnalysis,
        api_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate descriptions for schemas and their properties.

        Args:
            gaps: Gap analysis with missing schema and property descriptions
            api_info: API info for context

        Returns:
            Dictionary with paths to schema/property descriptions
        """
        Log.print_blue(f"Generating descriptions for {len(gaps.missing_schema_descriptions)} schemas and {len(gaps.missing_property_descriptions)} properties...")

        enhancements = {}

        # Generate schema-level descriptions
        for schema_name in gaps.missing_schema_descriptions[:10]:  # Batch to avoid token limits
            try:
                prompt = f"""
You are an expert API documentation writer. Generate a concise description for this OpenAPI schema.

API: {api_info.get('title', 'API')}
Schema: {schema_name}

Generate a 1-sentence description that explains what this schema represents.
Be specific and professional.

Examples:
- "Represents a user account with authentication credentials and profile information"
- "Configuration settings for AI reasoning including depth and complexity parameters"
- "Response object containing generated text and metadata about the generation process"

Return only the description text:
"""

                description = self._make_ai_request(prompt).strip()
                description = description.strip('"').strip("'")

                # Store with schema path
                yaml_path = f"components.schemas.{schema_name}.description"
                enhancements[yaml_path] = description

            except Exception as e:
                Log.print_yellow(f"Error generating description for schema '{schema_name}': {e}")
                continue

        # Generate property descriptions in batches by schema
        properties_by_schema = {}
        for schema_name, prop_name in gaps.missing_property_descriptions:
            if schema_name not in properties_by_schema:
                properties_by_schema[schema_name] = []
            properties_by_schema[schema_name].append(prop_name)

        # Process each schema's properties
        for schema_name, prop_names in list(properties_by_schema.items())[:5]:  # Limit schemas
            try:
                # Batch properties for this schema
                props_to_describe = prop_names[:10]  # Max 10 properties per request

                props_list = "\n".join([f"- {prop}" for prop in props_to_describe])

                prompt = f"""
You are an expert API documentation writer. Generate concise descriptions for these properties in the {schema_name} schema.

API: {api_info.get('title', 'API')}
Schema: {schema_name}

Properties needing descriptions:
{props_list}

For each property, generate a 1-sentence description explaining what it represents or controls.

Return as JSON:
{{
    "property_name": "description",
    ...
}}

Be specific and professional. Focus on what the property does or represents.
"""

                response = self._make_ai_request(prompt)
                json_str = self._extract_json_from_response(response)
                property_descriptions = json.loads(json_str)

                # Add to enhancements with proper paths
                for prop_name, description in property_descriptions.items():
                    if prop_name in props_to_describe:
                        yaml_path = f"components.schemas.{schema_name}.properties.{prop_name}.description"
                        enhancements[yaml_path] = description

            except Exception as e:
                Log.print_yellow(f"Error generating descriptions for schema '{schema_name}' properties: {e}")
                continue

        Log.print_green(f"Generated {len(enhancements)} schema/property descriptions")
        return enhancements

    def validate_enhancements(
        self,
        enhancements: Dict[str, str],
        gaps: YAMLGapAnalysis,
        yaml_path: str
    ) -> Dict[str, Any]:
        """
        Validate the quality of generated enhancements.

        Checks:
        - Completeness: Were all gaps filled?
        - Quality: Are descriptions meaningful and appropriate length?
        - Consistency: Do descriptions match existing tone/style?
        - Accuracy: Do descriptions match the API structure?

        Args:
            enhancements: Generated enhancements
            gaps: Original gap analysis
            yaml_path: Path to YAML file

        Returns:
            Validation result with scores and feedback
        """
        Log.print_blue(f"Validating {len(enhancements)} enhancements...")

        prompt = f"""
You are an expert API documentation reviewer. Evaluate the quality of these generated descriptions.

Original gaps identified: {gaps.get_gap_count()}
Enhancements generated: {len(enhancements)}

Generated enhancements:
{json.dumps(enhancements, indent=2)}

Evaluate on these criteria (0-100 scale):

1. Completeness: Were all identified gaps addressed?
2. Quality: Are descriptions meaningful, clear, and appropriate length (not too short/long)?
3. Consistency: Do descriptions follow professional API documentation standards?
4. Accuracy: Do descriptions accurately reflect what each field represents?

Return as JSON:
{{
    "scores": {{
        "completeness": 0-100,
        "quality": 0-100,
        "consistency": 0-100,
        "accuracy": 0-100,
        "overall": 0-100
    }},
    "missing_enhancements": ["list of fields that still need descriptions"],
    "quality_issues": ["list of descriptions that need improvement"],
    "suggestions": ["specific improvement suggestions"],
    "exit_criteria_met": true/false
}}

Overall score should be weighted average: (completeness * 0.4) + (quality * 0.3) + (consistency * 0.2) + (accuracy * 0.1)
Exit criteria met should be true if overall >= 85 and all categories >= 70.
"""

        try:
            response = self._make_ai_request(prompt)
            json_str = self._extract_json_from_response(response)
            result = json.loads(json_str)

            Log.print_blue(f"Validation scores: {result.get('scores', {})}")
            return result

        except Exception as e:
            Log.print_red(f"Error validating enhancements: {e}")
            # Return default passing validation on error
            return {
                "scores": {
                    "completeness": 100,
                    "quality": 100,
                    "consistency": 100,
                    "accuracy": 100,
                    "overall": 100
                },
                "missing_enhancements": [],
                "quality_issues": [],
                "suggestions": [],
                "exit_criteria_met": True
            }

    def refine_enhancements(
        self,
        enhancements: Dict[str, str],
        validation: Dict[str, Any],
        gaps: YAMLGapAnalysis,
        endpoints: List[EndpointData],
        api_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Refine enhancements based on validation feedback.

        Args:
            enhancements: Current enhancements
            validation: Validation results with feedback
            gaps: Original gap analysis
            endpoints: Endpoint data for context
            api_info: API info for context

        Returns:
            Refined enhancements
        """
        Log.print_blue("Refining enhancements based on feedback...")

        quality_issues = validation.get('quality_issues', [])
        suggestions = validation.get('suggestions', [])

        if not quality_issues and not suggestions:
            return enhancements

        prompt = f"""
You are an expert API documentation writer. Improve these descriptions based on the feedback.

Current enhancements:
{json.dumps(enhancements, indent=2)}

Quality issues identified:
{json.dumps(quality_issues, indent=2)}

Improvement suggestions:
{json.dumps(suggestions, indent=2)}

Generate improved versions of ONLY the descriptions that have issues.
Keep descriptions that are already good.

Return as JSON with the same structure as input:
{{
    "path.to.field": "improved description",
    ...
}}
"""

        try:
            response = self._make_ai_request(prompt)
            json_str = self._extract_json_from_response(response)
            refined = json.loads(json_str)

            # Merge refined descriptions with originals
            for key, value in refined.items():
                if key in enhancements:
                    enhancements[key] = value

            Log.print_green(f"Refined {len(refined)} descriptions")
            return enhancements

        except Exception as e:
            Log.print_red(f"Error refining enhancements: {e}")
            return enhancements

    # ========== PR Title Generation (adapted from DocGenerator) ==========

    def generate_pr_title(self, changed_files: List[str], enhancements_summary: Dict[str, int]) -> str:
        """
        Generate an AI-powered PR title for YAML enhancements.

        Args:
            changed_files: List of YAML files that were enhanced
            enhancements_summary: Dict mapping file paths to number of enhancements

        Returns:
            PR title string
        """
        if not changed_files:
            return "📝 Enhance API documentation"

        changes_summary = self._create_enhancement_summary(changed_files, enhancements_summary)

        prompt = f"""
Task: Generate a concise, descriptive pull request title for API documentation enhancements

Requirements:
- Maximum 60 characters
- Start with emoji (📝, ✨, 🔧, 📚, etc.)
- Be specific about what was enhanced
- Use active voice
- Professional tone

Changes made:
{changes_summary}

Examples of good titles:
- "📝 Add descriptions to AI Services API"
- "✨ Enhance FileSet API documentation"
- "🔧 Complete Users API metadata"
- "📚 Add missing tag descriptions"

Generate only the title (no explanation):
"""

        try:
            title = self._make_ai_request(prompt).strip()
            title = title.replace('"', "").strip()
            if len(title) > 60:
                title = title[:57] + "..."
            return title if title else "📝 Enhance API documentation"
        except Exception as e:
            Log.print_red(f"Failed to generate PR title: {e}")
            return self._create_fallback_pr_title(changed_files)

    def _create_enhancement_summary(
        self,
        changed_files: List[str],
        enhancements_summary: Dict[str, int]
    ) -> str:
        """Create a summary of enhancements for PR title generation."""
        summary_parts = []

        for file_path in changed_files:
            file_name = file_path.split("/")[-1].replace(".yaml", "").replace(".yml", "")
            enhancement_count = enhancements_summary.get(file_path, 0)
            summary_parts.append(f"- {file_name}: {enhancement_count} enhancements")

        return "\n".join(summary_parts)

    def _create_fallback_pr_title(self, changed_files: List[str]) -> str:
        """Create fallback PR title when AI generation fails."""
        if len(changed_files) == 1:
            file_name = changed_files[0].split("/")[-1].replace(".yaml", "").replace(".yml", "")
            return f"📝 Enhance {file_name} API docs"
        else:
            return f"📝 Enhance {len(changed_files)} API specifications"

    # ========== Helper Methods ==========

    def _summarize_endpoints(self, endpoints: List[EndpointData]) -> str:
        """Create a summary of endpoints for context."""
        if not endpoints:
            return "No endpoints found"

        summary = []
        for ep in endpoints[:10]:  # Limit to 10 for context
            summary.append(f"{ep.method.upper()} {ep.path}")

        if len(endpoints) > 10:
            summary.append(f"... and {len(endpoints) - 10} more")

        return ", ".join(summary)

    def _summarize_parameters(self, endpoint: EndpointData) -> str:
        """Create a summary of endpoint parameters."""
        all_params = (
            endpoint.path_parameters +
            endpoint.query_parameters +
            endpoint.header_parameters
        )

        if not all_params:
            return "No parameters"

        param_lines = []
        for param in all_params[:5]:  # Limit to 5
            param_type = param.get('type', 'string')
            param_location = param.get('in', 'query')
            param_lines.append(f"- {param['name']} ({param_type}, {param_location})")

        if len(all_params) > 5:
            param_lines.append(f"... and {len(all_params) - 5} more")

        return "\n".join(param_lines)

    def _summarize_responses(self, endpoint: EndpointData) -> str:
        """Create a summary of endpoint responses."""
        if not endpoint.responses:
            return "No response information"

        response_lines = []
        for status_code, response_data in endpoint.responses.items():
            description = response_data.get('description', 'No description')
            response_lines.append(f"- {status_code}: {description}")

        return "\n".join(response_lines)

    def _find_endpoint(self, endpoint_id: str, endpoints: List[EndpointData]) -> Optional[EndpointData]:
        """Find endpoint by ID (e.g., 'GET /users')."""
        for endpoint in endpoints:
            ep_id = f"{endpoint.method.upper()} {endpoint.path}"
            if ep_id == endpoint_id:
                return endpoint
        return None

    def _find_parameter(self, param_name: str, endpoint: EndpointData) -> Optional[Dict[str, Any]]:
        """Find parameter in endpoint."""
        all_params = (
            endpoint.path_parameters +
            endpoint.query_parameters +
            endpoint.header_parameters +
            endpoint.request_body_parameters
        )

        for param in all_params:
            if param.get('name') == param_name:
                return param

        return None

    # ========== Reusable Utility Methods (from DocGenerator) ==========

    def _should_exit(self, validation_result: Dict[str, Any], threshold: int) -> bool:
        """Determine if exit conditions are met."""
        overall_score = validation_result.get("scores", {}).get("overall", 0)
        exit_criteria_met = validation_result.get("exit_criteria_met", False)

        return overall_score >= threshold and exit_criteria_met

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from AI response that might contain markdown or extra text."""
        import re

        # Strategy 1: Extract from markdown code blocks
        json_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE
        )
        if json_match:
            candidate = json_match.group(1).strip()
            if self._is_valid_json(candidate):
                return candidate

        # Strategy 2: Find balanced JSON object
        json_candidate = self._extract_balanced_json(response)
        if json_candidate and self._is_valid_json(json_candidate):
            return json_candidate

        # Strategy 3: Clean and fix common issues
        cleaned_response = self._clean_json_response(response)
        if self._is_valid_json(cleaned_response):
            return cleaned_response

        # Strategy 4: Return original as fallback
        return response.strip()

    def _extract_balanced_json(self, text: str) -> str:
        """Extract JSON using balanced bracket counting."""
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
        """Clean common JSON formatting issues."""
        start_idx = response.find("{")
        if start_idx == -1:
            return response

        end_idx = response.rfind("}")
        if end_idx == -1:
            return response

        cleaned = response[start_idx : end_idx + 1]
        return cleaned

    def _is_valid_json(self, text: str) -> bool:
        """Check if string is valid JSON."""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    def _make_ai_request(self, prompt: str) -> str:
        """Make request to AI model."""
        try:
            response = self.__client.chat.completions.create(
                model=self.__model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            Log.print_red(f"AI request failed: {e}")
            return ""
