# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from unittest.mock import Mock, patch
from ai.doc_generator import DocGenerator


class TestDocGenerator(unittest.TestCase):

    def setUp(self):
        self.mock_client = Mock()
        self.mock_model = "gpt-4o"
        self.doc_generator = DocGenerator(self.mock_client, self.mock_model)

    def test_extract_template_placeholders(self):
        template = "# {{API_NAME}}\n{{#if CONDITION}}{{VALUE}}{{/if}}"
        placeholders = self.doc_generator._extract_template_placeholders(template)

        self.assertIn("API_NAME", placeholders)
        self.assertIn("#if CONDITION", placeholders)
        self.assertIn("VALUE", placeholders)

    def test_should_exit_true(self):
        validation_result = {
            "scores": {"overall": 95},
            "exit_criteria_met": True
        }
        result = self.doc_generator._should_exit(validation_result, 90)
        self.assertTrue(result)

    def test_should_exit_false_low_score(self):
        validation_result = {
            "scores": {"overall": 85},
            "exit_criteria_met": True
        }
        result = self.doc_generator._should_exit(validation_result, 90)
        self.assertFalse(result)

    def test_should_exit_false_criteria_not_met(self):
        validation_result = {
            "scores": {"overall": 95},
            "exit_criteria_met": False
        }
        result = self.doc_generator._should_exit(validation_result, 90)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()