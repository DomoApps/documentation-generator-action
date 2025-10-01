# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class ExampleGenerator:
    """Generate realistic examples from resolved OpenAPI schemas"""

    def generate_from_schema(self, schema: Dict[str, Any], property_name: str = None) -> Any:
        """
        Generate an example value from a resolved schema definition
        (assumes all $refs have been resolved by prance)

        Args:
            schema: Resolved OpenAPI schema dictionary (no $refs)
            property_name: Name of the property (used for contextual examples)

        Returns:
            Example value matching the schema type
        """
        # Use existing example if available
        if 'example' in schema:
            return schema['example']

        schema_type = schema.get('type', 'string')
        schema_format = schema.get('format')
        enum_values = schema.get('enum')

        # Handle enum types
        if enum_values:
            return enum_values[0]

        # Handle oneOf, anyOf, allOf
        if 'oneOf' in schema or 'anyOf' in schema:
            options = schema.get('oneOf') or schema.get('anyOf')
            if options:
                return self.generate_from_schema(options[0], property_name)

        if 'allOf' in schema:
            # Merge all schemas and generate
            merged = self._merge_all_of(schema['allOf'])
            return self.generate_from_schema(merged, property_name)

        # Handle different types
        if schema_type == 'string':
            return self._generate_string_example(schema_format, property_name, schema)
        elif schema_type == 'integer':
            return self._generate_integer_example(schema_format, property_name)
        elif schema_type == 'number':
            return self._generate_number_example(schema_format, property_name)
        elif schema_type == 'boolean':
            return False
        elif schema_type == 'array':
            return self._generate_array_example(schema, property_name)
        elif schema_type == 'object':
            return self._generate_object_example(schema)
        else:
            return None

    def _merge_all_of(self, schemas: list) -> Dict[str, Any]:
        """Merge allOf schemas into a single schema"""
        merged = {}
        for schema in schemas:
            if 'properties' in schema:
                if 'properties' not in merged:
                    merged['properties'] = {}
                merged['properties'].update(schema['properties'])
            if 'required' in schema:
                if 'required' not in merged:
                    merged['required'] = []
                merged['required'].extend(schema['required'])
            # Merge other fields
            for key, value in schema.items():
                if key not in ['properties', 'required']:
                    merged[key] = value
        return merged

    def _generate_string_example(self, fmt: Optional[str], name: Optional[str], schema: Dict[str, Any]) -> str:
        """Generate string examples based on format and context"""

        # Format-based examples
        if fmt == 'uuid':
            return str(uuid.uuid4())
        elif fmt == 'date-time':
            return datetime.utcnow().isoformat() + 'Z'
        elif fmt == 'date':
            return datetime.utcnow().date().isoformat()
        elif fmt == 'email':
            return 'user@example.com'
        elif fmt == 'uri' or fmt == 'url':
            return 'https://example.com/resource'
        elif fmt == 'binary':
            return '(binary data)'
        elif fmt == 'int64':  # Timestamp as string
            return str(int(datetime.utcnow().timestamp() * 1000))

        # Context-based examples
        if name:
            name_lower = name.lower()
            if 'id' in name_lower:
                return str(uuid.uuid4())
            elif 'name' in name_lower:
                return 'Example Name'
            elif 'description' in name_lower:
                return 'Example description'
            elif 'path' in name_lower:
                return 'example/path/to/resource'
            elif 'url' in name_lower:
                return 'https://example.com'
            elif 'email' in name_lower:
                return 'user@example.com'
            elif 'token' in name_lower:
                return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'

        # Default string
        return 'example-string'

    def _generate_integer_example(self, fmt: Optional[str], name: Optional[str]) -> int:
        """Generate integer examples based on format and context"""
        if fmt == 'int64':
            if name and ('timestamp' in name.lower() or 'created' in name.lower() or 'updated' in name.lower()):
                return int(datetime.utcnow().timestamp() * 1000)
            return 1234567890

        # Context-based
        if name:
            name_lower = name.lower()
            if 'count' in name_lower or 'limit' in name_lower:
                return 10
            elif 'offset' in name_lower:
                return 0
            elif 'id' in name_lower:
                return 12345
            elif 'port' in name_lower:
                return 8080

        return 42

    def _generate_number_example(self, fmt: Optional[str], name: Optional[str]) -> float:
        """Generate number examples"""
        if fmt == 'double':
            if name and 'score' in name.lower():
                return 0.85
            return 3.14159

        if name and 'score' in name.lower():
            return 0.85

        return 2.5

    def _generate_array_example(self, schema: Dict[str, Any], name: Optional[str]) -> list:
        """Generate array examples"""
        items_schema = schema.get('items', {})
        min_items = schema.get('minItems', 1)

        # Generate between 1-2 items for examples
        count = max(min_items, 1)
        count = min(count, 2)  # Cap at 2 for readability

        return [
            self.generate_from_schema(items_schema, name)
            for _ in range(count)
        ]

    def _generate_object_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object examples from properties"""
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])

        example = {}

        # Generate required fields first
        for prop_name in required_fields:
            if prop_name in properties:
                example[prop_name] = self.generate_from_schema(properties[prop_name], prop_name)

        # Generate some optional fields (up to 3 additional)
        optional_count = 0
        for prop_name, prop_schema in properties.items():
            if prop_name not in required_fields and optional_count < 3:
                example[prop_name] = self.generate_from_schema(prop_schema, prop_name)
                optional_count += 1

        return example

    def extract_existing_example(self, operation: Dict[str, Any], location: str) -> Optional[Any]:
        """
        Extract existing examples from OpenAPI operation

        Args:
            operation: OpenAPI operation object (resolved)
            location: Where to look ('requestBody' or 'responses')

        Returns:
            Example value if found, None otherwise
        """
        if location == 'requestBody':
            request_body = operation.get('requestBody', {})
            content = request_body.get('content', {})

            for media_type, media_obj in content.items():
                # Check for examples (OpenAPI 3.1)
                examples = media_obj.get('examples', {})
                if examples:
                    # Get the first example
                    first_example = next(iter(examples.values()))
                    return first_example.get('value')

                # Check for example (OpenAPI 3.0)
                if 'example' in media_obj:
                    return media_obj['example']

                # Check schema example
                schema = media_obj.get('schema', {})
                if 'example' in schema:
                    return schema['example']

        elif location == 'responses':
            responses = operation.get('responses', {})

            # Look for successful response (200, 201, etc.)
            for status_code in ['200', '201', '202']:
                if status_code in responses:
                    response = responses[status_code]
                    content = response.get('content', {})

                    for media_type, media_obj in content.items():
                        examples = media_obj.get('examples', {})
                        if examples:
                            first_example = next(iter(examples.values()))
                            return first_example.get('value')

                        if 'example' in media_obj:
                            return media_obj['example']

                        schema = media_obj.get('schema', {})
                        if 'example' in schema:
                            return schema['example']

        return None
