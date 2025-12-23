📓 Development Notebooks

This folder contains experimental notebooks for developing and testing the Granite Agent.

Setup

These notebooks run inside the jupyter Docker container.
Because the root directory is mounted to /app, you can import modules from the parent folder directly.

Example Import:

import sys
import os

# Add parent directory to path to import agent.py
sys.path.append(os.path.abspath('..'))

from agent import get_agent_executor


Access

If running via Docker Compose:
URL: http://localhost:7799
Token: granite