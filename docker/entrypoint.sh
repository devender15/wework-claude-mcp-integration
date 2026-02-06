#!/bin/bash
set -e

# Start Appium only if port 4723 is free (avoid EADDRINUSE when another container/process already has it)
if python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect(('127.0.0.1', 4723))
    s.close()
    exit(0)   # port in use
except (socket.error, OSError):
    exit(1)   # port free
" 2>/dev/null; then
    echo "[entrypoint] Port 4723 already in use, using existing Appium" >> /tmp/appium.log
else
    # Run Appium in a subshell with all output to file so nothing leaks to stdout (MCP uses stdout for JSON)
    ( appium --use-plugins=inspector 0</dev/null >>/tmp/appium.log 2>&1 ) &
    sleep 5
fi

# Start MCP server (stdio); run as module so app_mcp is on path
python -m app_mcp.server
