#!/usr/bin/env python3

import sys
import os
sys.path.append('./src')

from env_vars import EnvVars
from log import Log

def main():
    Log.print_green("Starting environment test...")

    try:
        env = EnvVars()
        Log.print_green("Environment variables loaded successfully")

        Log.print_green(f"API Key present: {bool(env.openai_api_key)}")
        Log.print_green(f"Model: {env.openai_model}")
        Log.print_green(f"Input path: {env.yaml_input_path}")
        Log.print_green(f"Output path: {env.markdown_output_path}")
        Log.print_green(f"Template path: {env.template_path}")

        env.check_vars()

        # Check if paths exist
        import os
        from pathlib import Path

        input_dir = Path(env.yaml_input_path)
        template_file = Path(env.template_path)

        Log.print_green(f"Input directory exists: {input_dir.exists()}")
        Log.print_green(f"Template file exists: {template_file.exists()}")

        if input_dir.exists():
            yaml_files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml"))
            Log.print_green(f"YAML files found: {len(yaml_files)}")
            for f in yaml_files:
                Log.print_green(f"  - {f}")

        Log.print_green("Environment test completed successfully!")

    except Exception as e:
        Log.print_red(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()