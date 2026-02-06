#!/usr/bin/env python3
"""
Launcher for the MCP server. Run this from the project root so that
Claude Desktop can start the server even when its cwd is not set correctly.

Usage:
  python3 run_mcp_server.py

With conda env "wework" (for Claude config use conda run; for manual testing keep stdin open):
  Claude:  conda run -n wework python /path/to/run_mcp_server.py
  Terminal test:  conda activate wework && python run_mcp_server.py
  (Without a connected stdin the server exits; Claude attaches stdin when it starts the process.)

Or from any directory with full path:
  python3 /path/to/wework-automate/run_mcp_server.py
"""
import os
import sys

# Ensure project root is on path (this script lives at project root)
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Run the MCP server module
import runpy
runpy.run_path(os.path.join(_project_root, "app_mcp", "server.py"), run_name="__main__")
