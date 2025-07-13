# 9. Contributing to CogniCode Agent: Join the Mission!

🚀 **Welcome, Future CogniCoder!** 🚀

First off, thank you for considering contributing to CogniCode Agent! This project thrives on the passion, expertise, and feedback of the developer community – people just like you. Whether you're here to squash a bug, dream up a new feature, polish our documentation, or share a brilliant idea, your involvement is what makes open source magical.

CogniCode Agent is built by developers, for developers. We aim to foster an environment that is welcoming, respectful, and collaborative. Every contribution, no matter how small, is valued and helps us move closer to our vision of an intelligent, privacy-first coding companion.

This guide is your map to navigating the contribution process. Let's build something amazing together!

## 📜 Code of Conduct: Our Community Compass

Before you dive in, please take a moment to read our [Code of Conduct](./CODE_OF_CONDUCT.md). We expect all members of the CogniCode Agent community – contributors, maintainers, and users alike – to adhere to these guidelines. This helps us ensure a positive, inclusive, and harassment-free environment for everyone. Let's treat each other with respect and empathy.

## 🛠️ Getting Your Workshop Ready: Setting Up for Contribution

Ready to roll up your sleeves and get coding (or documenting)? Here’s how to set up your local development environment. It's very similar to the standard setup, with a few extra steps for contributing back to the main project.

