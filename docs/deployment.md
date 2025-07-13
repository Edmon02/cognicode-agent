# 8. Deployment & Maintenance: Taking CogniCode Agent Live (and Keeping it Healthy)

CogniCode Agent is, at its heart, a **privacy-first local tool**. Its primary design revolves around running both the frontend and the AI-powered backend directly on your development machine. This ensures your code never leaves your control. However, we understand that development environments and needs can vary. This section will cover the recommended local deployment, how to use Docker for a more isolated or consistent setup, and briefly touch upon considerations for cloud deployment (with strong caveats). We'll also guide you through ongoing maintenance to keep your CogniCode Agent instance purring.

## 🚀 Deployment Strategies: Choosing Your Path

Your deployment strategy will largely depend on your specific use case and comfort level.

1.  **Local First (Highly Recommended for Most Users):**
    *   **The Why:** This is the simplest, most secure, and most privacy-preserving way to use CogniCode Agent. It aligns perfectly with our core philosophy.
    *   **The How:** You run both the Next.js frontend and the Python Flask backend on your local machine. The `start-dev.sh` script (or its equivalent like `run-dev.sh` mentioned in the main README) is specifically designed for this, launching both services concurrently for a seamless development experience.
    *   **Analogy:** Think of it as having your personal AI coding assistant sitting right next to you at your desk, using only your computer's resources.

2.  **Containerized Deployment (Docker): Power User / Consistent Environments:**
    *   **The Why:** Docker provides containerization, packaging the application and its dependencies into isolated environments. This is excellent for:
        *   Ensuring consistency if you move between different machines.
        *   Running the backend as a distinct, managed service locally if you prefer.
        *   A stepping stone if you were to consider deploying parts of it to a private, controlled server environment (though this moves away from the "local-first" privacy model for the backend).
    *   **The How:** We provide `Dockerfile.frontend`, `server/Dockerfile`, and a `docker-compose.yml` to orchestrate this.

3.  **Cloud Deployment (Frontend Only - A Common Scenario):**
    *   **The Why:** The Next.js frontend, being a standard web application, is perfectly suited for deployment on modern web hosting platforms.
    *   **The How:** Platforms like Vercel (by the creators of Next.js), Netlify, or even GitHub Pages (for fully static exports, though our app has dynamic elements) make deploying the frontend incredibly easy, often with direct Git integration.
    *   **Crucial Note:** If you deploy the frontend to the cloud, it will still need to connect to a backend. For CogniCode Agent's privacy model to hold, this backend should ideally still be your *local* backend. This requires exposing your local backend to the internet (e.g., using ngrok or a similar tunneling service, or configuring your router) which comes with its own security considerations.

4.  **Cloud Deployment (Backend - Advanced, Use with Extreme Caution & Full Awareness):**
    *   **The Why:** The *only* reason to consider this is if you are building a *team-internal* version of CogniCode Agent within a highly secure, private cloud environment, and you fully understand the implications.
    *   **The How:** This would involve containerizing the backend (using `server/Dockerfile`) and deploying it to a service like AWS ECS, Google Cloud Run, or Azure Container Instances.
    *   **Critical Caveats (Reiterated from Architecture):**
        *   **Privacy Lost (for team members):** If multiple users send their code to a centralized cloud backend, the "code never leaves *your* machine" principle is broken for those users. This is a fundamental shift from the project's primary design.
        *   **Security:** You become responsible for securing the API, authenticating users, authorizing access, and protecting code in transit and potentially at rest.
        *   **Resource Costs:** AI models are resource-hungry. Running them in the cloud can be expensive.
        *   **Model Management:** Storing and accessing large AI models in the cloud needs careful planning.
    *   **In short: This path is not recommended for the standard, privacy-focused use of CogniCode Agent.**

## 🐳 Deploying with Docker: Your App in a Box!

Docker is a fantastic tool for creating consistent and isolated environments. CogniCode Agent comes ready with Docker configurations to get you up and running smoothly.

### The Cast: `Dockerfile.frontend`, `server/Dockerfile`, `docker-compose.yml`

*   **`Dockerfile.frontend`**: This is the recipe for building the Next.js frontend container image.
    ```dockerfile
    # Use an official Node.js 18 image (Alpine for smaller size)
    FROM node:18-alpine

    # Set the working directory inside the container
    WORKDIR /app

    # Copy package.json and package-lock.json (or bun.lockb) first
    # This leverages Docker's layer caching: dependencies are only re-installed if these files change.
    COPY package*.json ./
    # COPY bun.lockb ./ # If using Bun

    # Install dependencies (using npm ci for cleaner installs from lock file)
    RUN npm ci
    # RUN bun install # If using Bun

    # Copy the rest of the application code into the container
    COPY . .

    # Build the Next.js application for production
    RUN npm run build

    # Expose the port the Next.js app will run on (usually 3000)
    EXPOSE 3000

    # The command to start the application when the container launches
    CMD ["npm", "start"]
    ```
    *   **Story of the Frontend Dockerfile:** It starts with a lean Node.js base, sets up a workspace, efficiently installs dependencies by copying lockfiles first, then copies all source code, builds the Next.js app for production, and finally specifies how to run the production server.

