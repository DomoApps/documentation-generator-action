#!/bin/bash
# Quick test script with your API key
# Usage: ./quick_test.sh

export OPENAI_API_KEY="sk-your-actual-key-here"  # Replace with your key
export OPENAI_MODEL="gpt-4o"
export YAML_INPUT_PATH="./samples"
export MARKDOWN_OUTPUT_PATH="./test-output"
export TEMPLATE_PATH="./samples/productAPI.template.md"
export MAX_ITERATIONS="3"
export COMPLETENESS_THRESHOLD="80"
export TIMEOUT_MINUTES="10"

echo "🚀 Running quick test with predefined settings..."
python test_local.py