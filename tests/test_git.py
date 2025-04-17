import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from src.git import Git
class TestGit(unittest.TestCase):

    def test_prep_diff_for_ai(self):
        # Add the current directory to sys.path to locate the mock data file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mock_data_path = os.path.join(current_dir, 'mock_data', 'mockDiff.txt')

        # Load the mock diff input from the file
        with open(mock_data_path, 'r') as mock_diff_file:
            diff_input = mock_diff_file.read()
        
        # Corrected expected output with headers removed and lines prepended with numbers
        expected_output = """1 
          2 # Domo Developer Portal
          3 
          4-Domo provides a large suite of enterprise-grade tools that help organizations unlock business value from their data. The Domo platform includes a world-class data warehouse, robust data pipeline functionality, and an industry-leading visualization engine — all while ensuring data is well-governed and secure.
          5+Welcome to Domo! If you’re new to our platform, you’re in the right place to get started. Domo offers a powerful suite of enterprise-grade tools designed to help organizations unlock the full potential of their data.
          6 
          7-Domo's Developer Portal gives customers and partners access to all the tools and documentation needed to build, manage, and connect to Domo.
          8+Our Developer Portal provides all the resources and documentation needed to build, manage, and connect to Domo. Dive in to explore API references, feature guides, best practices, and step-by-step tutorials.
          9 
          10-## Developer Resources
          11+- **[Get your free developer trial instance](https://www.domo.com/start/developer)**
          12+- **[Manage your instance with Domo's CLI tool](https://domo-support.domo.com/s/article/360043437733?language=en_US)**
          """

        # Call the method under test
        result = Git.prep_diff_for_ai(diff_input)
        # can we log the result during the test
        print("Result:", result)
        # Split the outputs into lines for comparison
        expected_lines = expected_output.splitlines()
        result_lines = result.splitlines()

        # Compare line by line
        for expected_line, result_line in zip(expected_lines, result_lines):
            self.assertEqual(expected_line, result_line)

        # Ensure the lengths match
        self.assertEqual(len(expected_lines), 12)

if __name__ == '__main__':
    unittest.main()