*   **`server/Dockerfile`**: This is the blueprint for our Python Flask backend container.
    ```dockerfile
    # Use an official Python 3.9 slim image (good balance of size and features)
    FROM python:3.9-slim

    # Set the working directory inside the container
    WORKDIR /app

    # Install system dependencies (gcc/g++ might be needed for some Python packages)
    RUN apt-get update && apt-get install -y \
        gcc \
        g++ \
        && rm -rf /var/lib/apt/lists/* # Clean up apt cache to reduce image size

    # Copy the requirements file first for Docker layer caching
    COPY requirements.txt .
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the backend application code
    COPY . .

    # Create the directory where AI models will be stored (if not already present)
    RUN mkdir -p /app/models
    # Note: Models themselves are best managed via volumes, not baked into the image due to size.

    # Expose the port the Flask app will run on (usually 5000 or 8000)
    EXPOSE 5000

    # Set the PYTHONPATH environment variable so Python can find our modules
    ENV PYTHONPATH=/app

    # Health check: Periodically checks if the /health endpoint is responsive
    HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
        CMD curl -f http://localhost:8000/health || exit 1
        # Note: Port in HEALTHCHECK should match the internal port the app runs on (e.g., 5000 or 8000)

    # The command to start the backend application
    CMD ["python", "app.py"]
    # For a more production-ready setup, you might use Gunicorn:
    # CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
    ```
    *   **Story of the Backend Dockerfile:** It starts with a Python base, installs necessary system build tools, efficiently installs Python packages, copies the backend code, and sets up the environment. The `HEALTHCHECK` instruction is a nice touch, allowing Docker to monitor if the application is running correctly. The `CMD` currently uses `python app.py`, suitable for development; for production, using a proper WSGI server like Gunicorn (as commented) is recommended.

*   **`docker-compose.yml`**: This is the conductor for our multi-container orchestra. It defines how our frontend and backend services run together.
    ```yaml
    version: '3.8' # Specifies the Docker Compose file format version

    services:
      # Frontend Service (Next.js)
      frontend:
        build:
          context: . # Build context is the project root
          dockerfile: Dockerfile.frontend # Specifies the Dockerfile to use
        ports:
          - "3000:3000" # Maps port 3000 on the host to port 3000 in the container
        environment:
          # Tells the frontend container where to find the backend.
          # 'backend' is the service name of our backend container within Docker's network.
          - NEXT_PUBLIC_BACKEND_URL=http://backend:5000
        depends_on:
          - backend # Ensures the backend service starts before the frontend attempts to connect
        volumes:
          # Mounts the current directory on the host to /app in the container.
          # Great for development: changes on host are reflected in container.
          - ./:/app
          # Anonymous volume to persist node_modules, avoiding re-installation on every start
          # if the host node_modules is accidentally mapped over.
          - /app/node_modules
        command: npm run dev # Runs the Next.js development server

      # Backend Service (Flask)
      backend:
        build:
          context: ./server # Build context is the server/ directory
          dockerfile: Dockerfile # Uses server/Dockerfile
        ports:
          - "5000:5000" # Maps port 5000 on host to port 5000 in container
                        # (Ensure this matches the port Flask listens on, e.g., 8000 if AppConfig default is used)
        environment:
          - FLASK_ENV=development
          - PYTHONPATH=/app # Ensures Python can find modules within /app in the container
        volumes:
          - ./server:/app # Mounts host's server/ to /app in container for live code changes
          - ./models:/app/models # Mounts host's ./models to /app/models in container
                                 # This is how downloaded models are made available to the backend.
        command: python app.py # Runs the Flask development server

      # Model Downloader Service (One-time setup)
      model-setup:
        build:
          context: ./server
          dockerfile: Dockerfile # Uses the same backend image
        volumes:
          - ./models:/app/models # Mounts the models volume
        # Runs the download script. This service will run, execute the command, and then exit.
        command: python scripts/download_models.py
        profiles:
          - setup # This service only runs if the 'setup' profile is activated
                  # e.g., docker-compose --profile setup up

    volumes: # Defines a named volume for models
      models:
        driver: local # Uses the local driver, meaning data is stored on the host machine
    ```
    *   **Story of Docker Compose:** It defines three services: `frontend`, `backend`, and a utility `model-setup`.
        *   `frontend` and `backend` services build their respective Docker images.
        *   **Ports:** Critical for accessing the services from your host machine. `3000:3000` means your local port 3000 maps to the container's port 3000. *Ensure the backend port mapping matches what `app.py` actually listens on (e.g., if `AppConfig` defaults to 8000, it should be `"8000:8000"` or the `PORT` env var should be set to 5000 in the compose file for the backend).*
        *   **Environment Variables:** `NEXT_PUBLIC_BACKEND_URL=http://backend:5000` for the frontend is key. Docker Compose creates an internal network where services can reach each other by their service name (`backend` in this case) and internal port (`5000`).
        *   **`depends_on`:** The `frontend` `depends_on: - backend` tells Docker Compose to start the `backend` service before starting the `frontend`.
        *   **Volumes:** These are super important for development.
            *   `./:/app` (frontend) and `./server:/app` (backend) mount your local source code directly into the containers. This means changes you make to your code on your host machine are immediately reflected inside the running containers, enabling hot reloading for both Next.js and (if configured) Flask.
            *   `/app/node_modules` (frontend) is an anonymous volume trick. It prevents your host `node_modules` (if any) from overwriting the `node_modules` installed *inside* the container during the `RUN npm ci` step of the Dockerfile build. This is good practice.
            *   `./models:/app/models` (backend and model-setup) ensures that the `models` directory (which should be in your `.gitignore` if models are large) is shared between the host and the containers. The `model-setup` service uses this to download models onto this volume, and the `backend` service then reads them from there.
        *   **`command`:** Specifies the command to run when the service container starts (e.g., `npm run dev` or `python app.py`).
        *   **`model-setup` service & `profiles`:** This is a neat way to handle one-time setup tasks. The `model-setup` service is only run if you explicitly activate the `setup` profile (e.g., `docker-compose --profile setup up`). It runs `scripts/download_models.py` to populate the shared `models` volume.
        *   **`volumes: models: driver: local`:** Defines a named Docker volume called `models`. This ensures that downloaded models persist even if containers are removed and recreated.

