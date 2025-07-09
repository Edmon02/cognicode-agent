# 2. Getting Started with CogniCode Agent

So, you're ready to bring the power of AI to your local development environment? Fantastic! This section will guide you through setting up CogniCode Agent and performing your first analysis. We've tried to make it as smooth as a perfectly refactored function.

## 📋 Prerequisites: What You'll Need

Before we dive in, let's make sure your system has the necessary ingredients. Think of this as your `mise en place` for coding excellence:

*   **Node.js:** Version 16 or higher. This is for our sleek Next.js frontend. You can check your version with `node -v`.
*   **npm (or yarn/pnpm):** Comes with Node.js. Used for managing frontend dependencies.
*   **Python:** Version 3.8 or higher. Our intelligent backend agents are Python-powered. Check with `python --version` or `python3 --version`.
*   **pip:** Python's package installer. Usually comes with Python.
*   **Git:** For cloning the repository.
*   **RAM:** A minimum of 4GB is required, but **8GB+ is highly recommended**, especially for the AI models to breathe comfortably.
*   **Disk Space:** At least 5GB of free disk space for the AI models. They're smart, but they need their space!

*(Detailed instructions on installing these prerequisites can be found in Appendix A: Installing Prerequisites - if needed, or link to external guides)*

## ⚙️ Setting Up Your Environment: The Pre-Flight Checklist

Alright, let's get your local environment prepped for CogniCode Agent. We'll walk through two paths: the express automated setup, and the scenic manual route for those who like to see all the steps.

### Option 1: The Automated Superhighway (`setup.sh`) - Get Ready to Launch!

For the quickest liftoff, we've bundled the initial setup into a handy script.

1.  **Clone the Mothership (The Repository):**
    If you haven't already, grab the code from GitHub:
    ```bash
    git clone https://github.com/Edmon02/cognicode-agent.git
    cd cognicode-agent
    ```
