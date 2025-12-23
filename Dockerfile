# Use a lightweight Python base image
FROM python:3.11-slim-bookworm

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory
WORKDIR /app

# Copy dependency files first to leverage cache
COPY pyproject.toml ./

# Install dependencies into the system python (no venv needed in container)
# We use --system because the container itself is an isolated environment
RUN uv pip install --system -r pyproject.toml

# Copy the application code
# Note: .dockerignore will exclude .env and .venv
COPY . .

# Expose the Streamlit port
EXPOSE 7777

# Set healthcheck
HEALTHCHECK CMD curl --fail http://localhost:7777/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=7777", "--server.address=0.0.0.0"]