"""
YAML Enhancer Main Entry Point

Processes OpenAPI YAML files to add AI-generated descriptions for missing fields.
Refactored from doc_generator_main.py to focus on YAML enhancement.
"""

import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

from ai.yaml_enhancement_generator import YAMLEnhancementGenerator
from yaml_enhancer import YAMLEnhancer
from yaml_preserver import YAMLPreserver
from openapi.openapi_parser import OpenAPIParser
from env_vars import EnvVars
from log import Log


def main():
    """Main function for YAML enhancement"""
    start_time = time.time()

    # Load environment variables
    env_vars = EnvVars()
    env_vars.check_vars()

    # Initialize components
    client = OpenAI(api_key=env_vars.openai_api_key)
    enhancement_generator = YAMLEnhancementGenerator(client, env_vars.openai_model)
    yaml_enhancer = YAMLEnhancer(min_description_length=10)
    yaml_preserver = YAMLPreserver()

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

    # Ensure output directory exists (if different from input)
    if env_vars.yaml_output_path and env_vars.yaml_output_path != env_vars.yaml_input_path:
        os.makedirs(env_vars.yaml_output_path, exist_ok=True)

    # Track enhancements for PR title generation
    enhancements_summary = {}
    processed_files = []

    # Function to process a single file (for parallel execution)
    def process_single_file(yaml_file):
        """Process a single YAML file and return results"""
        result = {
            'file': yaml_file,
            'success': False,
            'enhancements': 0,
            'error': None
        }

        Log.print_green(f"Processing: {yaml_file}")

        # Check timeout
        if time.time() - start_time > env_vars.timeout_minutes * 60:
            Log.print_red("Timeout reached for this file")
            result['error'] = 'timeout'
            return result

        try:
            # Parse OpenAPI spec
            parser = OpenAPIParser(yaml_file)
            api_info = parser.get_api_info()
            endpoints = parser.parse_all_endpoints()

            Log.print_blue(f"Found {len(endpoints)} endpoints in {os.path.basename(yaml_file)}")

            # Analyze gaps
            gaps = yaml_enhancer.analyze_yaml_gaps(yaml_file, parser)

            if not gaps.has_gaps():
                Log.print_green(f"No gaps found in {os.path.basename(yaml_file)} - YAML is complete!")
                result['success'] = True
                result['enhancements'] = 0
                return result

            Log.print_yellow(f"Found {gaps.get_gap_count()} gaps: {gaps.get_summary()}")

            # Generate enhancements with validation loop
            enhancements = enhancement_generator.process_yaml_enhancement(
                yaml_file,
                gaps,
                api_info,
                endpoints,
                max_iterations=env_vars.max_iterations,
                quality_threshold=getattr(env_vars, 'quality_threshold', 85)
            )

            if not enhancements:
                Log.print_yellow(f"No enhancements generated for {os.path.basename(yaml_file)}")
                result['success'] = True
                result['enhancements'] = 0
                return result

            # Apply enhancements preserving structure
            output_path = get_output_path(yaml_file, env_vars.yaml_output_path, env_vars.yaml_input_path)

            # Convert enhancement paths for YAMLPreserver
            # (Some paths from generator may need conversion)
            converted_enhancements = convert_enhancement_paths(enhancements, parser)

            success = yaml_preserver.apply_enhancements(
                yaml_file,
                converted_enhancements,
                output_path
            )

            if success:
                Log.print_green(
                    f"Successfully enhanced {os.path.basename(yaml_file)} "
                    f"with {len(enhancements)} improvements"
                )
                result['success'] = True
                result['enhancements'] = len(enhancements)

                # Validate the enhanced YAML is still valid
                if not yaml_preserver.validate_yaml_structure(output_path):
                    Log.print_red(f"Warning: Enhanced YAML may have validation issues: {output_path}")
            else:
                Log.print_red(f"Failed to apply enhancements to {yaml_file}")
                result['error'] = 'apply_failed'

        except Exception as e:
            Log.print_red(f"Error processing {yaml_file}: {e}")
            result['error'] = str(e)

        return result

    # Process files in parallel
    max_workers = min(len(yaml_files), 5)  # Limit to 5 parallel files
    Log.print_green(f"Processing {len(yaml_files)} files with {max_workers} workers")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_single_file, yaml_file): yaml_file
            for yaml_file in yaml_files
        }

        for future in as_completed(future_to_file):
            yaml_file = future_to_file[future]
            try:
                result = future.result()
                if result['success']:
                    processed_files.append(result['file'])
                    if result['enhancements'] > 0:
                        enhancements_summary[result['file']] = result['enhancements']
            except Exception as e:
                Log.print_red(f"Exception processing {yaml_file}: {e}")

    # Generate PR title if files were enhanced
    if processed_files and enhancements_summary:
        pr_title = enhancement_generator.generate_pr_title(processed_files, enhancements_summary)
        Log.print_green(f"Generated PR title: {pr_title}")

        # Save PR title to environment file for GitHub Actions
        if os.getenv('GITHUB_ENV'):
            with open(os.getenv('GITHUB_ENV'), 'a') as f:
                f.write(f"GENERATED_PR_TITLE={pr_title}\n")
            Log.print_green("PR title saved to GITHUB_ENV")

    # Print summary
    total_enhancements = sum(enhancements_summary.values())
    Log.print_green(f"\n=== Enhancement Summary ===")
    Log.print_green(f"Files processed: {len(yaml_files)}")
    Log.print_green(f"Files enhanced: {len(enhancements_summary)}")
    Log.print_green(f"Total enhancements: {total_enhancements}")

    elapsed_time = time.time() - start_time
    Log.print_green(f"Total time: {elapsed_time:.2f} seconds")