2.  **Engage the Setup Thrusters (`setup.sh`):**
    This script is your friendly neighborhood robot that will:
    *   Install frontend dependencies (`npm install`). Like stocking the cockpit with snacks.
    *   Set up a Python virtual environment for the backend (`python3 -m venv server/venv`). This gives our Python agents their own pristine workspace.
    *   Install backend dependencies (`pip install -r server/requirements.txt`). Equips the agents with their tools.

    Make it executable and run it:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    Watch the console for messages. If all goes well, you're almost ready for the next step!
    *(Note: `setup.sh` only handles the setup. We'll start the application engines in a moment.)*

### Option 2: The Scenic Manual Route - Know Your Machine Intimately

Prefer a hands-on approach? Here’s the step-by-step manual setup:

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone https://github.com/Edmon02/cognicode-agent.git
    cd cognicode-agent
    ```

2.  **Frontend Setup (The Command Deck):**
    Navigate to the project root (you should be there after cloning).
    ```bash
    npm install
    ```
    This command is like a shopping spree for your frontend, grabbing all the Next.js, React, and UI component goodies.

3.  **Backend Setup (The Engine Room):**
    Time to power up the Python side.
    ```bash
    cd server
    python3 -m venv venv
    ```
    This creates a dedicated virtual space for our backend. Now, activate it:
    *   On macOS/Linux: `source venv/bin/activate`
    *   On Windows: `venv\\Scripts\\activate`
    You should see `(venv)` at the beginning of your terminal prompt. Now, install the Python tools:
    ```bash
    pip install -r requirements.txt
    ```
    Once done, navigate back to the project root:
    ```bash
    cd ..
    ```

### Crucial Step for Both Routes: Downloading the AI Brains!

The real magic of CogniCode Agent comes from its locally-run AI models. These are like the specialized knowledge databases for our agents.

1.  **Navigate to the Server Directory:**
    ```bash
    cd server
    ```
2.  **Ensure Your Virtual Environment is Active:**
    If you did the manual backend setup, it should still be active. If you ran `setup.sh`, you'll need to activate it now:
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\\Scripts\\activate`
3.  **Run the Download Script:**
    ```bash
    python scripts/download_models.py
    ```
    This script connects to Hugging Face (or other model repositories) and downloads the pre-trained models (like CodeBERT and CodeT5) specified in the script. This might take a few minutes depending on your internet speed, as these models can be hefty. Grab a coffee!
    *Default models downloaded typically include `microsoft/codebert-base` and `Salesforce/codet5-small`.*
4.  **Return to Root:**
    ```bash
    cd ..
    ```

### Configuring Your Universe: Environment Variables

Environment variables let you customize some core settings without digging into the code.

*   **Frontend (`.env.local` in the project root):**
    Create this file if it doesn't exist.
    ```env
    NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
    NEXT_PUBLIC_APP_NAME="CogniCode Agent"
    ```
    *   `NEXT_PUBLIC_BACKEND_URL`: Tells your browser where to find the Python backend. Crucial!
    *   `NEXT_PUBLIC_APP_NAME`: Just a display name, feel free to personalize.

*   **Backend (`.env` in the `server/` directory):**
    Create this file inside `server/` if it's not there.
    ```env
    FLASK_ENV=development
    PORT=5000
    # MODELS_PATH=./models # Usually defaults correctly
    # USE_DEMO_MODE=true # If you want demo behavior
    # LOG_LEVEL=INFO
    # SECRET_KEY=your_very_secret_flask_key # Important for security if exposed
    ```
    *   `FLASK_ENV`: `development` gives more debug info; `production` is for optimized running.
    *   `PORT`: Which port the Python backend listens on. Must match the frontend's `NEXT_PUBLIC_BACKEND_URL`.
    *   `MODELS_PATH`: Where the AI models are stored. The `download_models.py` script and backend usually handle this, but you can override it.
    *   `SECRET_KEY`: Change this to a long, random string if you ever plan to expose the backend beyond your local machine (not recommended for standard use).

##🚀 Installation & First Run: Igniting the Engines!

With setup and configuration complete, it's time for liftoff!

### Using the Development Script (Recommended for Local Dev - `start-dev.sh`)

The easiest way to get both frontend and backend running together is with our development script. From the project root:
```bash
chmod +x start-dev.sh # Ensure it's executable first time
./start-dev.sh
```
This script (its exact name confirmed from `ls` output, `start-dev.sh`) does the heavy lifting:
*   🚀 Starts the backend Flask server (typically on `http://localhost:5000` or the port you set in `server/.env`).
*   🎨 Starts the Next.js frontend development server (typically on `http://localhost:3000`).
You'll see log outputs from both servers in your terminal.

### Manual Service Start (The Dual-Control Approach)

If you prefer more control or need to debug services independently, start them in separate terminals:

*   **Terminal 1: Backend Server (The Engine Room)**
    ```bash
    cd server
    source venv/bin/activate # Or venv\Scripts\activate on Windows
    python app.py
    ```
    Watch for messages like "Running on http://0.0.0.0:5000/" (port may vary).

*   **Terminal 2: Frontend Server (The Command Deck)**
    In the project root directory:
    ```bash
    npm run dev
    ```
    Watch for messages like "ready - started server on 0.0.0.0:3000".

## ✨ Quick Start: Your First Analysis - "Hello, CogniCode!"

The moment of truth! Let's see CogniCode Agent in action.

1.  **Open Your Browser:** Navigate to `http://localhost:3000` (or the port your frontend is running on).
2.  **Behold the Interface:** You should be greeted by the CogniCode Agent dashboard. Take a moment to admire the sleek design – your new coding co-pilot's cockpit!
3.  **The Code Editor:** Spot the main code input area. That's the Monaco Editor, ready for your code.
4.  **Choose Your Language:** Use the dropdown menu to select the programming language of the code you're about to analyze (e.g., JavaScript, Python).
5.  **Write or Paste Code:** Let's give it a classic, slightly sub-optimal JavaScript Fibonacci function. This function is a good test case because it has a clear performance issue for larger numbers.
    ```javascript
    function fibonacci(n) {
      // This is a comment explaining the base case: F(0)=0, F(1)=1
      if (n <= 1) {
        return n;
      }
      // This is the recursive step, which can be very slow for large 'n'
      // due to repeated calculations. An AI might spot this!
      return fibonacci(n - 1) + fibonacci(n - 2);
    }

    console.log(fibonacci(10)); // Let's calculate the 10th Fibonacci number!
    ```
6.  **Click "Analyze":** Find the "Analyze" button (or similar) and click it. This sends your code to the local backend for processing. Watch as the gears start turning!
7.  **Review the Results:** The magic unfolds in the results panel, likely organized into tabs:
    *   **Analysis Tab:** Expect to see insights about your code. For our Fibonacci example, it might flag the potential performance issue due to recursion. It could also comment on style or find minor bugs if any were present.
    *   **Refactor Tab:** Here, AI-powered suggestions might appear. For Fibonacci, it might suggest using memoization or an iterative approach to improve performance.
    *   **Tests Tab:** CogniCode Agent might generate some unit tests for your `fibonacci` function, covering base cases and perhaps a recursive step.

**Congratulations!** You've successfully performed your first code analysis with CogniCode Agent. You've taken your first step into a larger world of AI-assisted development. This is just a glimpse of its capabilities!

## 🔧 Troubleshooting First Run Issues: When Gremlins Appear

Even in the best systems, sometimes gremlins try to throw a wrench in the works. Here are a few common culprits and their fixes:

*   **"Port already in use" error:**
    *   **Problem:** Another application is using the port CogniCode Agent needs (e.g., 3000 for frontend, 5000 for backend).
    *   **Solution:** Stop the other application, or change the port for CogniCode Agent in `.env.local` (for frontend) or `server/.env` (for backend) and restart.
*   **`python` or `node` command not found:**
    *   **Problem:** Python or Node.js might not be installed correctly or not available in your system's PATH.
    *   **Solution:** Revisit the Prerequisites section and ensure they are installed and accessible from your terminal.
*   **AI Model download fails:**
    *   **Problem:** Network issues, Hugging Face connectivity problems, or insufficient disk space.
    *   **Solution:** Check your internet connection. Ensure you have enough disk space. Try running `python server/scripts/download_models.py` again. If issues persist, check the script for specific model URLs and try accessing them in your browser.
*   **Frontend shows "Cannot connect to backend" or similar:**
    *   **Problem:** The backend server might not be running, or the `NEXT_PUBLIC_BACKEND_URL` in `.env.local` is incorrect.
    *   **Solution:** Ensure the backend (`python app.py` or via `start-dev.sh`) is running and shows no errors. Double-check the URL and port in `.env.local`.
*   **Errors related to Python virtual environment (`venv`):**
    *   **Problem:** `venv` not activated, or dependencies not installed correctly within the `venv`.
    *   **Solution:** Make sure you activate the `venv` (`source server/venv/bin/activate` or `server\\venv\\Scripts\\activate`) before running backend scripts or `pip install`. Re-run `pip install -r server/requirements.txt` within the active `venv`.

If you encounter an issue not listed here, check the terminal logs for detailed error messages. These often provide clues. If you're stuck, don't hesitate to raise an issue on our [GitHub Issues Page](https://github.com/Edmon02/cognicode-agent/issues)!

---
Next: [Architecture Deep Dive](architecture.md)
