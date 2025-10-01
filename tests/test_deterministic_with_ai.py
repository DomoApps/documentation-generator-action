#!/usr/bin/env python3
# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

"""
Test deterministic approach with AI (limited to 3 endpoints for faster testing)
"""

import os
import pytest
from openai import OpenAI
from src.openapi.openapi_parser import OpenAPIParser
from src.ai.doc_generator import DocGenerator
from src.log import Log


@pytest.fixture
def openai_client():
    """Create OpenAI client from environment"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=api_key)


@pytest.fixture
def test_files():
    """Verify test files exist"""
    yaml_path = './samples/ai.yaml'
    template_path = './templates/product-api.template.md'

    if not os.path.exists(yaml_path):
        pytest.skip(f"Test YAML file not found: {yaml_path}")

    if not os.path.exists(template_path):
        pytest.skip(f"Template file not found: {template_path}")

    with open(template_path, 'r') as f:
        template_content = f.read()

    return yaml_path, template_content


@pytest.mark.integration
def test_deterministic_approach_with_limited_endpoints(openai_client, test_files):
    """Test deterministic approach with AI on first 3 endpoints (faster testing)"""
    yaml_path, template_content = test_files
    output_path = './output/ai_deterministic_limited.md'

    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Use mini for faster/cheaper testing
    Log.print_green(f"Using model: {model}")

    # Create doc generator
    doc_gen = DocGenerator(openai_client, model)

    # Parse spec
    Log.print_green("Parsing OpenAPI spec deterministically...")
    parser = OpenAPIParser(yaml_path)
    api_info = parser.get_api_info()
    all_endpoints = parser.parse_all_endpoints()

    Log.print_green(f"Found {len(all_endpoints)} total endpoints")
    Log.print_green("Processing first 3 endpoints for testing...")

    endpoints = all_endpoints[:3]  # Test with just 3 endpoints

    # Build documentation for each endpoint
    endpoint_docs = []
    for i, endpoint in enumerate(endpoints, 1):
        Log.print_green(f"Processing endpoint {i}/{len(endpoints)}: {endpoint.method.upper()} {endpoint.path}")

        # Generate documentation for this endpoint
        doc = doc_gen._generate_endpoint_documentation(endpoint, template_content, parser)
        endpoint_docs.append(doc)

        # Verify doc was generated
        assert doc is not None
        assert len(doc) > 0
        assert isinstance(doc, str)

        Log.print_green(f"✓ Generated {len(doc)} characters")

    # Combine all endpoint documentation
    full_doc = doc_gen._combine_endpoint_docs(api_info, endpoint_docs)

    # Verify combined doc
    assert full_doc is not None
    assert len(full_doc) > 0
    assert len(endpoint_docs) == 3

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write output
    with open(output_path, 'w') as f:
        f.write(full_doc)

    Log.print_green(f"✓ Documentation generated: {len(full_doc)} characters")
    Log.print_green(f"✓ Endpoints documented: {len(endpoints)}")
    Log.print_green(f"✓ Output written to: {output_path}")
