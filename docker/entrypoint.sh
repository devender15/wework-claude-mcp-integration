#!/bin/bash
set -e

# Start Appium in background
appium --use-plugins=inspector &
sleep 5

# Start MCP server (stdio)
python mcp/server.py
