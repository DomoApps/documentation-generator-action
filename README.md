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
   - \*`GITHUBAPI_TOKEN`: Your Github Access Token.
     - **Required**
1. Add the Github Variables for target file extensions to review:
   - `TARGET_EXTENSIONS`: Comma-separated list of file extensions to review (e.g., `py,js`).
     - Default: `py,js`.
   - `CHATGPT_MODEL`: The AI model to use (e.g., `gpt-4`).
     - Default: `gpt-4o`.
   - `FOCUS_AREAS`: Written instructions to be included in AI prompt for areas of focus.
     - **Required**.
     - Example:
       ```performance: Ensure the code is optimized for performance, avoiding unnecessary re-renders and using efficient algorithms.
         security: Check for potential security vulnerabilities, such as unsafe handling of user input or improper use of third-party libraries.
         accessibility: Verify that the code adheres to accessibility standards (e.g., ARIA roles, keyboard navigation).
         code_quality: Ensure the code is clean, maintainable, and follows best practices.
         ui_consistency: Check for consistency in UI components and adherence to design guidelines.
         naming_contentions: Ensure good conventions are used, and that the naming aligns with the rest of the file
       ```

## Inputs

| Input Name          | Description                                                                  | Required | Default | Inclusion |
| ------------------- | ---------------------------------------------------------------------------- | -------- | ------- | ---------
| `github_token`      | A GitHub personal access token with appropriate permissions.                 | Yes      |         | Secret    |
| `chatgpt_model`     | The AI model to use (e.g., `gpt-4`).                                         | No       | gpt-4o  | Vars      |
| `target_extensions` | Comma-separated list of file extensions to review (e.g., `py,js`).           | No       | py,js   | Vars      |
| `focus_areas`       | Specific areas to focus on during the review (e.g., `security,performance`). | No       |         | Vars      |

## Outputs

This action does not produce any outputs but posts comments directly on the pull request.

## Contributing

Contributions are welcome! Please follow these steps:

1. Create a branch `<your name>/<feature or bug>` from the `main` branch to ensure your changes are based on the latest code.
2. Make your changes, ensuring they align with the project's coding standards and guidelines.
3. Write clear and concise commit messages to describe your changes.
4. Test your changes thoroughly to ensure they work as expected and do not introduce any new issues.
5. Submit a pull request with a clear and detailed description of your changes, including the problem being solved, the approach taken, and any potential impacts.
6. Engage in the review process by addressing feedback and making necessary updates to your pull request.
