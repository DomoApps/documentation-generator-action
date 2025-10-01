# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

from typing import Any, Dict, List, Optional
import json
import prance
from markdownify import markdownify as md
from .example_generator import ExampleGenerator
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from log import Log


class EndpointData:
    """Structured data for a single API endpoint"""

    def __init__(self):
        self.path: str = ""
        self.method: str = ""
        self.operation_id: str = ""
        self.summary: str = ""
        self.description: str = ""
        self.tags: List[str] = []

        # Parameters
        self.path_parameters: List[Dict[str, Any]] = []
        self.query_parameters: List[Dict[str, Any]] = []
        self.header_parameters: List[Dict[str, Any]] = []

        # Request body
        self.request_body_schema: Optional[Dict[str, Any]] = None
        self.request_body_description: str = ""  # Schema-level description
        self.request_body_parameters: List[Dict[str, Any]] = []
        self.request_body_example: Optional[Any] = None

        # Responses
        self.responses: Dict[str, Dict[str, Any]] = {}
        self.success_response_example: Optional[Any] = None
        self.success_status_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'path': self.path,
            'method': self.method.upper(),
            'operation_id': self.operation_id,
            'summary': self.summary,
            'description': self.description,
            'tags': self.tags,
            'path_parameters': self.path_parameters,
            'query_parameters': self.query_parameters,
            'header_parameters': self.header_parameters,
            'request_body_description': self.request_body_description,
            'request_body_parameters': self.request_body_parameters,
            'request_body_example': self.request_body_example,
            'responses': self.responses,
            'success_response_example': self.success_response_example,
            'success_status_code': self.success_status_code,
        }


