# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import os
from pathlib import Path
from log import Log


class EnvVars:
    """
    Environment variable configuration for TOC Generator.

    Loads and validates environment variables needed for generating
    Mintlify TOC entries from OpenAPI YAML files.
    """

    def __init__(self):
        # Load .env file if it exists (for local development)
        self._load_env_file()

        # Required: Path to docs.json to update
        self.docs_json_path = os.getenv("DOCS_JSON_PATH", "")

        # Input/Output paths
        self.yaml_input_path = os.getenv("YAML_INPUT_PATH", "./yaml")

        # OpenAPI base path for page references in docs.json
        # Example: "openapi/product" results in pages like
        # "openapi/product/api.yaml GET /users"
        self.openapi_base_path = os.getenv("OPENAPI_BASE_PATH", "openapi/product")

        # Optional: Copy YAML files to this destination after processing
        self.yaml_copy_destination = os.getenv("YAML_COPY_DESTINATION", "")

        # Changed files processing
        self.process_changed_only = (
            os.getenv("PROCESS_CHANGED_ONLY", "false").lower() == "true"
        )
        self.changed_files = (
            os.getenv("CHANGED_FILES", "").strip().split("\n")
            if os.getenv("CHANGED_FILES")
            else []
        )
        # Filter out empty strings from changed_files
        self.changed_files = [f for f in self.changed_files if f.strip()]

        # Required environment variables for validation
        self.env_vars = {
            "docs_json_path": self.docs_json_path,
            "yaml_input_path": self.yaml_input_path,
        }

    def check_vars(self):
        """
        Validate that all required environment variables are set.

        Raises:
            ValueError: If required environment variables are missing
        """
        missing_vars = [var for var, value in self.env_vars.items() if not value]
        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise ValueError(
                f"The following environment variables are missing or empty: {missing_vars_str}"
            )
        else:
            Log.print_green("All required environment variables are set.")

    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        if key not in os.environ:
                            os.environ[key] = value

    def get_yaml_files_to_process(self) -> list:
        """
        Get the list of YAML files to process.

        Returns:
            List of YAML file paths to process
        """
        if self.process_changed_only and self.changed_files:
            Log.print_green(f"Processing {len(self.changed_files)} changed files")
            return self.changed_files
        else:
            # Find all YAML files in input directory
            yaml_dir = Path(self.yaml_input_path)
            if not yaml_dir.exists():
                Log.print_red(f"Input directory not found: {self.yaml_input_path}")
                return []

            yaml_files = list(yaml_dir.glob("*.yaml")) + list(yaml_dir.glob("*.yml"))
            file_paths = [str(f) for f in yaml_files]
            Log.print_green(f"Found {len(file_paths)} YAML files in {self.yaml_input_path}")
            return file_paths
