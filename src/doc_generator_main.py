# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import os
import time
from pathlib import Path
from openai import OpenAI
from ai.doc_generator import DocGenerator
from env_vars import EnvVars
from log import Log

def main():
    """Main function for YAML to Markdown documentation generation"""
    start_time = time.time()

    # Load environment variables
    env_vars = EnvVars()
    env_vars.check_vars()

    # Initialize AI client
    client = OpenAI(api_key=env_vars.openai_api_key)
    doc_generator = DocGenerator(client, env_vars.openai_model)

    # Load template
    template_content = load_template(env_vars.template_path)
    if not template_content:
        Log.print_red("Failed to load template file")
        return

    # Determine which YAML files to process
    if env_vars.process_changed_only and env_vars.changed_files:
        Log.print_green("Processing only changed files:")
        yaml_files = [f for f in env_vars.changed_files if f.endswith(('.yaml', '.yml'))]
        for file in yaml_files:
            Log.print_green(f"  - {file}")
    else:
        # Process all YAML files in input directory
        yaml_files = find_yaml_files(env_vars.yaml_input_path)

    if not yaml_files:
        Log.print_red("No YAML files found to process")
        return

    # Ensure output directory exists
    os.makedirs(env_vars.markdown_output_path, exist_ok=True)

    # Collect YAML summaries for PR title generation
    yaml_summaries = {}
    processed_files = []

    # Process each YAML file
    for yaml_file in yaml_files:
        Log.print_green(f"Processing: {yaml_file}")

        # Check timeout
        if time.time() - start_time > env_vars.timeout_minutes * 60:
            Log.print_red("Timeout reached, stopping process")
            break

        # Load YAML content
        yaml_content = load_yaml_file(yaml_file)
        if not yaml_content:
            Log.print_red(f"Failed to load YAML file: {yaml_file}")
            continue

        # Extract basic info for PR title generation
        try:
            import yaml
            yaml_data = yaml.safe_load(yaml_content)
            yaml_summaries[yaml_file] = yaml_data
        except Exception as e:
            Log.print_red(f"Failed to parse YAML for summary: {e}")
            yaml_summaries[yaml_file] = {"info": {"title": "API"}}

        # Generate documentation
        markdown_content = doc_generator.process_yaml_to_markdown(
            yaml_content=yaml_content,
            template_content=template_content,
            max_iterations=env_vars.max_iterations,
            completeness_threshold=env_vars.completeness_threshold
        )

        # Save output
        output_file = get_output_filename(yaml_file, env_vars.markdown_output_path)
        save_markdown_file(output_file, markdown_content)

        Log.print_green(f"Generated documentation: {output_file}")
        processed_files.append(yaml_file)

    # Generate AI-powered PR title if files were processed
    if processed_files and env_vars.process_changed_only:
        Log.print_green("Generating smart PR title...")
        pr_title = doc_generator.generate_pr_title(processed_files, yaml_summaries)

        # Save PR title to environment variable for GitHub Actions
        with open(os.environ.get('GITHUB_ENV', '/dev/null'), 'a') as f:
            f.write(f"GENERATED_PR_TITLE={pr_title}\n")
        Log.print_green(f"Generated PR title: {pr_title}")

    Log.print_green("Documentation generation complete")

def load_template(template_path: str) -> str:
    """Load markdown template file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        Log.print_red(f"Template file not found: {template_path}")
        return ""
    except Exception as e:
        Log.print_red(f"Error loading template: {e}")
        return ""

def find_yaml_files(input_path: str) -> list:
    """Find all YAML files in input directory"""
    yaml_extensions = ['.yaml', '.yml']
    yaml_files = []

    input_dir = Path(input_path)
    if not input_dir.exists():
        Log.print_red(f"Input directory does not exist: {input_path}")
        return []

    for ext in yaml_extensions:
        yaml_files.extend(input_dir.glob(f"*{ext}"))
        yaml_files.extend(input_dir.glob(f"**/*{ext}"))

    return [str(f) for f in yaml_files]

def load_yaml_file(yaml_file: str) -> str:
    """Load YAML file content as string"""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        Log.print_red(f"Error loading YAML file {yaml_file}: {e}")
        return ""

def get_output_filename(yaml_file: str, output_path: str) -> str:
    """Generate output markdown filename"""
    yaml_path = Path(yaml_file)
    output_name = yaml_path.stem + ".md"
    return os.path.join(output_path, output_name)

def save_markdown_file(output_file: str, content: str):
    """Save generated markdown to file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        Log.print_red(f"Error saving markdown file {output_file}: {e}")

if __name__ == "__main__":
    main()