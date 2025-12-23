

# 🚀 `uv` Command Reference Guide

## 1. Project Initialization

Start a new project or set up the current directory.

- **Create a standard project:**
    
    Bash
    
    ```
    uv init new_app
    ```
    
- Create specific project types:
    
    Use flags to define if you are building an executable application or a reusable library.
    
    Bash
    
    ```
    # Create an application project
    uv init new_app --app
    
    # Create a library project (for Python packages)
    uv init new_app --lib
    ```
    

## 2. Dependency Management

Manage your Python packages and virtual environments.

- Add packages:
    
    (Automatically creates/updates the .venv and uv.lock)
    
    Bash
    
    ```
    uv add flask requests
    ```
    
- **Remove packages:**
    
    Bash
    
    ```
    uv remove flask
    ```
    
- View dependency graph:
    
    See a tree view of installed libraries and their dependencies.
    
    Bash
    
    ```
    uv tree
    ```
    

## 3. Environment Synchronization

Crucial for collaboration or when cloning a repo.

- Sync environment:
    
    Installs everything exactly as defined in uv.lock. This recreates the environment perfectly on a new machine.
    
    Bash
    
    ```
    uv sync
    ```
    

## 4. Running Code

`uv` handles the virtual environment for you automatically.

- Run a script:
    
    Executes the script using the project's environment, even if you deleted the .venv folder (it will recreate it!).
    
    Bash
    
    ```
    uv run main.py
    ```
    

## 5. Global Tools (`uv tool`)

Manage command-line tools (like `ruff`, `black`, `pytest`) globally or temporarily.

- Install a tool permanently:
    
    Makes the tool available globally on your system.
    
    Bash
    
    ```
    uv tool install ruff
    ```
    
- Run a tool (Ephemeral/Temporary):
    
    Download and run a tool once without installing it permanently.
    
    Bash
    
    ```
    # Using 'uv tool run'
    uv tool run ruff check
    
    # Short alias (recommended)
    uvx ruff check
    ```
    
- **Manage installed tools:**
    
    Bash
    
    ```
    # List all installed tools
    uv tool list
    
    # Upgrade all installed tools
    uv tool upgrade --all
    ```
    

## 6. Docker Optimization 🐳

Best practices for using `uv` inside a Dockerfile to maximize caching and build speed.

Dockerfile

```
# 1. Copy the definition files first (enables Docker caching)
COPY pyproject.toml uv.lock ./

# 2. Install dependencies exactly as locked
# --frozen ensures the build fails if the lockfile is out of sync
RUN uv sync --frozen
```

> **💡 Note:** The `--frozen` flag is a great safety check for CI/CD pipelines. It prevents accidental upgrades by ensuring the installed packages match `uv.lock` exactly.

---

### Quick Summary

|**Command**|**Description**|
|---|---|
|**`uv init`**|Scaffolds new projects.|
|**`uv add/remove`**|Manages dependencies and updates the lockfile.|
|**`uv tree`**|Visualizes your dependency graph.|
|**`uv sync`**|Recreates the environment from the lockfile.|
|**`uv run`**|Executes scripts in the managed environment.|
|**`uvx`**|Runs temporary tools without installation.|




## Building streamlit app with uv and docker 

````
# Streamlit App with uv & Docker: A Complete Guide

This guide covers setting up a Python project using `uv`, building a simple Streamlit app, and containerizing it with Docker (including hot-reloading).

## 1. Project Initialization (uv)

First, we create a reproducible project environment.

```bash
# 1. Create a new project application
uv init thank_you_app --app

# 2. Navigate into the folder
cd thank_you_app

# 3. Add Streamlit as a dependency
uv add streamlit
````

## 2. The Application Code

Create a file named `app.py` with the following content:

Python

```
import streamlit as st

st.title("Welcome!")

name = st.text_input("Please enter your name:")

if name:
    st.write(f"Thank you {name}!")
```

## 3. Testing Locally

Run the app locally to ensure it works before Dockerizing.

Bash

```
# Use 'uv run' to execute streamlit within the virtual environment
uv run streamlit run app.py
```

## 4. Docker Setup

### A. The Dockerfile

Create a file named `Dockerfile` (no extension):

Dockerfile

```
# 1. Setup
FROM python:3.12-slim
RUN pip install uv
WORKDIR /app

# 2. Dependencies (Cached!)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 3. Application Code
COPY . .

# 4. Run it
EXPOSE 8501
# Note: server.address=0.0.0.0 is required for Docker
# server.fileWatcherType=poll is required for hot-reloading on some systems
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=poll"]
```

### B. The .dockerignore

Create a file named `.dockerignore` to keep the image small:

Plaintext

```
.venv/
__pycache__/
*.pyc
.git/
```

## 5. Build & Run

### Step 1: Build the Image

Bash

```
docker build -t thank-you-app .
```

### Step 2: Run the Container (Standard)

Bash

```
docker run -p 8501:8501 thank-you-app
```

### Step 3: Run with Hot-Reloading (Dev Mode)

This mounts your local code into the container so changes happen instantly.

**Mac/Linux:**

Bash

```
docker run -p 8501:8501 -v $(pwd):/app -v /app/.venv thank-you-app
```

**Windows (PowerShell):**

PowerShell

```
docker run -p 8501:8501 -v ${PWD}:/app -v /app/.venv thank-you-app
```

_(Note: If hot-reloading fails, use the absolute path instead of `$(pwd)`)_