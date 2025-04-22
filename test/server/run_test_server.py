#!/usr/bin/env python3
"""Wrapper script to run the test server with proper Python path setup."""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from test.server.test_server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="error") 