class OpenAPIParser:
    """Parse OpenAPI specifications deterministically using prance for $ref resolution"""

    def __init__(self, yaml_path: str):
        """
        Initialize parser with OpenAPI specification file

        Args:
            yaml_path: Path to OpenAPI YAML file
        """
        Log.print_green(f"Parsing OpenAPI specification: {yaml_path}")

        # Pre-process the YAML to handle common invalid patterns
        import yaml
        import tempfile
        with open(yaml_path, 'r') as f:
            raw_spec = yaml.safe_load(f)

        # Fix common issues that break validation but are common in real specs
        self._fix_spec_issues(raw_spec)

        # Write cleaned spec to temp file for prance
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            yaml.dump(raw_spec, tmp)
            tmp_path = tmp.name

        # Don't use prance's ResolvingParser - it fails completely if ANY ref is circular
        # Instead, use raw spec and manually resolve refs on-demand
        # This allows us to handle most refs while gracefully dealing with circular ones
        Log.print_green("Using manual $ref resolution (avoids prance failures on circular refs)")
        self.spec = raw_spec

        # Clean up temp file
        import os
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        self.example_generator = ExampleGenerator()

        self.info = self.spec.get('info', {})
        self.api_title = self.info.get('title', 'API')
        self.api_description = self.info.get('description', '')
        self.api_version = self.info.get('version', '1.0.0')

        Log.print_green(f"Successfully parsed: {self.api_title} v{self.api_version}")

    def _fix_spec_issues(self, spec: Dict[str, Any]):
        """
        Fix common OpenAPI spec issues that break validation but are common in practice

        Args:
            spec: The raw OpenAPI spec dictionary (modified in-place)
        """
        # Fix empty server objects
        if 'servers' in spec:
            servers = spec['servers']
            if isinstance(servers, list):
                for i, server in enumerate(servers):
                    if isinstance(server, dict) and not server.get('url'):
                        # Replace empty server with a placeholder
                        spec['servers'][i] = {'url': 'https://api.example.com'}
                        Log.print_red(f"Warning: Fixed empty server object at index {i}")

        # Add more fixes here as we encounter them in real-world specs
        # For example: missing required fields, invalid formats, etc.

    def parse_all_endpoints(self) -> List[EndpointData]:
        """
        Parse all endpoints from the OpenAPI spec

        Returns:
            List of EndpointData objects, one per endpoint
        """
        endpoints = []
        paths = self.spec.get('paths', {})

        for path, path_item in paths.items():
            # Skip common fields that aren't HTTP methods
            common_params = path_item.get('parameters', [])

            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if method in path_item:
                    operation = path_item[method]
                    endpoint = self._parse_endpoint(path, method, operation, common_params)
                    endpoints.append(endpoint)

        Log.print_green(f"Parsed {len(endpoints)} endpoints from OpenAPI spec")
        return endpoints

    def _parse_endpoint(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any],
        common_params: List[Dict[str, Any]]
    ) -> EndpointData:
        """Parse a single endpoint (all $refs already resolved by prance)"""
        endpoint = EndpointData()

        endpoint.path = path
        endpoint.method = method
        endpoint.operation_id = operation.get('operationId', '')
        endpoint.summary = operation.get('summary', '')
        endpoint.description = operation.get('description', '')
        endpoint.tags = operation.get('tags', [])

        # Parse parameters
        all_params = common_params + operation.get('parameters', [])
        self._parse_parameters(endpoint, all_params)

        # Parse request body
        if 'requestBody' in operation:
            self._parse_request_body(endpoint, operation['requestBody'], operation)

        # Parse responses
        self._parse_responses(endpoint, operation)

        return endpoint

    def _parse_parameters(self, endpoint: EndpointData, parameters: List[Dict[str, Any]]):
        """Parse parameters into categorized lists"""
        for param in parameters:
            param_in = param.get('in', 'query')
            param_data = self._extract_parameter_data(param)

            if param_in == 'path':
                endpoint.path_parameters.append(param_data)
            elif param_in == 'query':
                endpoint.query_parameters.append(param_data)
            elif param_in == 'header':
                endpoint.header_parameters.append(param_data)

    def _extract_parameter_data(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured parameter data from resolved schema"""
        schema = param.get('schema', {})

        # Handle unresolved $ref
        if '$ref' in schema:
            ref_path = schema['$ref']
            # Check if it's a _Nullable ref (these are optional complex types)
            if '_Nullable' in ref_path:
                type_name = ref_path.split('/')[-1].replace('_Nullable', '')
                schema = {'type': 'object', 'description': f"Optional {type_name} object (nullable)"}
            else:
                Log.print_red(f"Warning: Unresolved $ref in parameter: {ref_path}")
                schema = {'type': 'object'}  # Fallback

        param_type = schema.get('type', 'string')
        param_format = schema.get('format', '')
        if param_format:
            param_type = f"{param_type} ({param_format})"

        # Generate example
        example = param.get('example')
        if not example and 'example' in schema:
            example = schema['example']
        if not example:
            try:
                example = self.example_generator.generate_from_schema(schema, param.get('name'))
            except Exception as e:
                Log.print_red(f"Warning: Failed to generate example for {param.get('name')}: {e}")
                example = None

        return {
            'name': param.get('name', 'unnamed'),
            'type': param_type,
            'required': param.get('required', False),
            'description': param.get('description', ''),
            'example': example,
            'enum': schema.get('enum', []),
            'default': schema.get('default'),
        }

    def _parse_request_body(self, endpoint: EndpointData, request_body: Dict[str, Any], operation: Dict[str, Any]):
        """Parse request body schema and generate examples"""
        # Try to get existing example first
        existing_example = self.example_generator.extract_existing_example(operation, 'requestBody')
        if existing_example:
            endpoint.request_body_example = existing_example

        # Get the schema (already resolved by prance)
        content = request_body.get('content', {})
        for media_type, media_obj in content.items():
            schema = media_obj.get('schema', {})
            if not schema:
                continue

            endpoint.request_body_schema = schema

            # Handle $ref - manually resolve it
            if '$ref' in schema:
                schema = self._resolve_ref(schema['$ref'])

            # Capture schema-level description (provides important context!)
            schema_description = schema.get('description', '')
            if schema_description:
                # Convert HTML to markdown for cleaner output
                endpoint.request_body_description = md(schema_description, strip=['p']).strip()

            # Extract properties as parameters
            properties = schema.get('properties', {})
            required_fields = schema.get('required', [])

            # Convert properties to parameter list
            for prop_name, prop_schema in properties.items():
                # Handle $ref in properties
                if '$ref' in prop_schema:
                    ref_path = prop_schema['$ref']
                    # Check if it's a _Nullable ref (these are optional complex types)
                    if '_Nullable' in ref_path:
                        # Extract the base type name
                        type_name = ref_path.split('/')[-1].replace('_Nullable', '')
                        prop_schema = {
                            'type': 'object',
                            'description': f"Optional {type_name} object (nullable)"
                        }
                    else:
                        # Resolve the ref (with recursion protection)
                        prop_schema = self._resolve_ref(ref_path)

                param_type = prop_schema.get('type', 'string')
                param_format = prop_schema.get('format', '')
                if param_format:
                    param_type = f"{param_type} ({param_format})"

                # Generate example
                example = prop_schema.get('example')
                if not example:
                    try:
                        example = self.example_generator.generate_from_schema(prop_schema, prop_name)
                    except Exception as e:
                        Log.print_red(f"Warning: Failed to generate example for {prop_name}: {e}")
                        example = None

                endpoint.request_body_parameters.append({
                    'name': prop_name,
                    'type': param_type,
                    'required': prop_name in required_fields,
                    'description': prop_schema.get('description', ''),
                    'example': example,
                    'enum': prop_schema.get('enum', []),
                })

            # Generate full example if not already present
            if not endpoint.request_body_example:
                try:
                    endpoint.request_body_example = self.example_generator.generate_from_schema(schema)
                except Exception as e:
                    Log.print_red(f"Warning: Failed to generate request body example: {e}")
                    endpoint.request_body_example = None

            break  # Only process first media type

    def _parse_responses(self, endpoint: EndpointData, operation: Dict[str, Any]):
        """Parse response definitions"""
        responses = operation.get('responses', {})

        # Try to get existing success example
        existing_example = self.example_generator.extract_existing_example(operation, 'responses')
        if existing_example:
            endpoint.success_response_example = existing_example

        for status_code, response in responses.items():
            description = response.get('description', '')
            content = response.get('content', {})

            response_data = {
                'status_code': status_code,
                'description': description,
                'examples': []
            }

            for media_type, media_obj in content.items():
                schema = media_obj.get('schema', {})
                if schema:
                    # Get examples
                    examples = media_obj.get('examples', {})
                    if examples:
                        for example_name, example_obj in examples.items():
                            response_data['examples'].append(example_obj.get('value'))
                    elif 'example' in media_obj:
                        response_data['examples'].append(media_obj['example'])
                    else:
                        # Generate example from schema
                        try:
                            generated = self.example_generator.generate_from_schema(schema)
                            response_data['examples'].append(generated)
                        except Exception as e:
                            Log.print_red(f"Warning: Failed to generate response example: {e}")
                            response_data['examples'].append({})

            endpoint.responses[status_code] = response_data

            # Set success response
            if status_code.startswith('2') and not endpoint.success_response_example:
                if response_data['examples']:
                    endpoint.success_response_example = response_data['examples'][0]
                    endpoint.success_status_code = status_code

        # Try to set success status if still not set
        if not endpoint.success_status_code:
            for code in ['200', '201', '202', '204']:
                if code in endpoint.responses:
                    endpoint.success_status_code = code
                    break

    def _resolve_ref(self, ref_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Manually resolve a $ref from components/schemas

        Args:
            ref_path: Reference like '#/components/schemas/SomeName'
            max_depth: Maximum recursion depth to prevent infinite loops

        Returns:
            Resolved schema or fallback object schema
        """
        if max_depth <= 0:
            Log.print_red(f"Warning: Max recursion depth reached resolving {ref_path}")
            return {'type': 'object', 'description': '(Max recursion depth reached)'}

        if not ref_path.startswith('#/components/schemas/'):
            return {'type': 'object'}

        schema_name = ref_path.split('/')[-1]
        components_schemas = self.spec.get('components', {}).get('schemas', {})

        if schema_name not in components_schemas:
            return {'type': 'object'}

        schema = components_schemas[schema_name]

        # If this schema itself has a $ref, resolve it (but limit depth)
        if isinstance(schema, dict) and '$ref' in schema:
            return self._resolve_ref(schema['$ref'], max_depth - 1)

        return schema

    def get_api_info(self) -> Dict[str, Any]:
        """Get API-level information"""
        return {
            'title': self.api_title,
            'description': self.api_description,
            'version': self.api_version,
            'servers': self.spec.get('servers', []),
            'tags': self.spec.get('tags', [])
        }

    def get_endpoints_by_tag(self, tag: str) -> List[EndpointData]:
        """Get all endpoints with a specific tag"""
        all_endpoints = self.parse_all_endpoints()
        return [ep for ep in all_endpoints if tag in ep.tags]

    def format_example_as_json(self, example: Any) -> str:
        """Format an example as pretty-printed JSON"""
        if example is None:
            return ""
        try:
            return json.dumps(example, indent=2)
        except (TypeError, ValueError):
            return str(example)
