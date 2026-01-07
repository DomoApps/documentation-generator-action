"""
Tests for YAMLEnhancer module

Tests gap detection logic for OpenAPI YAML files.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.yaml_enhancer import YAMLEnhancer, YAMLGapAnalysis, Enhancement
from src.openapi.openapi_parser import OpenAPIParser, EndpointData


@pytest.fixture
def yaml_enhancer():
    """Create a YAMLEnhancer instance for testing."""
    return YAMLEnhancer(min_description_length=10)


@pytest.fixture
def mock_parser_complete():
    """Create a mock parser with complete API documentation."""
    parser = Mock(spec=OpenAPIParser)
    parser.get_api_info.return_value = {
        'title': 'Complete API',
        'description': 'A fully documented API with all descriptions present',
        'version': '1.0.0'
    }
    parser.spec = {
        'tags': [
            {'name': 'Users', 'description': 'User management operations'},
            {'name': 'Products', 'description': 'Product catalog operations'}
        ],
        'components': {
            'schemas': {
                'User': {
                    'description': 'User account information',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Unique user identifier'},
                        'name': {'type': 'string', 'description': 'User full name'}
                    }
                }
            }
        }
    }

    endpoint = EndpointData()
    endpoint.path = '/users'
    endpoint.method = 'get'
    endpoint.operation_id = 'getUsers'
    endpoint.summary = 'Get all users'
    endpoint.description = 'Retrieve a list of all users in the system'
    endpoint.tags = ['Users']
    endpoint.path_parameters = []
    endpoint.query_parameters = [
        {'name': 'limit', 'description': 'Maximum number of users to return'}
    ]
    endpoint.header_parameters = []
    endpoint.request_body_schema = {}
    endpoint.request_body_description = ''
    endpoint.request_body_parameters = []
    endpoint.request_body_example = None
    endpoint.responses = {'200': {'description': 'Success'}}
    endpoint.success_response_example = None
    endpoint.success_status_code = '200'
    parser.parse_all_endpoints.return_value = [endpoint]

    return parser


@pytest.fixture
def mock_parser_incomplete():
    """Create a mock parser with incomplete API documentation."""
    parser = Mock(spec=OpenAPIParser)
    parser.get_api_info.return_value = {
        'title': '',  # Missing
        'description': 'API',  # Too short
        'version': ''  # Missing
    }
    parser.spec = {
        'tags': [
            {'name': 'Users', 'description': ''},  # Missing
            {'name': 'Products'}  # No description field
        ],
        'components': {
            'schemas': {
                'User': {
                    # No description
                    'properties': {
                        'id': {'type': 'integer'},  # No description
                        'name': {'type': 'string', 'description': 'Name'}  # Too short
                    }
                }
            }
        }
    }

    endpoint = EndpointData()
    endpoint.path = '/users'
    endpoint.method = 'get'
    endpoint.operation_id = 'getUsers'
    endpoint.summary = 'Get users'
    endpoint.description = ''  # Missing
    endpoint.tags = ['Users']
    endpoint.path_parameters = []
    endpoint.query_parameters = [
        {'name': 'limit'}  # No description
    ]
    endpoint.header_parameters = []
    endpoint.request_body_schema = {}
    endpoint.request_body_description = ''
    endpoint.request_body_parameters = []
    endpoint.request_body_example = None
    endpoint.responses = {'200': {'description': 'Success'}}
    endpoint.success_response_example = None
    endpoint.success_status_code = '200'
    parser.parse_all_endpoints.return_value = [endpoint]

    return parser


class TestYAMLGapAnalysis:
    """Test suite for YAMLGapAnalysis dataclass."""

    def test_has_gaps_no_gaps(self):
        """Test has_gaps returns False when no gaps exist."""
        gaps = YAMLGapAnalysis()
        assert gaps.has_gaps() is False

    def test_has_gaps_with_info_gaps(self):
        """Test has_gaps returns True when info gaps exist."""
        gaps = YAMLGapAnalysis(missing_info_title=True)
        assert gaps.has_gaps() is True

    def test_has_gaps_with_tag_gaps(self):
        """Test has_gaps returns True when tag gaps exist."""
        gaps = YAMLGapAnalysis(missing_tags=['Users'])
        assert gaps.has_gaps() is True

    def test_get_gap_count_none(self):
        """Test get_gap_count returns 0 when no gaps."""
        gaps = YAMLGapAnalysis()
        assert gaps.get_gap_count() == 0

    def test_get_gap_count_multiple(self):
        """Test get_gap_count with multiple gaps."""
        gaps = YAMLGapAnalysis(
            missing_info_title=True,
            missing_info_description=True,
            missing_tags=['Users', 'Products'],
            missing_endpoint_descriptions=['GET /users']
        )
        assert gaps.get_gap_count() == 5  # 1 + 1 + 2 + 1

    def test_get_summary_no_gaps(self):
        """Test get_summary with no gaps."""
        gaps = YAMLGapAnalysis()
        summary = gaps.get_summary()
        assert "No gaps found" in summary

    def test_get_summary_with_gaps(self):
        """Test get_summary with gaps."""
        gaps = YAMLGapAnalysis(
            missing_info_title=True,
            missing_tags=['Users']
        )
        summary = gaps.get_summary()
        assert "info.title" in summary
        assert "1 tag descriptions" in summary


class TestYAMLEnhancer:
    """Test suite for YAMLEnhancer class."""

    def test_analyze_yaml_gaps_complete(self, yaml_enhancer, mock_parser_complete):
        """Test analyzing a complete YAML with no gaps."""
        gaps = yaml_enhancer.analyze_yaml_gaps(
            '/path/to/complete.yaml',
            parser=mock_parser_complete
        )

        assert gaps.has_gaps() is False
        assert gaps.missing_info_title is False
        assert gaps.missing_info_description is False
        assert gaps.missing_info_version is False
        assert len(gaps.missing_tags) == 0
        assert len(gaps.missing_endpoint_descriptions) == 0
        assert len(gaps.missing_parameter_descriptions) == 0

    def test_analyze_yaml_gaps_incomplete(self, yaml_enhancer, mock_parser_incomplete):
        """Test analyzing an incomplete YAML with many gaps."""
        gaps = yaml_enhancer.analyze_yaml_gaps(
            '/path/to/incomplete.yaml',
            parser=mock_parser_incomplete
        )

        assert gaps.has_gaps() is True
        assert gaps.missing_info_title is True
        assert gaps.missing_info_description is True
        assert gaps.missing_info_version is True
        assert 'Users' in gaps.missing_tags
        assert 'Products' in gaps.missing_tags
        assert len(gaps.missing_endpoint_descriptions) == 1
        assert ('GET /users', 'limit') in gaps.missing_parameter_descriptions

    def test_is_inadequate_description_empty(self, yaml_enhancer):
        """Test inadequate description detection - empty string."""
        assert yaml_enhancer._is_inadequate_description('') is True
        assert yaml_enhancer._is_inadequate_description('   ') is True

    def test_is_inadequate_description_too_short(self, yaml_enhancer):
        """Test inadequate description detection - too short."""
        assert yaml_enhancer._is_inadequate_description('API') is True
        assert yaml_enhancer._is_inadequate_description('short') is True

    def test_is_inadequate_description_adequate(self, yaml_enhancer):
        """Test inadequate description detection - adequate length."""
        assert yaml_enhancer._is_inadequate_description('This is a proper API description') is False

    def test_analyze_info_gaps_missing_title(self, yaml_enhancer):
        """Test info gap detection - missing title."""
        parser = Mock(spec=OpenAPIParser)
        parser.get_api_info.return_value = {
            'title': '',
            'description': 'Valid description here',
            'version': '1.0.0'
        }

        gaps = YAMLGapAnalysis()
        yaml_enhancer._analyze_info_gaps(parser, gaps)

        assert gaps.missing_info_title is True
        assert gaps.missing_info_description is False
        assert gaps.missing_info_version is False

    def test_analyze_tag_gaps(self, yaml_enhancer):
        """Test tag gap detection."""
        parser = Mock(spec=OpenAPIParser)
        parser.spec = {
            'tags': [
                {'name': 'Users', 'description': ''},
                {'name': 'Products', 'description': 'Valid product description'},
                {'name': 'Orders'}  # No description field
            ]
        }

        gaps = YAMLGapAnalysis()
        yaml_enhancer._analyze_tag_gaps(parser, gaps)

        assert 'Users' in gaps.missing_tags
        assert 'Products' not in gaps.missing_tags
        assert 'Orders' in gaps.missing_tags

    def test_analyze_endpoint_gaps(self, yaml_enhancer):
        """Test endpoint gap detection."""
        parser = Mock(spec=OpenAPIParser)

        endpoint1 = EndpointData()
        endpoint1.path = '/users'
        endpoint1.method = 'get'
        endpoint1.operation_id = 'getUsers'
        endpoint1.summary = 'Get users'
        endpoint1.description = ''  # Missing
        endpoint1.tags = ['Users']
        endpoint1.path_parameters = []
        endpoint1.query_parameters = []
        endpoint1.header_parameters = []
        endpoint1.request_body_schema = {}
        endpoint1.request_body_description = ''
        endpoint1.request_body_parameters = []
        endpoint1.request_body_example = None
        endpoint1.responses = {}
        endpoint1.success_response_example = None
        endpoint1.success_status_code = '200'

        endpoint2 = EndpointData()
        endpoint2.path = '/products'
        endpoint2.method = 'post'
        endpoint2.operation_id = 'createProduct'
        endpoint2.summary = 'Create product'
        endpoint2.description = 'Create a new product in the catalog'
        endpoint2.tags = ['Products']
        endpoint2.path_parameters = []
        endpoint2.query_parameters = []
        endpoint2.header_parameters = []
        endpoint2.request_body_schema = {}
        endpoint2.request_body_description = ''
        endpoint2.request_body_parameters = []
        endpoint2.request_body_example = None
        endpoint2.responses = {}
        endpoint2.success_response_example = None
        endpoint2.success_status_code = '201'

        parser.parse_all_endpoints.return_value = [endpoint1, endpoint2]

        gaps = YAMLGapAnalysis()
        yaml_enhancer._analyze_endpoint_gaps(parser, gaps)

        assert 'GET /users' in gaps.missing_endpoint_descriptions
        assert 'POST /products' not in gaps.missing_endpoint_descriptions

    def test_check_parameter_descriptions(self, yaml_enhancer):
        """Test parameter description checking."""
        endpoint = EndpointData()
        endpoint.path = '/users/{id}'
        endpoint.method = 'get'
        endpoint.operation_id = 'getUser'
        endpoint.summary = 'Get user'
        endpoint.description = 'Get a specific user'
        endpoint.tags = ['Users']
        endpoint.path_parameters = [
            {'name': 'id', 'description': ''}  # Missing
        ]
        endpoint.query_parameters = [
            {'name': 'include', 'description': 'Fields to include in response'}
        ]
        endpoint.header_parameters = []
        endpoint.request_body_schema = {}
        endpoint.request_body_description = ''
        endpoint.request_body_parameters = []
        endpoint.request_body_example = None
        endpoint.responses = {}
        endpoint.success_response_example = None
        endpoint.success_status_code = '200'

        gaps = YAMLGapAnalysis()
        yaml_enhancer._check_parameter_descriptions(endpoint, gaps)

        assert ('GET /users/{id}', 'id') in gaps.missing_parameter_descriptions
        assert ('GET /users/{id}', 'include') not in gaps.missing_parameter_descriptions

    def test_analyze_schema_gaps(self, yaml_enhancer):
        """Test schema gap detection."""
        parser = Mock(spec=OpenAPIParser)
        parser.spec = {
            'components': {
                'schemas': {
                    'User': {
                        'description': '',  # Missing
                        'properties': {
                            'id': {'type': 'integer', 'description': ''},  # Missing
                            'name': {'type': 'string', 'description': 'User full name'}
                        }
                    },
                    'Product': {
                        'description': 'Product information',
                        'properties': {
                            'sku': {'type': 'string', 'description': 'Product SKU'}
                        }
                    }
                }
            }
        }

        gaps = YAMLGapAnalysis()
        yaml_enhancer._analyze_schema_gaps(parser, gaps)

        assert 'User' in gaps.missing_schema_descriptions
        assert 'Product' not in gaps.missing_schema_descriptions
        assert ('User', 'id') in gaps.missing_property_descriptions
        assert ('User', 'name') not in gaps.missing_property_descriptions

    def test_get_enhancement_priorities(self, yaml_enhancer):
        """Test priority ordering of enhancements."""
        gaps = YAMLGapAnalysis(
            missing_info_title=True,
            missing_tags=['Users'],
            missing_endpoint_descriptions=['GET /users'],
            missing_parameter_descriptions=[('GET /users', 'limit')],
            missing_schema_descriptions=['User']
        )

        priorities = yaml_enhancer.get_enhancement_priorities(gaps)

        # Should be in order: info, tags, endpoints, parameters, schemas
        assert priorities[0] == 'info'
        assert priorities[1] == 'tags'
        assert priorities[2] == 'endpoints'
        assert priorities[3] == 'parameters'
        assert priorities[4] == 'schemas'

    def test_get_enhancement_priorities_empty(self, yaml_enhancer):
        """Test priority list when no gaps exist."""
        gaps = YAMLGapAnalysis()
        priorities = yaml_enhancer.get_enhancement_priorities(gaps)
        assert len(priorities) == 0
