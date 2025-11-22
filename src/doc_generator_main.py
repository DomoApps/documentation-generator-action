# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    # Function to process a single file (for parallel execution)
    def process_single_file(yaml_file):
        """Process a single YAML file and return results"""
        import yaml as yaml_lib

        result = {
            'file': yaml_file,
            'success': False,
            'yaml_data': None,
            'error': None
        }

        Log.print_green(f"Processing: {yaml_file}")

        # Check timeout
        if time.time() - start_time > env_vars.timeout_minutes * 60:
            Log.print_red("Timeout reached for this file")
            result['error'] = 'timeout'
            return result

        # Load YAML content
        yaml_content = load_yaml_file(yaml_file)
        if not yaml_content:
            Log.print_red(f"Failed to load YAML file: {yaml_file}")
            result['error'] = 'load_failed'
            return result

        # Extract basic info for PR title generation
        try:
            yaml_data = yaml_lib.safe_load(yaml_content)
            result['yaml_data'] = yaml_data
        except Exception as e:
            Log.print_red(f"Failed to parse YAML for summary: {e}")
            result['yaml_data'] = {"info": {"title": "API"}}

        # Generate documentation using HYBRID approach (deterministic + validation)
        try:
            markdown_content = doc_generator.process_openapi_to_markdown_deterministic(
                yaml_path=yaml_file,
                template_content=template_content,
                max_iterations=env_vars.max_iterations,
                completeness_threshold=env_vars.completeness_threshold
            )
        except Exception as e:
            Log.print_red(f"Hybrid approach failed: {e}")
            Log.print_red("Falling back to legacy iterative approach...")
            # Fallback to old method if deterministic fails
            try:
                markdown_content = doc_generator.process_yaml_to_markdown(
                    yaml_content=yaml_content,
                    template_content=template_content,
                    max_iterations=env_vars.max_iterations,
                    completeness_threshold=env_vars.completeness_threshold
                )
            except Exception as fallback_error:
                Log.print_red(f"Legacy approach also failed: {fallback_error}")
                result['error'] = str(fallback_error)
                return result

        # Save output
        output_file = get_output_filename(yaml_file, env_vars.markdown_output_path)
        save_markdown_file(output_file, markdown_content)

        Log.print_green(f"Generated documentation: {output_file}")
        result['success'] = True
        return result

    # Process files in parallel
    max_workers = min(len(yaml_files), 5)  # Limit to 5 parallel workers to avoid rate limits
    Log.print_green(f"Processing {len(yaml_files)} files with {max_workers} parallel workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_single_file, yf): yf for yf in yaml_files}

        # Collect results as they complete
        for future in as_completed(future_to_file):
            result = future.result()
            if result['success']:
                processed_files.append(result['file'])
                if result['yaml_data']:
                    yaml_summaries[result['file']] = result['yaml_data']

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
        # Use **/* for recursive search (includes current dir)
        yaml_files.extend(input_dir.glob(f"**/*{ext}"))

    # Remove duplicates by converting to set and back
    yaml_files = list(set([str(f) for f in yaml_files]))

    Log.print_green(f"Found {len(yaml_files)} YAML file(s): {yaml_files}")
    return yaml_files

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