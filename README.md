# Documentation Reviewer GitHub Action

This repository contains a reusable GitHub Action that leverages AI to automate the review of pull requests (PRs). The action integrates with OpenAI's GPT model to provide meaningful feedback on code changes, helping maintain code quality and streamline the review process.

## Features

- **AI-Powered Reviews**: Uses OpenAI's GPT model to analyze code changes and provide actionable feedback.
- **GitHub Integration**: Automatically fetches PR details and posts comments directly on GitHub.
- **Customizable**: Supports configuration for target file extensions and AI model settings.

## Usage

To use this GitHub Action in your repository, follow these steps:

1. Create a workflow file (e.g., `.github/workflows/review.yml`) in your repository:

   ```yaml
   name: AI-Powered PR Review

   on:
     pull_request:
       types: [opened, synchronize, reopened]

   jobs:
     review:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - name: Run Documentation Reviewer Action
           uses: your-username/doc_reviewer_action@v1
           with:
             repo_owner: ${{ github.repository_owner }}
             repo_name: ${{ github.event.repository.name }}
             pull_number: ${{ github.event.pull_request.number }}
             github_token: ${{ secrets.GITHUB_TOKEN }}
             chatgpt_key: ${{ secrets.CHATGPT_KEY }}
             chatgpt_model: gpt-4
             target_extensions: py,js
   ```

2. Add the required secrets to your repository:
   - `GITHUB_TOKEN`: Automatically provided by GitHub Actions.
   - `CHATGPT_KEY`: Your OpenAI API key.

## Inputs

| Input Name         | Description                                                                 | Required | Default |
|--------------------|-----------------------------------------------------------------------------|----------|---------|
| `repo_owner`       | The owner of the repository.                                               | Yes      |         |
| `repo_name`        | The name of the repository.                                                | Yes      |         |
| `pull_number`      | The pull request number to review.                                         | Yes      |         |
| `github_token`     | A GitHub personal access token with appropriate permissions.               | Yes      |         |
| `chatgpt_key`      | Your OpenAI API key.                                                       | Yes      |         |
| `chatgpt_model`    | The AI model to use (e.g., `gpt-4`).                                       | No       | gpt-4   |
| `target_extensions`| Comma-separated list of file extensions to review (e.g., `py,js`).         | No       | py,js   |

## Outputs

This action does not produce any outputs but posts comments directly on the pull request.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
