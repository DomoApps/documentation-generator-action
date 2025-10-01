#!/usr/bin/env python3
# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

"""
Test the deterministic OpenAPI parsing approach with full AI generation
"""

import os
import pytest
from openai import OpenAI
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
def test_deterministic_approach_generates_full_documentation(openai_client, test_files):
    """Test that deterministic approach can generate complete documentation with AI"""
    yaml_path, template_content = test_files
    output_path = './output/ai_deterministic.md'

    model = os.getenv('OPENAI_MODEL', 'gpt-4o')
    Log.print_green(f"Using model: {model}")

    # Create doc generator
    doc_gen = DocGenerator(openai_client, model)

    # Process using deterministic approach
    markdown = doc_gen.process_openapi_to_markdown_deterministic(
        yaml_path=yaml_path,
        template_content=template_content
    )

    # Verify output
    assert markdown is not None
    assert len(markdown) > 0
    assert isinstance(markdown, str)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write output
    with open(output_path, 'w') as f:
        f.write(markdown)

    Log.print_green(f"✓ Documentation generated: {len(markdown)} characters")
    Log.print_green(f"✓ Output written to: {output_path}")
