"""
YAML Enhancer Module

Analyzes OpenAPI YAML specifications to identify missing or inadequate descriptions.
Works with OpenAPIParser to detect gaps in API documentation.
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any

sys.path.insert(0, os.path.dirname(__file__))
from openapi.openapi_parser import OpenAPIParser, EndpointData
from log import Log


@dataclass
class YAMLGapAnalysis:
    """
    Represents missing or inadequate descriptions in an OpenAPI YAML file.
    """
    # Top-level metadata gaps
    missing_info_title: bool = False
    missing_info_description: bool = False
    missing_info_version: bool = False

    # Tag description gaps (list of tag names with missing descriptions)
    missing_tags: List[str] = field(default_factory=list)

    # Endpoint description gaps (list of operation IDs or paths)
    missing_endpoint_descriptions: List[str] = field(default_factory=list)

    # Parameter description gaps (list of tuples: (endpoint_id, param_name))
    missing_parameter_descriptions: List[Tuple[str, str]] = field(default_factory=list)

    # Schema description gaps (list of schema names)
    missing_schema_descriptions: List[str] = field(default_factory=list)

    # Property description gaps (list of tuples: (schema_name, property_name))
    missing_property_descriptions: List[Tuple[str, str]] = field(default_factory=list)

    # File being analyzed
    yaml_file: str = ""

    def has_gaps(self) -> bool:
        """Check if there are any gaps identified."""
        return (
            self.missing_info_title or
            self.missing_info_description or
            self.missing_info_version or
            len(self.missing_tags) > 0 or
            len(self.missing_endpoint_descriptions) > 0 or
            len(self.missing_parameter_descriptions) > 0 or
            len(self.missing_schema_descriptions) > 0 or
            len(self.missing_property_descriptions) > 0
        )

    def get_gap_count(self) -> int:
        """Get total number of gaps identified."""
        count = 0
        if self.missing_info_title:
            count += 1
        if self.missing_info_description:
            count += 1
        if self.missing_info_version:
            count += 1
        count += len(self.missing_tags)
        count += len(self.missing_endpoint_descriptions)
        count += len(self.missing_parameter_descriptions)
        count += len(self.missing_schema_descriptions)
        count += len(self.missing_property_descriptions)
        return count

    def get_summary(self) -> str:
        """Get a human-readable summary of gaps."""
        if not self.has_gaps():
            return "No gaps found - YAML is complete"

        parts = []
        if self.missing_info_title:
            parts.append("info.title")
        if self.missing_info_description:
            parts.append("info.description")
        if self.missing_info_version:
            parts.append("info.version")
        if self.missing_tags:
            parts.append(f"{len(self.missing_tags)} tag descriptions")
        if self.missing_endpoint_descriptions:
            parts.append(f"{len(self.missing_endpoint_descriptions)} endpoint descriptions")
        if self.missing_parameter_descriptions:
            parts.append(f"{len(self.missing_parameter_descriptions)} parameter descriptions")
        if self.missing_schema_descriptions:
            parts.append(f"{len(self.missing_schema_descriptions)} schema descriptions")
        if self.missing_property_descriptions:
            parts.append(f"{len(self.missing_property_descriptions)} property descriptions")

        return f"Found {self.get_gap_count()} gaps: " + ", ".join(parts)


@dataclass
class Enhancement:
    """
    Represents a single enhancement to apply to the YAML.
    """
    yaml_path: str  # JSONPath or dot-notation path (e.g., "info.description")
    current_value: Optional[str]  # Existing value (if any)
    suggested_value: str  # AI-generated description
    confidence: float = 1.0  # AI confidence score (0.0-1.0)
    reasoning: str = ""  # Why AI chose this description
    field_type: str = ""  # Type of field (info, tag, endpoint, parameter, schema, property)


class YAMLEnhancer:
    """
    Analyzes OpenAPI YAML files to identify missing descriptions and documentation gaps.
    """

    def __init__(self, min_description_length: int = 10):
        """
        Initialize the YAML enhancer.

        Args:
            min_description_length: Minimum length for a description to be considered adequate
        """
        self.min_description_length = min_description_length

    def analyze_yaml_gaps(
        self,
        yaml_path: str,
        parser: Optional[OpenAPIParser] = None
    ) -> YAMLGapAnalysis:
        """
        Analyze an OpenAPI YAML file to identify missing descriptions.

        Args:
            yaml_path: Path to the YAML file
            parser: Optional pre-initialized OpenAPIParser (if None, will create one)

        Returns:
            YAMLGapAnalysis object with all identified gaps
        """
        try:
            # Create parser if not provided
            if parser is None:
                parser = OpenAPIParser(yaml_path)

            gaps = YAMLGapAnalysis(yaml_file=yaml_path)

            # Analyze info section
            self._analyze_info_gaps(parser, gaps)

            # Analyze tags
            self._analyze_tag_gaps(parser, gaps)

            # Analyze endpoints
            self._analyze_endpoint_gaps(parser, gaps)

            # Analyze schemas (if available)
            self._analyze_schema_gaps(parser, gaps)

            Log.print_blue(f"Gap analysis complete: {gaps.get_summary()}")
            return gaps

        except Exception as e:
            Log.print_red(f"Error analyzing YAML gaps: {e}")
            # Return empty gaps on error
            return YAMLGapAnalysis(yaml_file=yaml_path)

    def _analyze_info_gaps(self, parser: OpenAPIParser, gaps: YAMLGapAnalysis) -> None:
        """Analyze the info section for missing descriptions."""
        try:
            api_info = parser.get_api_info()

            # Check title
            title = api_info.get('title', '')
            if not title or self._is_inadequate_description(title, 'title'):
                gaps.missing_info_title = True

            # Check description - use stricter criteria
            description = api_info.get('description', '')
            if not description or self._is_inadequate_description(description, 'description'):
                gaps.missing_info_description = True
            # Additional check: if it's too generic, mark as inadequate
            elif len(description) < 30:  # Very short descriptions are likely inadequate
                gaps.missing_info_description = True

            # Check version
            if not api_info.get('version') or api_info.get('version') == '':
                gaps.missing_info_version = True

        except Exception as e:
            Log.print_yellow(f"Error analyzing info section: {e}")

    def _analyze_tag_gaps(self, parser: OpenAPIParser, gaps: YAMLGapAnalysis) -> None:
        """Analyze tags for missing descriptions."""
        try:
            spec = parser.spec
            tags = spec.get('tags', [])

            for tag in tags:
                tag_name = tag.get('name', '')
                tag_description = tag.get('description', '')

                if not tag_description or self._is_inadequate_description(tag_description):
                    gaps.missing_tags.append(tag_name)

        except Exception as e:
            Log.print_yellow(f"Error analyzing tags: {e}")

    def _analyze_endpoint_gaps(self, parser: OpenAPIParser, gaps: YAMLGapAnalysis) -> None:
        """Analyze endpoints for missing descriptions and parameters."""
        try:
            endpoints = parser.parse_all_endpoints()

            for endpoint in endpoints:
                # Check endpoint description
                if not endpoint.description or self._is_inadequate_description(endpoint.description):
                    endpoint_id = f"{endpoint.method.upper()} {endpoint.path}"
                    gaps.missing_endpoint_descriptions.append(endpoint_id)

                # Check parameter descriptions
                self._check_parameter_descriptions(endpoint, gaps)

        except Exception as e:
            Log.print_yellow(f"Error analyzing endpoints: {e}")

    def _check_parameter_descriptions(self, endpoint: EndpointData, gaps: YAMLGapAnalysis) -> None:
        """Check parameter descriptions for an endpoint."""
        endpoint_id = f"{endpoint.method.upper()} {endpoint.path}"

        # Check all parameter types
        all_parameters = (
            endpoint.path_parameters +
            endpoint.query_parameters +
            endpoint.header_parameters +
            endpoint.request_body_parameters
        )

        for param in all_parameters:
            param_name = param.get('name', '')
            param_description = param.get('description', '')

            if not param_description or self._is_inadequate_description(param_description):
                gaps.missing_parameter_descriptions.append((endpoint_id, param_name))

    def _analyze_schema_gaps(self, parser: OpenAPIParser, gaps: YAMLGapAnalysis) -> None:
        """Analyze component schemas for missing descriptions."""
        try:
            spec = parser.spec

            # Get schemas location (OpenAPI 3.x uses components.schemas, 2.0 uses definitions)
            schemas = {}
            if 'components' in spec and 'schemas' in spec['components']:
                schemas = spec['components']['schemas']
            elif 'definitions' in spec:
                schemas = spec['definitions']

            for schema_name, schema_obj in schemas.items():
                # Check schema description
                schema_description = schema_obj.get('description', '')
                if not schema_description or self._is_inadequate_description(schema_description):
                    gaps.missing_schema_descriptions.append(schema_name)

                # Check property descriptions
                properties = schema_obj.get('properties', {})
                for prop_name, prop_obj in properties.items():
                    prop_description = prop_obj.get('description', '')
                    if not prop_description or self._is_inadequate_description(prop_description):
                        gaps.missing_property_descriptions.append((schema_name, prop_name))

        except Exception as e:
            Log.print_yellow(f"Error analyzing schemas: {e}")

    def _is_inadequate_description(self, description: str, field_name: str = "") -> bool:
        """
        Check if a description is inadequate (too short or just repeats field name).

        Args:
            description: The description to check
            field_name: Optional field name to check for repetition

        Returns:
            True if description is inadequate, False otherwise
        """
        if not description or len(description.strip()) < self.min_description_length:
            return True

        # Check if it's just whitespace
        if description.strip() == '':
            return True

        # Check for generic/low-quality descriptions
        description_lower = description.strip().lower()

        # Generic API descriptions that don't add value
        generic_phrases = [
            'api', 'service', 'endpoint', 'request', 'response',
            'documentation', 'specification'
        ]

        # If description is just generic words, it's inadequate
        words = description_lower.split()
        if len(words) <= 3 and all(word in generic_phrases for word in words):
            return True

        # Check if it just repeats the field name
        if field_name:
            field_lower = field_name.lower().replace('_', ' ').replace('-', ' ')
            if field_lower in description_lower and len(description) < 30:
                return True

        return False

    def get_enhancement_priorities(self, gaps: YAMLGapAnalysis) -> List[str]:
        """
        Get a prioritized list of enhancement categories based on gaps.

        Returns categories in order of importance:
        1. info (most important for API understanding)
        2. tags (helps organize endpoints)
        3. endpoints (core functionality)
        4. parameters (helps users understand how to call APIs)
        5. schemas (helps understand data structures)

        Args:
            gaps: The gap analysis results

        Returns:
            List of category names in priority order
        """
        priorities = []

        if gaps.missing_info_title or gaps.missing_info_description or gaps.missing_info_version:
            priorities.append('info')

        if gaps.missing_tags:
            priorities.append('tags')

        if gaps.missing_endpoint_descriptions:
            priorities.append('endpoints')

        if gaps.missing_parameter_descriptions:
            priorities.append('parameters')

        if gaps.missing_schema_descriptions or gaps.missing_property_descriptions:
            priorities.append('schemas')

        return priorities

    def fix_server_url_templates(self, yaml_path: str, parser: Optional[OpenAPIParser] = None) -> Dict[str, Any]:
        """
        Fix server URL templates that use angle brackets <variable> instead of {variable}.

        Args:
            yaml_path: Path to the YAML file
            parser: Optional pre-initialized OpenAPIParser

        Returns:
            Dictionary of fixes applied with paths and new values
        """
        import re

        fixes = {}

        try:
            if parser is None:
                parser = OpenAPIParser(yaml_path)

            spec = parser.spec
            servers = spec.get('servers', [])

            for idx, server in enumerate(servers):
                url = server.get('url', '')

                # Check if URL contains angle bracket variables like <subdomain>
                angle_bracket_pattern = r'<([a-zA-Z_][a-zA-Z0-9_]*)>'
                matches = re.findall(angle_bracket_pattern, url)

                if matches:
                    # Convert angle brackets to curly braces
                    fixed_url = re.sub(r'<([a-zA-Z_][a-zA-Z0-9_]*)>', r'{\1}', url)

                    # Create variables section if it doesn't exist
                    if 'variables' not in server:
                        from ruamel.yaml.comments import CommentedMap

                        variables = CommentedMap()
                        for var_name in matches:
                            var_spec = CommentedMap()
                            var_spec['default'] = self._get_default_value_for_variable(var_name)
                            var_spec['description'] = f'Your {var_name.replace("_", " ")}'
                            variables[var_name] = var_spec

                        fixes[f'servers.{idx}.url'] = fixed_url
                        fixes[f'servers.{idx}.variables'] = variables

                        Log.print_blue(f"Fixed server URL template: {url} → {fixed_url}")

            return fixes

        except Exception as e:
            Log.print_yellow(f"Error fixing server URL templates: {e}")
            return {}

    def _get_default_value_for_variable(self, var_name: str) -> str:
        """
        Get a sensible default value for a server URL variable.

        Args:
            var_name: Variable name (e.g., 'subdomain', 'region')

        Returns:
            Default value string
        """
        # Common variable name mappings
        defaults = {
            'subdomain': 'your-instance',
            'instance': 'your-instance',
            'region': 'us-east-1',
            'environment': 'production',
            'env': 'prod',
            'domain': 'example',
            'tenant': 'your-tenant',
            'workspace': 'default'
        }

        return defaults.get(var_name.lower(), f'your-{var_name.replace("_", "-")}')
