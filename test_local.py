#!/usr/bin/env python3
"""
Local testing script for YAML to Markdown Documentation Generator
Author: Jonathan Tiritilli
License: Apache License 2.0

This script allows you to test the action locally without GitHub Actions environment.
"""

import os
import sys
import argparse
from pathlib import Path

def load_env_file(env_file='.env'):
    """Load environment variables from .env file if it exists"""
    env_path = Path(env_file)
    if env_path.exists():
        print(f"📄 Loading environment from {env_file}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Don't override existing environment variables
                    if key not in os.environ:
                        os.environ[key] = value
        return True
    return False

def setup_environment(openai_key: str = None, use_mock: bool = False):
    """Set up environment variables for local testing"""

    # Core configuration
    if use_mock:
        os.environ['OPENAI_API_KEY'] = 'mock-key-for-testing'
        print("⚠️  Using mock API key - AI requests will fail but structure will be tested")
    elif openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
        print("✅ Using provided OpenAI API key")
    else:
        existing_key = os.getenv('OPENAI_API_KEY')
        if not existing_key:
            print("❌ No OpenAI API key provided. Use --openai-key or set OPENAI_API_KEY environment variable")
            return False
        print("✅ Using existing OpenAI API key from environment")

    # Default paths - using samples for testing
    os.environ['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'gpt-4o')
    os.environ['YAML_INPUT_PATH'] = os.getenv('YAML_INPUT_PATH', './samples')
    os.environ['MARKDOWN_OUTPUT_PATH'] = os.getenv('MARKDOWN_OUTPUT_PATH', './test-output')
    os.environ['TEMPLATE_PATH'] = os.getenv('TEMPLATE_PATH', './samples/productAPI.template.md')

    # Process configuration
    os.environ['MAX_ITERATIONS'] = os.getenv('MAX_ITERATIONS', '3')  # Reduced for testing
    os.environ['COMPLETENESS_THRESHOLD'] = os.getenv('COMPLETENESS_THRESHOLD', '80')  # Lower threshold for testing
    os.environ['TIMEOUT_MINUTES'] = os.getenv('TIMEOUT_MINUTES', '10')  # Shorter timeout for testing

    return True

def validate_setup():
    """Validate that required files and directories exist"""
    yaml_input = os.getenv('YAML_INPUT_PATH')
    template_path = os.getenv('TEMPLATE_PATH')

    print("\n🔍 Validating setup...")

    # Check input directory
    if not os.path.exists(yaml_input):
        print(f"❌ Input directory not found: {yaml_input}")
        return False

    # Check for YAML files
    yaml_files = list(Path(yaml_input).glob('*.yaml')) + list(Path(yaml_input).glob('*.yml'))
    if not yaml_files:
        print(f"❌ No YAML files found in: {yaml_input}")
        return False

    print(f"✅ Found {len(yaml_files)} YAML file(s):")
    for f in yaml_files:
        print(f"   - {f.name}")

    # Check template
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False

    print(f"✅ Template file found: {template_path}")

    # Create output directory
    output_path = os.getenv('MARKDOWN_OUTPUT_PATH')
    os.makedirs(output_path, exist_ok=True)
    print(f"✅ Output directory ready: {output_path}")

    return True

def print_configuration():
    """Print current configuration"""
    print("\n⚙️  Current Configuration:")
    print(f"   OpenAI Model: {os.getenv('OPENAI_MODEL')}")
    print(f"   Input Path: {os.getenv('YAML_INPUT_PATH')}")
    print(f"   Output Path: {os.getenv('MARKDOWN_OUTPUT_PATH')}")
    print(f"   Template: {os.getenv('TEMPLATE_PATH')}")
    print(f"   Max Iterations: {os.getenv('MAX_ITERATIONS')}")
    print(f"   Quality Threshold: {os.getenv('COMPLETENESS_THRESHOLD')}%")
    print(f"   Timeout: {os.getenv('TIMEOUT_MINUTES')} minutes")

def run_generator():
    """Import and run the main generator"""
    try:
        # Add src to Python path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        print("\n🚀 Starting documentation generation...")

        # Import and run main function
        from doc_generator_main import main
        main()

        print("\n✅ Documentation generation completed successfully!")

        # Show generated files
        output_path = os.getenv('MARKDOWN_OUTPUT_PATH')
        md_files = list(Path(output_path).glob('*.md'))
        if md_files:
            print(f"\n📄 Generated {len(md_files)} file(s):")
            for f in md_files:
                print(f"   - {f}")

        return True

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test YAML to Markdown Documentation Generator locally')
    parser.add_argument('--openai-key', help='OpenAI API key for testing')
    parser.add_argument('--mock', action='store_true', help='Use mock API key (will fail AI requests but test structure)')
    parser.add_argument('--input-path', help='Path to YAML input directory', default='./samples')
    parser.add_argument('--output-path', help='Path to output directory', default='./test-output')
    parser.add_argument('--template', help='Path to template file', default='./samples/productAPI.template.md')
    parser.add_argument('--model', help='OpenAI model to use', default='gpt-4o')
    parser.add_argument('--iterations', type=int, help='Max iterations', default=3)
    parser.add_argument('--threshold', type=int, help='Quality threshold', default=80)
    parser.add_argument('--timeout', type=int, help='Timeout in minutes', default=10)

    args = parser.parse_args()

    # Override defaults with command line args
    if args.input_path != './samples':
        os.environ['YAML_INPUT_PATH'] = args.input_path
    if args.output_path != './test-output':
        os.environ['MARKDOWN_OUTPUT_PATH'] = args.output_path
    if args.template != './samples/productAPI.template.md':
        os.environ['TEMPLATE_PATH'] = args.template
    if args.model != 'gpt-4o':
        os.environ['OPENAI_MODEL'] = args.model
    if args.iterations != 3:
        os.environ['MAX_ITERATIONS'] = str(args.iterations)
    if args.threshold != 80:
        os.environ['COMPLETENESS_THRESHOLD'] = str(args.threshold)
    if args.timeout != 10:
        os.environ['TIMEOUT_MINUTES'] = str(args.timeout)

    print("🧪 YAML to Markdown Documentation Generator - Local Test")
    print("=" * 55)

    # Try to load .env file first
    load_env_file()

    # Setup environment
    if not setup_environment(args.openai_key, args.mock):
        sys.exit(1)

    # Validate setup
    if not validate_setup():
        sys.exit(1)

    # Print configuration
    print_configuration()

    # Ask for confirmation unless using mock
    if not args.mock:
        print(f"\n⚠️  This will make real API calls to OpenAI (model: {os.getenv('OPENAI_MODEL')})")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("❌ Test cancelled by user")
            sys.exit(0)

    # Run the generator
    success = run_generator()

    if success:
        print("\n🎉 Local test completed successfully!")
        print(f"📁 Check the output directory: {os.getenv('MARKDOWN_OUTPUT_PATH')}")
    else:
        print("\n💥 Local test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()