def find_yaml_files(directory: str) -> list:
    """Recursively find all YAML files in directory"""
    yaml_files = []
    search_path = Path(directory)

    if not search_path.exists():
        Log.print_red(f"Directory not found: {directory}")
        return yaml_files

    for path in search_path.rglob('*.yaml'):
        yaml_files.append(str(path))
    for path in search_path.rglob('*.yml'):
        yaml_files.append(str(path))

    return sorted(yaml_files)


def get_output_path(yaml_file: str, output_path: str, input_path: str) -> str:
    """
    Determine output path for enhanced YAML file.

    If output_path is not set or equals input_path, modify in-place.
    Otherwise, maintain directory structure in output_path.

    Args:
        yaml_file: Path to original YAML file
        output_path: Configured output directory
        input_path: Configured input directory

    Returns:
        Path where enhanced YAML should be saved
    """
    # In-place modification if output equals input or output not set
    if not output_path or output_path == input_path:
        return yaml_file

    # Maintain directory structure in output directory
    try:
        relative_path = Path(yaml_file).relative_to(input_path)
        final_path = Path(output_path) / relative_path
        final_path.parent.mkdir(parents=True, exist_ok=True)
        return str(final_path)
    except ValueError:
        # File is not relative to input_path, just use same filename in output
        filename = os.path.basename(yaml_file)
        return os.path.join(output_path, filename)


def convert_enhancement_paths(
    enhancements: dict,
    parser: OpenAPIParser
) -> dict:
    """
    Convert enhancement paths from generator format to YAMLPreserver format.

    Some paths from the generator may use simplified notation (e.g., 'tag.TagName.description')
    that needs to be converted to actual YAML paths (e.g., 'tags.0.description').

    Args:
        enhancements: Dictionary of enhancements from generator
        parser: OpenAPIParser instance for looking up indices

    Returns:
        Dictionary with converted paths
    """
    converted = {}
    spec = parser.spec

    for path, value in enhancements.items():
        # Handle tag paths: 'tag.TagName.description' → 'tags.INDEX.description'
        if path.startswith('tag.'):
            parts = path.split('.')
            if len(parts) >= 3:
                tag_name = parts[1]
                field = parts[2]

                # Find tag index
                tags = spec.get('tags', [])
                for i, tag in enumerate(tags):
                    if tag.get('name') == tag_name:
                        converted[f'tags.{i}.{field}'] = value
                        break
                continue

        # Other paths can be used as-is
        converted[path] = value

    return converted


if __name__ == "__main__":
    main()