### Building & Running with Docker Compose:
The main `README.md` provides the command:
```bash
# From the project root
docker-compose up --build
```
*   **`--build`**: Forces Docker Compose to rebuild the images if their Dockerfiles or build contexts have changed. Good to use when you've made changes to `Dockerfile` or related files.
*   **Accessing:** Once up, the frontend should be accessible at `http://localhost:3000` and the backend at `http://localhost:5000` (or whatever port you've configured and mapped for the backend).
*   **To run model setup first (if needed):**
    ```bash
    docker-compose --profile setup up -d model-setup
    # Wait for it to complete (check logs: docker-compose logs model-setup)
    docker-compose up --build
    ```

### Building Individual Services:
As noted in the draft and main `README.md`:
*   **Frontend:** `docker build -t cognicode-frontend .`
*   **Backend:** `docker build -t cognicode-backend ./server`
These commands build the Docker images and tag them, but `docker-compose` is generally preferred for managing the multi-service application.

## ☁️ Cloud Deployment Examples (Brief Recap & Context)

As emphasized, CogniCode Agent is primarily local. But for completeness:

### Frontend to Vercel (or Netlify, etc.):
Platforms like Vercel are excellent for Next.js frontends.
1.  Push your code to a Git provider (GitHub, GitLab, Bitbucket).
2.  Connect this Git repository to Vercel.
3.  Configure Vercel build settings (usually auto-detected).
4.  **Crucially, set the `NEXT_PUBLIC_BACKEND_URL` environment variable in Vercel's project settings.** This URL must point to wherever your backend is accessible. If your backend is still local while the frontend is on Vercel, you'll need a tunneling service like `ngrok` to expose your local backend to the internet (use with caution and secure your tunnel).
5.  Deploy. Vercel handles the build and hosting.

### Backend to Cloud (Private/Controlled Environments Only):
If deploying the backend (e.g., for a secure internal team tool):
1.  **Containerize:** Use `server/Dockerfile` (consider switching `CMD` to Gunicorn for production).
2.  **Push Image:** Push `cognicode-backend` image to a private container registry (AWS ECR, Google Artifact Registry, Docker Hub private repo).
3.  **Deploy to Cloud Service:**
    *   **Serverless Containers (e.g., Google Cloud Run, AWS App Runner, Azure Container Apps):** Good for stateless applications or if you can manage state (like AI models) externally.
    *   **Container Orchestration (e.g., AWS ECS, Kubernetes - GKE, EKS, AKS):** More complex but offers greater control for stateful applications or those needing persistent storage for models. You'd need to configure persistent volumes for the AI models.
4.  **Critical Considerations (Reiteration is Key!):** Security (network, auth), resource allocation (CPU/GPU for models, memory), cost, and a robust strategy for managing and accessing AI models in the cloud.

## 🛠️ Maintenance & Updates: Keeping Your Agent Sharp

Like any good tool, CogniCode Agent benefits from regular maintenance.

### Keeping CogniCode Agent Up-to-Date:
1.  **Pull Latest Code Changes:**
    ```bash
    git pull origin main # Or the specific branch you're tracking
    ```
2.  **Update Frontend Dependencies:**
    ```bash
    npm install
    ```
    (Or `npm update` if you want to try updating to newer minor/patch versions of dependencies as per your `package.json` constraints. `npm install` is generally safer as it respects `package-lock.json`.)
3.  **Update Backend Dependencies:**
    ```bash
    cd server
    source venv/bin/activate # If using virtual environments
    pip install -r requirements.txt --upgrade
    cd ..
    ```
    The `--upgrade` flag attempts to upgrade already installed packages to their latest allowed versions.
4.  **Re-download or Update AI Models (If Necessary):**
    If the project updates the models it uses, or if you've changed them:
    ```bash
    cd server
    source venv/bin/activate
    python scripts/download_models.py
    cd ..
    ```
5.  **Rebuild Docker Images (If Using Docker):**
    If you've pulled code changes or updated dependencies, you'll need to rebuild your Docker images to include these changes:
    ```bash
    docker-compose up --build -d
    ```
    (The `-d` runs containers in detached mode).

### Monitoring & Logging: Your Window into Operations
*   **Local Development:**
    *   Frontend (Next.js): Logs from `npm run dev` appear in your terminal. Browser developer tools are also essential.
    *   Backend (Flask): Logs from `python app.py` (or via `start-dev.sh`) appear in its terminal. The backend uses our custom logger from `server/utils/logger.py`, so log level and format are configurable via `.env` and the logger setup.
*   **Docker Deployment:**
    *   View logs for a specific service: `docker-compose logs -f <service_name>` (e.g., `docker-compose logs -f backend`). The `-f` flag follows the log output.
    *   View all logs: `docker-compose logs -f`
*   **Cloud Deployment:** Utilize the native logging services of your chosen cloud provider (e.g., AWS CloudWatch, Google Cloud Logging, Azure Monitor). Ensure your Docker containers are configured to send logs to these services.

### Troubleshooting Common Issues (Post-Deployment / General):
*   **Connectivity Issues (Frontend <-> Backend):**
    *   **Symptom:** Frontend loads but shows "Disconnected," analysis fails.
    *   **Checks:**
        *   Is the backend server running? Check its logs.
        *   Is `NEXT_PUBLIC_BACKEND_URL` in the frontend's environment correctly pointing to the backend's host and port?
        *   If using Docker, are port mappings in `docker-compose.yml` correct? Can containers reach each other on Docker's internal network (e.g., `http://backend:PORT`)?
        *   Firewall rules (local or cloud) blocking connections?
*   **AI Model Loading Failures (Backend):**
    *   **Symptom:** Backend starts but analysis fails, logs show errors related to model loading.
    *   **Checks:**
        *   Is `MODELS_PATH` in `server/.env` correct and accessible by the backend process/container?
        *   Were models downloaded correctly by `scripts/download_models.py` into that path?
        *   Are there sufficient permissions to read model files?
        *   Enough disk space and RAM for the models?
*   **Performance Degradation:**
    *   **Symptom:** Analysis is very slow, UI is sluggish.
    *   **Checks:**
        *   System resources (CPU, RAM) on the machine running the backend. AI models are demanding.
        *   Check backend logs for performance metrics from `@log_performance` if applied to relevant functions.
        *   Consider if the code being analyzed is exceptionally large or complex.
        *   For Docker/Cloud: Are container resource limits too low?
*   **Configuration Errors:**
    *   **Symptom:** Unexpected behavior, errors related to missing settings.
    *   **Checks:** Double-check all environment variables in `.env.local` (frontend) and `server/.env` (backend). Ensure they are correctly named and have valid values.
*   **Python/Node Version Incompatibility (Less common with Docker, more for manual setups):**
    *   **Symptom:** Errors during dependency installation or runtime.
    *   **Checks:** Ensure your installed Node.js and Python versions meet the prerequisites mentioned in `README.md`.

This detailed deployment and maintenance guide should equip you to run and manage CogniCode Agent effectively, whether locally or in more complex setups.

---
Next: [Contributing to CogniCode Agent](contributing.md)
