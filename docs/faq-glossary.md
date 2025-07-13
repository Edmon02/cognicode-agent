# 10. FAQ & Glossary: Your Quick Reference Guide

Welcome to the CogniCode Agent knowledge hub! This section is designed to quickly answer your most common questions and demystify any jargon or specific terminology you might encounter while exploring the project or this documentation.

## ❓ Frequently Asked Questions (FAQ)

We've compiled a list of questions that often pop up. If you don't see your question here, feel free to raise an issue on GitHub!

---
**General Questions**
---
*   **Q: What is CogniCode Agent in simple terms?**
    A: Think of it as your personal AI coding assistant that lives right on your computer. It reads your code in real-time, helps you find potential bugs, suggests ways to improve your code (like making it faster or easier to read), and can even help write basic tests for you. And the best part? It does all this privately on your machine; your code never gets sent to the cloud.

*   **Q: Who is CogniCode Agent for?**
    A: It's for any developer who wants an extra pair of AI-powered eyes on their code!
    *   **Junior developers** can learn best practices and catch common mistakes early.
    *   **Senior developers** can speed up tasks like identifying performance bottlenecks or getting initial test coverage.
    *   **Teams** can use it (with careful consideration for local-first principles) to help maintain code quality and consistency.

*   **Q: Is my code sent to any external servers for analysis?**
    A: **No, absolutely not.** This is a core design principle. All code analysis and AI model processing happen *locally* on your machine. Your intellectual property stays with you. See our [Privacy-First Local Processing feature](./features.md#privacy-first-local-processing) for more.

*   **Q: What programming languages does CogniCode Agent support?**
    A: CogniCode Agent supports a range of languages with varying levels of feature depth. Key languages include JavaScript, TypeScript, Python, and Java. For a detailed list and support tiers, please see the [Multi-Language Support section in Features](./features.md#-multi-language-support). We're always looking to expand this!

*   **Q: Is CogniCode Agent free to use?**
    A: Yes! CogniCode Agent is an open-source project licensed under the MIT License, making it free for both personal and commercial use.

*   **Q: What makes CogniCode Agent different from other AI coding tools or linters?**
    A: Key differentiators include its **privacy-first local processing**, its **multi-agent architecture** (specialized AIs for linting, refactoring, testing), and its aim to provide a **comprehensive suite** of AI-assisted development tools in one package. While many linters are rule-based, CogniCode Agent integrates (or plans to deeply integrate) AI models for more nuanced understanding.

---
**Setup & Installation**
---
*   **Q: What are the system requirements?**
    A: You'll need Node.js (16+), Python (3.8+), at least 4GB RAM (8GB+ highly recommended for AI models), and about 5GB of free disk space for the models. For more details, see [Prerequisites in Getting Started](./getting-started.md#-prerequisites-what-youll-need).

*   **Q: The `setup.sh` script failed. What should I do?**
    A: First, ensure the script is executable (`chmod +x setup.sh`). If it still fails, try the [Manual Setup steps](./getting-started.md#option-2-the-scenic-manual-route---know-your-machine-intimately). Check the error messages in your terminal for clues. Common issues include missing Python/Node versions or permission problems.

*   **Q: Why does the initial setup take a while?**
    A: The main reason is the download of AI models (like CodeBERT, CodeT5) via `server/scripts/download_models.py`. These models can be several gigabytes in size. Subsequent startups are much faster as the models are cached locally.

*   **Q: Can I use CogniCode Agent without an internet connection?**
    A: Yes! Once the initial setup (dependencies) and AI model downloads are complete, the core analysis features work entirely offline because all processing is local.

*   **Q: I'm getting a "port already in use" error when starting the servers.**
    A: This means another application is using the port CogniCode Agent needs (default 3000 for frontend, 8000 or 5000 for backend). You can either stop the other application or configure CogniCode Agent to use different ports via the `.env.local` and `server/.env` files. See the [Configuration Guide](./configuration.md#️-environment-variables-the-master-switches) for details.

---
**Usage & Features**
---
*   **Q: How "real-time" is the analysis?**
    A: The goal is near real-time. When you trigger an analysis (e.g., by clicking "Analyze" or if a future feature enables on-the-fly analysis), the request is sent to the local backend. The speed depends on your machine's resources (CPU, RAM), the size and complexity of the code, and the specific AI models being used. You'll see progress updates in the UI.

*   **Q: Are the AI suggestions always correct or optimal?**
    A: AI is incredibly powerful, but it's not infallible, and it doesn't (yet!) understand the full context of your project like you do. **Always critically review AI-generated suggestions before applying them.** CogniCode Agent is a tool to *assist* your judgment, not replace it.

*   **Q: Can I customize the analysis rules or the types of suggestions I get?**
    A: Currently, direct rule customization in the UI is limited. However, you can:
    *   Choose different AI models (see [Customizing AI Agents & Models](./configuration.md#-customizing-ai-agents--models-for-the-adventurous-developer)).
    *   For advanced users, modify the agent logic in `server/agents/` to change heuristics or rules.
    *   The "Analysis Levels" (Quick, Standard, Deep) mentioned in the original feature list suggest a future direction for user-selectable analysis depth.

*   **Q: How does the "Apply Refactoring" feature work?**
    A: When the `RefactorAgent` provides a suggestion that includes `refactoredCode`, the frontend's `RefactorPanel` will have an option to apply it. Clicking this updates the code in your editor directly. See the `onApplySuggestion` callback in [`app/page.tsx`](./codebase-explorer/frontend/app_directory.md#-pagetsx-the-main-application-dashboard--where-interaction-unfolds).

---
**Troubleshooting**
---
*   **Q: The backend server (`app.py`) isn't starting or crashes.**
    A: Check your terminal for error messages. Common causes:
        *   Python virtual environment (`server/venv`) not activated.
        *   Missing dependencies: re-run `pip install -r server/requirements.txt` in the active venv.
        *   Port conflicts (see above).
        *   Errors during AI model loading (check `MODELS_PATH` in `server/.env` and ensure models are downloaded).
        *   Incorrect `FLASK_ENV` or other backend environment variables.

*   **Q: The frontend UI loads, but it says "Disconnected" or "Cannot connect to backend."**
    A:
        1.  Ensure the backend server is running (check its terminal for logs).
        2.  Verify the `NEXT_PUBLIC_BACKEND_URL` in your frontend's `.env.local` file is correct and matches the host and port where the backend is actually running (e.g., `http://localhost:8000` or `http://localhost:5000`).
        3.  Check your browser's developer console for WebSocket connection errors or CORS issues.

*   **Q: Analysis results seem inconsistent or stale.**
    A: This could be due to several factors:
        *   **Caching:** The `CodeService` caches analysis results. While this is usually good for performance, if you suspect stale data, you could try restarting the backend server (which might clear in-memory caches depending on how it's implemented, though our `CodeService` cache is in-memory per instance). For a full reset, you might need to manually clear any persistent cache if one were added.
        *   **AI Model Variability:** Some AI models can have slight randomness (though usually controlled by seeds for reproducibility).
        *   **Code Context:** Very small, seemingly insignificant changes to your code can sometimes lead to different analysis paths or outputs from the AI.

---
**Contributing & Development**
---
*   **Q: I found a bug! How do I report it?**
    A: That's fantastic (well, not the bug, but that you found it!). Please head over to our [GitHub Issues Page](https://github.com/Edmon02/cognicode-agent/issues) and create a new issue. Provide as much detail as possible: steps to reproduce, what you expected, what actually happened, your OS/environment, and any relevant error messages or screenshots.

*   **Q: I have an idea for a new feature or want to contribute code. What's the process?**
    A: Awesome! We love contributions. Please start by reading our [Contributing Guide](./contributing.md). For significant features, it's often a good idea to open an issue first to discuss your proposal.

*   **Q: Where can I learn more about the architecture or a specific part of the code?**
    A: You're in the right place! This documentation, especially the [Architecture Deep Dive](./architecture.md) and the [Codebase Explorer](./codebase-explorer/), is designed for that. If something isn't clear, please let us know by opening an issue!

## 📖 Glossary of Terms: Decoding CogniCode Lingo

Here are definitions for common terms, technologies, and concepts you'll encounter while working with CogniCode Agent and its documentation.

*   **Agent (AI Agent):** A specialized Python class in the backend (`server/agents/`) responsible for a specific task (e.g., `LinterAgent` for linting, `RefactorAgent` for suggesting code changes, `TestGenAgent` for generating tests). Each agent typically uses one or more AI models.
*   **AgentPool:** A class in `server/app.py` that manages the lifecycle and access to instances of AI Agents, promoting resource efficiency.
*   **App Router (Next.js):** The newer routing system in Next.js (used in this project, located in the `app/` directory) that uses directory and file conventions to define routes and layouts.
*   **AST (Abstract Syntax Tree):** A tree-like representation of the syntactic structure of source code. Parsing code into an AST allows for more sophisticated analysis than simple text matching. The `LinterAgent` uses Python's `ast` module for analyzing Python code.
*   **Backend:** The server-side component of CogniCode Agent, built with Python and Flask. It runs locally, handles AI processing, and communicates with the frontend via WebSockets. Located in the `server/` directory.
*   **Client Component (Next.js/React):** A React component that is rendered on the client-side (in the browser) and can use React hooks like `useState` and `useEffect`, and interact with browser APIs. Marked with `'use client';` directive.
*   **CodeBERT:** A large language model pre-trained by Microsoft on a massive dataset of source code. It's excellent for code understanding tasks like bug detection, code search, and code documentation generation. Used by our `LinterAgent` (conceptually).
*   **CodeService:** A Python class in `server/services/code_service.py` that acts as a business logic layer between `app.py` (web handlers) and the AI agents. It processes, formats, and caches results from the agents.
*   **CodeT5:** A large language model pre-trained by Salesforce that can understand and generate code. It's well-suited for tasks like code refactoring, summarization, and translation. Used by our `RefactorAgent` (conceptually).
*   **Conventional Commits:** A specification for adding human and machine-readable meaning to commit messages. See our [Contributing Guide](./contributing.md#️-commit-message-conventions-writing-history-clearly).
*   **CORS (Cross-Origin Resource Sharing):** A browser security mechanism that controls whether a web application running at one origin (domain/port) can request resources from a server at a different origin. Essential for our frontend (e.g., `localhost:3000`) to talk to our backend (e.g., `localhost:8000`).
*   **`cn` function (`lib/utils.ts`):** A utility function that combines `clsx` (for conditional class names) and `tailwind-merge` (for resolving Tailwind CSS class conflicts) to make dynamic styling easier.
*   **Docker:** A platform for developing, shipping, and running applications in isolated environments called containers. CogniCode Agent provides Dockerfiles and a `docker-compose.yml` for containerization.
*   **Docker Compose:** A tool for defining and running multi-container Docker applications. Our `docker-compose.yml` defines how to run the frontend and backend services together.
*   **Dockerfile:** A text document that contains all the commands a user could call on the command line to assemble an image. We have `Dockerfile.frontend` and `server/Dockerfile`.
*   **Environment Variables:** Configuration values (e.g., port numbers, API keys, feature flags) that are set outside the application code, typically in `.env` files. See the [Configuration Guide](./configuration.md).
*   **ESLint:** A pluggable and configurable linter tool for identifying and reporting on patterns in JavaScript and TypeScript code.
*   **Flake8:** A Python library that wraps PyFlakes, pycodestyle, and McCabe to check Python code for style errors (PEP 8) and other issues.
*   **Flask:** A lightweight WSGI web application framework in Python. It's used as the foundation for our backend server in `server/app.py`.
*   **Flask-SocketIO:** A Flask extension that integrates Socket.IO, enabling real-time, bidirectional communication between the server and clients (our frontend).
*   **Frontend:** The client-side component of CogniCode Agent, built with Next.js and React. It runs in the user's browser and provides the user interface.
*   **Git:** A distributed version control system used for tracking changes in source code during software development.
*   **Hugging Face Transformers:** A popular Python library by Hugging Face that provides easy access to thousands of pre-trained state-of-the-art models for Natural Language Processing (NLP) and Machine Learning, including models like CodeBERT and CodeT5.
*   **Jest:** A JavaScript testing framework widely used for testing React applications, including Next.js projects.
*   **Linting:** The process of running a tool (a linter) that analyzes source code to flag programming errors, bugs, stylistic errors, and suspicious constructs.
*   **Local Processing:** A core principle of CogniCode Agent, meaning all data processing, including AI model inference, happens on the user's own machine, not on external servers.
*   **Lucide Icons:** A simply beautiful and consistent open-source icon set used in our frontend.
*   **Monaco Editor:** The code editor that powers Visual Studio Code. We use the `@monaco-editor/react` library to embed it in our frontend for a rich code input experience.
*   **Next.js:** A popular React framework for building full-stack web applications, offering features like server-side rendering, static site generation, file-system routing (including the App Router), and optimized builds.
*   **`next-themes`:** A library used in Next.js applications to easily implement dark mode and theme switching.
*   **npm (Node Package Manager):** The default package manager for Node.js, used for managing frontend project dependencies and running scripts defined in `package.json`.
*   **Pytest:** A mature and feature-rich Python testing framework used for testing our backend Python code.
*   **PyTorch:** An open-source machine learning framework primarily developed by Facebook's AI Research lab (FAIR). It's widely used for deep learning applications, including training and running models like those from Hugging Face Transformers.
*   **Refactoring:** The process of restructuring existing computer code—changing its internal structure—without changing its external behavior. The goal is often to improve readability, reduce complexity, or enhance maintainability.
*   **shadcn/ui:** A collection of beautifully designed, accessible, and customizable React components built using Radix UI and Tailwind CSS. We use it for many of our UI elements.
*   **Socket.IO:** A library that enables real-time, event-based, bidirectional communication between web clients and servers. It's built on top of WebSockets and provides fallbacks for older browsers/environments.
*   **Sonner (Toast Library):** A library used to display elegant and non-intrusive notifications (toasts) in our frontend.
*   **Tailwind CSS:** A utility-first CSS framework for rapidly building custom user interfaces. Instead of writing custom CSS, you apply pre-defined utility classes directly in your HTML/JSX.
*   **TypeScript:** An open-source language developed by Microsoft that builds on JavaScript by adding static type definitions. This helps catch errors early and improves code maintainability and developer experience.
*   **Unit Testing:** A software testing method by which individual units of source code (functions, methods, components) are tested in isolation to determine if they are fit for use.
*   **Virtual Environment (Python `venv`):** An isolated Python environment that allows packages to be installed for use by a particular application, rather than being installed system-wide. Crucial for managing dependencies.
*   **WebSocket:** A communication protocol that provides a full-duplex (two-way) communication channel over a single, long-lived TCP connection. Used for real-time updates between our frontend and backend.

*(This glossary will be expanded as more specific terms are identified or if new technologies are introduced.)*

---
Next: [Changelog](changelog.md)
