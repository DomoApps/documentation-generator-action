# Documentation Reviewer GitHub Action

This repository contains a reusable GitHub Action that leverages AI to automate the review of pull requests (PRs). The action integrates with OpenAI's GPT model to provide meaningful feedback on code changes, helping maintain code quality and streamline the review process.

## Features

- **AI-Powered Reviews**: Uses OpenAI's GPT model to analyze code changes and provide actionable feedback.
- **GitHub Integration**: Automatically fetches PR details and posts comments directly on GitHub.
- **Customizable**: Supports configuration for target file extensions and AI model settings.

## Usage
IMPORTANT NOTE:
I haven't tested this across organizations. Our GHES Action Runners do not support actions on public repositories. This is very beta phase, so all feedback is welcome

To use this GitHub Action in your repository, follow these steps:

1. Create a workflow file (e.g., `.github/workflows/review.yml`) in your repository:

   ```yaml
   name: Pull Request ChatGPT review
   on:
     pull_request:
       types: [opened, synchronize, reopened]

   jobs:
     ai_pr_reviewer:
       uses: eps/github-reviewer-action/.github/workflows/action.yml@main
       secrets: inherit
   ```

1. Add the Github Secrets to your repository:
   - \*`GITHUB_TOKEN`: Your Github Access Token.
     - **Required**
1. Add the Github Variables for target file extensions to review:
   - `TARGET_EXTENSIONS`: Comma-separated list of file extensions to review (e.g., `py,js`).
     - Default: `py,js`.
   - `CHATGPT_MODEL`: The AI model to use (e.g., `gpt-4`).
     - Default: `gpt-4o`.
   - `FOCUS_AREAS`: Written instructions to be included in AI prompt for areas of focus.
     - **Required**.

## Inputs

| Input Name          | Description                                                                  | Required | Default |
| ------------------- | ---------------------------------------------------------------------------- | -------- | ------- |
| `repo_owner`        | The owner of the repository.                                                 | Yes      |         |
| `repo_name`         | The name of the repository.                                                  | Yes      |         |
| `pull_number`       | The pull request number to review.                                           | Yes      |         |
| `github_token`      | A GitHub personal access token with appropriate permissions.                 | Yes      |         |
| `chatgpt_model`     | The AI model to use (e.g., `gpt-4`).                                         | No       | gpt-4o  |
| `target_extensions` | Comma-separated list of file extensions to review (e.g., `py,js`).           | No       | py,js   |
| `focus_areas`       | Specific areas to focus on during the review (e.g., `security,performance`). | No       |         |

## Outputs

This action does not produce any outputs but posts comments directly on the pull request.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