1.  **Fork the Mothership (The Repository):**
    *   Navigate to the main CogniCode Agent GitHub repository: [https://github.com/Edmon02/cognicode-agent](https://github.com/Edmon02/cognicode-agent)
    *   In the top-right corner, click the "Fork" button. This creates your personal copy of the repository under your GitHub account. It's like getting your own sandbox to play in!

2.  **Clone Your Fork to Your Local Machine:**
    Now, bring your forked repository to your computer:
    ```bash
    git clone https://github.com/YOUR_USERNAME/cognicode-agent.git
    cd cognicode-agent
    ```
    Remember to replace `YOUR_USERNAME` with your actual GitHub username.

3.  **Connect to the Source (Set Upstream Remote):**
    To keep your fork in sync with the main project (often called "upstream"), you need to add it as a remote:
    ```bash
    git remote add upstream https://github.com/Edmon02/cognicode-agent.git
    ```
    You can verify this by typing `git remote -v`. You should see both `origin` (your fork) and `upstream` (the main repo).

4.  **Follow the Standard Project Setup:**
    Now that you have the code, follow the instructions in our [Getting Started Guide](./getting-started.md) to:
    *   Install all frontend dependencies (e.g., `npm install`).
    *   Set up the Python virtual environment for the backend and install its dependencies (e.g., `cd server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd ..`).
    *   Download the necessary AI models by running `python server/scripts/download_models.py` (ensure your backend venv is active).
    *   The `setup.sh` script in the root directory can automate most of these dependency installation steps.

## 🌿 Our Git Workflow: The Art of Collaborative Coding

We follow a standard "Fork & Pull Request" workflow with feature branches. This keeps the main codebase clean and makes collaboration smooth.

1.  **Keep Your `main` Branch Pristine:** Your local `main` branch should be a clean reflection of the `upstream/main`. Before starting any new work, make sure it's up-to-date:
    ```bash
    git checkout main
    git fetch upstream # Fetch changes from the main repository
    git rebase upstream/main # Rebase your local main onto the upstream main (or use git pull upstream main)
    git push origin main # Optional: update your fork's main branch on GitHub
    ```

2.  **Create a Dedicated Feature Branch:**
    Never work directly on your `main` branch! For every new feature, bug fix, or documentation update, create a new branch off your up-to-date `main` branch. Use a descriptive name:
    *   For features: `feature/your-cool-new-feature` (e.g., `feature/add-ruby-linter`)
    *   For bug fixes: `fix/issue-number-short-description` (e.g., `fix/123-linter-crash-on-empty-file`)
    *   For documentation: `docs/update-contributing-guide`
    ```bash
    git checkout -b feature/your-amazing-feature
    ```

3.  **Code, Test, Document, Commit – The Creative Loop:**
    *   **Code:** Implement your changes. Follow our [Coding Standards](#️-coding-standards--linting-keeping-our-code-tidy).
    *   **Test:** Write new tests for your changes and ensure all existing tests pass. See the [Testing Guide](./testing.md).
    *   **Document:** If you're adding a new feature or changing behavior, update the relevant documentation (including this guide if necessary!).
    *   **Commit:** Make small, logical commits. Follow our [Commit Message Conventions](#️-commit-message-conventions-writing-history-clearly).
    ```bash
    git add . # Stage your changes
    git commit -m "feat(linter): Add initial support for Ruby analysis"
    ```

4.  **Keep Your Branch Updated (Rebase, Don't Merge):**
    Periodically, especially before pushing or opening a PR, update your feature branch with the latest changes from `upstream/main` to avoid complex merge conflicts later:
    ```bash
    git fetch upstream
    git rebase upstream/main
    ```
    (You might need to resolve conflicts if any arise during the rebase.)

5.  **Push Your Branch to Your Fork:**
    ```bash
    git push origin feature/your-amazing-feature
    ```
    If you rebased, you might need to force push to your branch on your fork (use with caution if others are collaborating on your fork's branch): `git push --force-with-lease origin feature/your-amazing-feature`.

6.  **Open a Pull Request (PR) on GitHub:**
    *   Go to your forked repository on GitHub (`https://github.com/YOUR_USERNAME/cognicode-agent`).
    *   GitHub will usually detect your recently pushed branch and show a button to "Compare & pull request."
    *   **Base Repository:** `Edmon02/cognicode-agent` | **Base Branch:** `main`
    *   **Head Repository:** `YOUR_USERNAME/cognicode-agent` | **Compare Branch:** `feature/your-amazing-feature`
    *   Write a clear and descriptive title for your PR.
    *   In the PR description:
        *   Explain *what* your changes do and *why* you made them.
        *   Reference any GitHub issues your PR addresses (e.g., "Closes #123", "Fixes #456").
        *   Mention any specific areas you'd like reviewers to focus on.
    *   If there's a PR template, please fill it out.

## 💅 Coding Standards & Linting: Keeping Our Code Tidy

Consistent code style makes the codebase easier to read, understand, and maintain for everyone. We use linters and formatters to help enforce these standards.

*   **Frontend (TypeScript/React):**
    *   **ESLint:** Our primary linter for JavaScript and TypeScript. Configuration is likely in `.eslintrc.js` or `package.json`. It helps catch syntax errors, style issues, and potential bugs.
    *   **Prettier (often used with ESLint):** For consistent code formatting.
    *   **Command:** Run `npm run lint` from the project root to check your frontend code. Please fix any linting errors before submitting a PR.
    *   **General Practices:** Follow standard React best practices, aim for functional components with hooks, and ensure good component modularity.

*   **Backend (Python):**
    *   **Black:** The "uncompromising Python code formatter." We use Black to ensure uniform code style.
    *   **Flake8:** A wrapper around PyFlakes, pycodestyle, and McCabe. It checks for style errors (PEP 8), programming errors (like unused variables), and complexity.
    *   **Configuration:** Settings for these tools might be in `pyproject.toml` or `setup.cfg` (not visible in current file listing, but common).
    *   **Commands (from the `server/` directory, with your virtual environment active):**
        ```bash
        # Format code with Black
        black .
        # Check for linting errors with Flake8
        flake8 .
        ```
        Please format your Python code with Black and fix Flake8 errors before committing. Many IDEs can be configured to run these tools automatically on save.

*   **General Principles (All Code):**
    *   **Readability:** Write code that is easy for other humans to understand.
    *   **Comments:** Write clear, concise comments for complex logic, non-obvious decisions, or public APIs. "Why, not just what."
    *   **Naming:** Use descriptive and consistent names for variables, functions, classes, and files.
    *   **Simplicity:** Prefer simple, straightforward solutions over overly complex ones (KISS principle).

## 💌 Commit Message Conventions: Writing History Clearly

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This makes our Git history more readable, helps automate changelog generation, and allows tools to understand the nature of changes.

**Format:**
```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

**Common Types:**
*   `feat`: A new feature for the user (e.g., `feat(linter): Add support for Ruby analysis`).
*   `fix`: A bug fix for the user (e.g., `fix(parser): Handle empty input gracefully`).
*   `docs`: Changes to documentation only (e.g., `docs(readme): Clarify setup instructions`).
*   `style`: Code style changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.) (e.g., `style(frontend): Apply Prettier formatting`).
*   `refactor`: A code change that neither fixes a bug nor adds a feature, but improves the internal structure (e.g., `refactor(backend): Simplify AgentPool initialization`).
*   `perf`: A code change that improves performance (e.g., `perf(cache): Optimize cache retrieval logic`).
*   `test`: Adding missing tests or correcting existing tests (e.g., `test(agents): Add unit tests for LinterAgent`).
*   `chore`: Changes to the build process, auxiliary tools, or other maintenance tasks that don't modify src or test files (e.g., `chore: Update Dockerfile base image`).
*   `ci`: Changes to our CI configuration files and scripts.

**Example:**
```
feat(refactor): Add suggestion for arrow function conversion

This commit introduces a new refactoring suggestion that identifies
opportunities to convert traditional JavaScript functions to ES6
arrow functions where appropriate.

Fixes #201
```

## 🚀 How to Add a Feature (Tutorial Example): Adding a "Copy Code Hash" Button

Let's walk through a hypothetical example: adding a small button to the UI that copies the `code_hash` (from the analysis results) to the clipboard.

1.  **Understand & Discuss (Optional but good for big features):**
    *   *Goal:* Allow users to easily copy the code hash.
    *   *Location:* Maybe in the `AnalysisPanel` near where other metadata is shown.
    *   *If it's a larger feature, open a GitHub Issue first to discuss the idea with maintainers.*

2.  **Setup Your Branch:**
    ```bash
    git checkout main
    git pull upstream main
    git checkout -b feat/copy-code-hash-button
    ```

3.  **Implement the Frontend Change:**
    *   **Modify `components/analysis-panel.tsx`:**
        *   Add a new button element.
        *   Add an icon (e.g., `<ClipboardCopyIcon />` from `lucide-react`).
        *   Write a click handler that uses `navigator.clipboard.writeText(analysis.code_hash)` and shows a success/error toast.
    *   **Add Tests:** If the logic is non-trivial, add a unit test for the click handler or component interaction.

4.  **Documentation (If Applicable):**
    *   Since this is a small UI tweak, it might not need a dedicated docs section, but if it were a new configurable feature, you'd update `docs_new/features.md` or `docs_new/configuration.md`.

5.  **Lint, Format, and Test:**
    *   From project root: `npm run lint` (fix errors)
    *   From project root: `npm test` (ensure all tests pass)

6.  **Commit Your Changes:**
    ```bash
    git add components/analysis-panel.tsx
    # Add any other changed files
    git commit -m "feat(ui): Add button to copy code_hash from AnalysisPanel" -m "Allows users to easily grab the code hash for reference or debugging."
    ```

7.  **Push to Your Fork:**
    ```bash
    git push origin feat/copy-code-hash-button
    ```

8.  **Open a Pull Request:**
    *   Go to your fork on GitHub and create a PR against `Edmon02/cognicode-agent`'s `main` branch.
    *   Fill in the PR description clearly.

## 📬 Submitting Pull Requests (PRs): Sharing Your Masterpiece

You've done the hard work, and now it's time to share it!

*   **One PR per Feature/Fix:** Keep your PRs focused on a single logical change. This makes them easier to review and merge.
*   **Clear Title & Description:** Explain *what* your PR does and *why* it's needed. If it fixes an issue, link to it (e.g., "Closes #123").
*   **Draft PRs for Early Feedback:** If you want feedback on work-in-progress, open a "Draft" Pull Request.
*   **Ensure Tests Pass:** All automated checks (linting, unit tests) configured in our CI pipeline (if any) must pass. Run tests locally first!
*   **Code Review & Iteration:** Be prepared for feedback! Maintainers will review your code and may request changes or ask questions. This is a normal and healthy part of the collaborative process. Respond to comments and push updates to your PR branch.
*   **Patience:** Reviewing takes time. We appreciate your patience!

Thank you for your interest in making CogniCode Agent even better. We're excited to see your contributions! If you have questions, feel free to open an issue or join our community discussions (if available).

---
Next: [FAQ & Glossary](faq-glossary.md)
