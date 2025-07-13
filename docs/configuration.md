# 6. Configuration & Customization: Tailoring CogniCode Agent to Your Needs

CogniCode Agent is engineered to be a powerful ally right out of the box. However, we believe that the best tools are those that can adapt to *your* unique way of working and your project's specific demands. This section is your guide to tweaking, tuning, and tailoring CogniCode Agent to make it truly your own. From environment variables that control core behavior to customizing the look and feel, let's explore how you can put your personal stamp on this AI companion.

## ⚙️ Environment Variables: The Master Switches

The primary way to configure CogniCode Agent's core operational parameters is through environment variables. These act as master switches, allowing you to define crucial settings for both the frontend and backend components without needing to modify the codebase itself.

### Frontend Configuration (`.env.local` in the project root)

To customize the frontend, create a file named `.env.local` in the main project directory (the same level as `package.json`). This file is gitignored, so your local settings won't be committed.

Here are the variables you can set:

*   **`NEXT_PUBLIC_BACKEND_URL`**
    *   **Purpose:** This is the critical link! It tells your Next.js frontend the network address (URL and port) where the Python backend server is listening for WebSocket connections and API calls.
    *   **How it's used:** The `useSocket` hook ([`hooks/use-socket-real.ts`](./codebase-explorer/frontend/hooks_directory.md#-use-socket-realts-the-real-time-communication-engine)) reads this variable to establish its connection.
    *   **Default if not set (from `use-socket-real.ts`):** `http://localhost:8000` (Note: The main README example shows `http://localhost:5000`. Ensure this matches your backend's `PORT` setting.)
    *   **Example:**
        ```env
        NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
        ```
    *   **Why `NEXT_PUBLIC_`?** In Next.js, environment variables prefixed with `NEXT_PUBLIC_` are embedded into the JavaScript bundle and are accessible on the client-side (in the browser). Variables without this prefix are only available during the build process or on the server-side (if using Next.js server-side features, which we primarily don't for the core agent interaction).

*   **`NEXT_PUBLIC_APP_NAME`**
    *   **Purpose:** Allows you to set a custom display name for the application. This might be used in the browser window title (though `app/layout.tsx` sets a more specific title) or potentially in UI elements.
    *   **How it's used:** The main `README.md` suggests this, but its direct usage in the current UI components (`Header`, `layout.tsx metadata`) seems to use hardcoded or specific titles. If used, it would be accessed via `process.env.NEXT_PUBLIC_APP_NAME` in frontend components.
    *   **Default (from README example):** `CogniCode Agent`
    *   **Example:**
        ```env
        NEXT_PUBLIC_APP_NAME="My Supercharged Dev Assistant"
        ```

### Backend Configuration (`.env` in the `server/` directory)

For the backend, create a file named `.env` inside the `server/` directory. This file is also gitignored. The `AppConfig` class in `server/app.py` ([see walkthrough](./codebase-explorer/backend/app_py.md#-appconfig-class-central-command-for-configuration)) reads these variables.

*   **`FLASK_ENV`**
    *   **Purpose:** Sets the operational environment for the Flask application.
    *   **Values:**
        *   `development`: Enables debug mode (provides detailed error pages in the browser, auto-reloads server on code changes), often sets more verbose logging. Ideal for local development.
        *   `production`: Disables debug mode and uses settings more appropriate for a stable, deployed application.
    *   **Default (from `AppConfig`):** `production`
    *   **Example (from main README, good for local dev):**
        ```env
        FLASK_ENV=development
        ```

*   **`PORT`**
    *   **Purpose:** Specifies the network port on which the Python Flask backend server will listen for incoming connections.
    *   **Default (from `AppConfig`):** `8000`
    *   **Example (from main README):**
        ```env
        PORT=5000
        ```
        *Remember to ensure `NEXT_PUBLIC_BACKEND_URL` on the frontend points to this port!*

*   **`SECRET_KEY`**
    *   **Purpose:** A cryptographically secure random string used by Flask for signing session cookies and other security-related purposes. **This is critical for security.**
    *   **Default (from `AppConfig`):** `cognicode-secret-key-2025`
    *   **Recommendation:** **ALWAYS override the default for any instance that might be exposed, even on a local network if you're security-conscious.** Generate a long, random string. You can use Python to generate one:
        ```python
        import os; os.urandom(24).hex()
        ```
    *   **Example:**
        ```env
        SECRET_KEY=a_very_long_and_super_random_string_of_characters
        ```

*   **`MODELS_PATH`**
    *   **Purpose:** Defines the directory path where AI models are stored or where the `server/scripts/download_models.py` script should download them.
    *   **Default (implied by `download_models.py` and agent configurations):** `./models` (relative to the `server/` directory).
    *   **Example:**
        ```env
        MODELS_PATH=/path/to/your/ai_models_folder
        ```
        *(Note: If you change this, ensure `download_models.py` and agent model loading logic can correctly use this path.)*

*   **`USE_DEMO_MODE`**
    *   **Purpose:** The main `README.md` mentions this variable. Its actual impact would depend on how it's used within the codebase (e.g., in `app.py` or the agents). It might enable features like mocked AI responses for demonstrations, bypass certain checks, or limit functionality.
    *   **Values:** `true` or `false`.
    *   **Default (from README example):** `true` (The `AppConfig` class in `app.py` does not explicitly read this, so its effect might be through other means or a planned feature).

*   **`LOG_LEVEL`**
    *   **Purpose:** Controls the verbosity of the backend logger (configured in `server/utils/logger.py`).
    *   **Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
    *   **Default (if `setup_logger` is called without a level, it defaults to 'INFO'):** `INFO` (as per README example). `DEBUG` is very verbose, useful for deep troubleshooting.
    *   **Example:**
        ```env
        LOG_LEVEL=DEBUG
        ```

*   **Backend Performance Tuning Variables (from `AppConfig`):**
    *   **`MAX_CONNECTIONS`**
        *   **Purpose:** Intended to control the maximum number of concurrent connections (likely WebSocket clients) the server or `AgentPool` might handle.
        *   **Default (from `AppConfig`):** `100`
    *   **`AGENT_POOL_SIZE`**
        *   **Purpose:** Could influence how many agent instances are pre-initialized or the maximum size of the pool for each agent type in the `AgentPool`.
        *   **Default (from `AppConfig`):** `3`
    *   **`CACHE_TIMEOUT`**
        *   **Purpose:** Sets the expiration time in seconds for items in the `CodeService`'s analysis cache.
        *   **Default (from `AppConfig`):** `3600` (1 hour)

## 🎨 Frontend Customization: Beyond Environment Variables

While environment variables handle core settings, you can also customize the frontend's appearance and component behavior more directly:

*   **Theming (Light/Dark Mode & Colors):**
    *   **How it works:** Theming is managed by `next-themes` via the `ThemeProvider` component (used in [`app/layout.tsx`](./codebase-explorer/frontend/app_directory.md#-layouttsx-the-root-layout--our-applications-consistent-shell)). Colors are defined as CSS custom properties in `app/globals.css` ([see details](./codebase-explorer/frontend/app_directory.md#-globalscss-the-canvas--color-palette)).
    *   **Customization:** You can modify the HSL color values in `app/globals.css` for `:root` (light theme) and `.dark` (dark theme) to change the application's color scheme. For deeper changes, you might adjust `tailwind.config.ts` which defines the Tailwind theme (spacing, fonts, colors that `shadcn/ui` might build upon).

*   **`shadcn/ui` Component Configuration:**
    *   **`components.json`**: This file in the project root is used by the `shadcn/ui` CLI to know where to place new components and how to resolve aliases (like `@/*`). You generally don't need to edit this unless you're restructuring your project significantly.
    *   **Styling `shadcn/ui` components**: Most `shadcn/ui` components are styled using Tailwind utility classes. You can customize them by either:
        1.  Copying the component code from the `shadcn/ui` documentation into your `components/ui/` directory and modifying its internal Tailwind classes.
        2.  Applying additional Tailwind classes when you use the component in your JSX.

## 🧠 Customizing AI Agents & Models: For the Adventurous Developer

CogniCode Agent is designed with flexibility in mind, even down to the AI models it uses.

*   **Using Different Hugging Face Models:**
    *   **How it works:** Each agent (e.g., `LinterAgent`, `RefactorAgent`) is initialized with a specific model name in its constructor (see [`server/agents/base_agent.py`](./codebase-explorer/backend/agents_directory.md#-base_agentpy-the-agent-blueprint--foundation-for-intelligence) and its subclasses). For example, `LinterAgent` defaults to `'microsoft/codebert-base'`.
    *   **Customization:** You can change these model string identifiers in the agent's `__init__` method to point to a different compatible model from the Hugging Face Hub.
    *   **Considerations:**
        *   **Compatibility:** The new model must be compatible with the task the agent performs (e.g., a text generation model for `RefactorAgent`, a code understanding model for `LinterAgent`).
        *   **Resource Requirements:** Different models have vastly different sizes and computational needs. Ensure your local machine can handle the new model.
        *   **Tokenizer:** The model's corresponding tokenizer must also be available and correctly loaded. `AutoModel` and `AutoTokenizer` from the `transformers` library usually handle this well if the model is on the Hub.
    *   **Example (Conceptual - in `LinterAgent.__init__`):**
        ```python
        # super().__init__('LinterAgent', 'microsoft/codebert-base') # Default
        super().__init__('LinterAgent', 'another/compatible-code-model') # Custom
        ```
    *   The main `README.md` also mentions a `CUSTOM_MODELS` dictionary example for `base_agent.py`. This suggests a more centralized way to override model names, potentially by modifying `BaseAgent` to consult such a dictionary or by passing model names during `AgentPool` initialization. The current `BaseAgent` code initializes `self.model_name` directly in its `__init__`.

*   **Fine-tuning Models (Advanced):**
    *   While CogniCode Agent uses pre-trained models, fine-tuning these models on your specific codebase or coding standards is a possibility for achieving highly tailored results.
    *   This is an advanced Machine Learning task, typically involving:
        *   Curating a dataset of your code and desired analysis outputs/refactorings.
        *   Using libraries like `transformers` to train the model further.
    *   This is beyond the scope of simple configuration and would require significant ML expertise. *(Future guides or community contributions might explore this!)*

*   **Modifying Agent Logic (Advanced):**
    *   If you want to change how an agent processes information or the rules it uses (especially for the current heuristic-based parts of `LinterAgent`, `RefactorAgent`, `TestGenAgent`), you would need to directly modify the Python code within the respective agent files in the `server/agents/` directory. This allows for complete control but requires understanding the agent's internal structure.

## 🔧 Adjusting Analysis Parameters (User-Level Customization - If Available)

The `docs/user-guide/features.md` (existing documentation) mentions "Analysis Levels: Quick, Standard, Deep." This implies that users might be able to select the depth or focus of the analysis.

*   **How it might work:**
    *   The frontend (`app/page.tsx`) could have UI elements (e.g., a dropdown) to select an analysis level.
    *   This selection would be passed as a parameter in the `analyze_code` WebSocket event to the backend.
    *   The `LinterAgent` (or other agents) would then adjust their behavior based on this parameter (e.g., run more rules, use different model inference settings, limit analysis time).
*   **Current Implementation:** A quick review of `app/page.tsx` and `LinterAgent` doesn't immediately show a UI element or backend handling for these distinct levels. This might be a planned feature or one that's configured differently. If such parameters are available (e.g., via hidden flags or specific input to agents), they would be detailed here after further code exploration.

By understanding these configuration points, you can significantly adapt CogniCode Agent to better suit your development practices and project requirements.

---
Next: [Testing & Validation](testing.md)
