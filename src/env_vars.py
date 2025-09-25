# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import os
from log import Log

class EnvVars:
    def __init__(self):
        # Core configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o')

        # Input/Output paths
        self.yaml_input_path = os.getenv('YAML_INPUT_PATH', './input')
        self.markdown_output_path = os.getenv('MARKDOWN_OUTPUT_PATH', './output')
        self.template_path = os.getenv('TEMPLATE_PATH', './templates/productAPI.template.md')

        # Process configuration
        self.max_iterations = int(os.getenv('MAX_ITERATIONS', '10'))
        self.completeness_threshold = int(os.getenv('COMPLETENESS_THRESHOLD', '90'))
        self.timeout_minutes = int(os.getenv('TIMEOUT_MINUTES', '30'))

        self.env_vars = {
            "openai_api_key": self.openai_api_key,
            "openai_model": self.openai_model,
            "yaml_input_path": self.yaml_input_path,
            "markdown_output_path": self.markdown_output_path,
            "template_path": self.template_path,
            "max_iterations": self.max_iterations,
            "completeness_threshold": self.completeness_threshold,
            "timeout_minutes": self.timeout_minutes,
        }

    def check_vars(self):
        missing_vars = [var for var, value in self.env_vars.items() if not value]
        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise ValueError(f"The following environment variables are missing or empty: {missing_vars_str}")
        else:
            Log.print_green("All required environment variables are set.")
