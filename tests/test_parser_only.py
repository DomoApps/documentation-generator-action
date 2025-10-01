#!/usr/bin/env python3
# Test just the parser without AI

import pytest
import json
from src.openapi.openapi_parser import OpenAPIParser
from src.log import Log


def test_openapi_parser_can_parse_spec():
    """Test that OpenAPI parser can load and parse a spec file"""
    yaml_path = './samples/ai.yaml'

    parser = OpenAPIParser(yaml_path)

    # Verify API info is extracted
    api_info = parser.get_api_info()
    assert api_info is not None
    assert 'title' in api_info
    assert 'version' in api_info
    assert 'description' in api_info

    Log.print_green(f"✓ API Info parsed: {api_info['title']} v{api_info['version']}")


def test_openapi_parser_extracts_endpoints():
    """Test that parser extracts all endpoints from spec"""
    yaml_path = './samples/ai.yaml'

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Verify endpoints were extracted
    assert endpoints is not None
    assert len(endpoints) > 0

    Log.print_green(f"✓ Parsed {len(endpoints)} endpoints")


def test_openapi_parser_endpoint_structure():
    """Test that parsed endpoints have the expected structure"""
    yaml_path = './samples/ai.yaml'

    parser = OpenAPIParser(yaml_path)
    endpoints = parser.parse_all_endpoints()

    # Check first endpoint has expected fields
    ep = endpoints[0]
    assert hasattr(ep, 'path')
    assert hasattr(ep, 'method')
    assert hasattr(ep, 'summary')
    assert hasattr(ep, 'description')
    assert hasattr(ep, 'path_parameters')
    assert hasattr(ep, 'query_parameters')
    assert hasattr(ep, 'request_body_parameters')

    # Verify data types
    assert isinstance(ep.path, str)
    assert isinstance(ep.method, str)
    assert isinstance(ep.path_parameters, list)
    assert isinstance(ep.query_parameters, list)
    assert isinstance(ep.request_body_parameters, list)

    Log.print_green(f"✓ Endpoint structure valid for {ep.method.upper()} {ep.path}")


def test_openapi_parser_generates_examples():
    """Test that parser generates request/response examples"""
    yaml_path = './samples/ai.yaml'

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

    Log.print_green(f"✓ Examples generated: {len(endpoints_with_request_examples)} request, {len(endpoints_with_response_examples)} response")
