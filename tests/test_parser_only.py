#!/usr/bin/env python3
# Test just the parser without AI

import pytest
import json
from pathlib import Path
from src.openapi.openapi_parser import OpenAPIParser
from src.log import Log


@pytest.fixture
def yaml_path():
    """Get path to sample YAML file."""
    return './samples/Documents.yaml'


def test_openapi_parser_can_parse_spec(yaml_path):
    """Test that OpenAPI parser can load and parse a spec file"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)

    # Verify API info is extracted
    api_info = parser.get_api_info()
    assert api_info is not None
    assert 'title' in api_info
    assert 'version' in api_info
    assert 'description' in api_info

    Log.print_green(f"API Info parsed: {api_info['title']} v{api_info['version']}")


def test_openapi_parser_extracts_endpoints(yaml_path):
    """Test that parser extracts all endpoints from spec"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Verify endpoints were extracted
    assert endpoints is not None
    assert len(endpoints) > 0

    Log.print_green(f"Parsed {len(endpoints)} endpoints")


def test_openapi_parser_endpoint_structure(yaml_path):
    """Test that parsed endpoints have the expected structure"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Check first endpoint has expected fields
    ep = endpoints[0]
    assert hasattr(ep, 'path')
    assert hasattr(ep, 'method')
    assert hasattr(ep, 'summary')
    assert hasattr(ep, 'description')
    assert hasattr(ep, 'tags')
    assert hasattr(ep, 'path_parameters')
    assert hasattr(ep, 'query_parameters')
    assert hasattr(ep, 'request_body_parameters')

    # Verify data types
    assert isinstance(ep.path, str)
    assert isinstance(ep.method, str)
    assert isinstance(ep.tags, list)
    assert isinstance(ep.path_parameters, list)
    assert isinstance(ep.query_parameters, list)
    assert isinstance(ep.request_body_parameters, list)

    Log.print_green(f"Endpoint structure valid for {ep.method.upper()} {ep.path}")


def test_openapi_parser_extracts_tags(yaml_path):
    """Test that parser extracts tags from endpoints"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Check that at least some endpoints have tags
    endpoints_with_tags = [ep for ep in endpoints if ep.tags]
    assert len(endpoints_with_tags) > 0, "Expected some endpoints to have tags"

    Log.print_green(f"{len(endpoints_with_tags)} endpoints have tags")


def test_openapi_parser_generates_examples(yaml_path):
    """Test that parser generates request/response examples"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Check that at least some endpoints have examples
    endpoints_with_request_examples = [ep for ep in endpoints if ep.request_body_example]
    endpoints_with_response_examples = [ep for ep in endpoints if ep.success_response_example]

    # Not all endpoints will have request bodies, but endpoints with request bodies should have examples
    endpoints_with_request_body = [ep for ep in endpoints if ep.request_body_parameters]
    if endpoints_with_request_body:
        assert len(endpoints_with_request_examples) > 0, "Expected some endpoints to have request examples"

    # Most endpoints should have success response examples
    assert len(endpoints_with_response_examples) > 0, "Expected some endpoints to have response examples"

    Log.print_green(f"Examples generated: {len(endpoints_with_request_examples)} request, {len(endpoints_with_response_examples)} response")


def test_openapi_parser_api_info(yaml_path):
    """Test that API-level info is correctly extracted"""
    if not Path(yaml_path).exists():
        pytest.skip("Sample YAML file not found")

    parser = OpenAPIParser(yaml_path)
    api_info = parser.get_api_info()

    # Verify expected fields
    assert 'title' in api_info
    assert 'description' in api_info
    assert 'version' in api_info
    assert 'tags' in api_info

    # For Documents.yaml, we know the title
    assert api_info['title'] == 'Documents'

    Log.print_green(f"API info: {api_info['title']} - {len(api_info.get('tags', []))} tags defined")
