#!/bin/bash
# Run the MCP server with conda env "wework" activated.
# Use this as Claude Desktop command so the server has the right env even when
# Claude was started from the Dock (no conda on PATH).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Set CONDA_ROOT to your conda install if not in a standard place (e.g. export in your shell or edit below)
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda3}"
[[ -d "$CONDA_ROOT" ]] || CONDA_ROOT="$HOME/anaconda3"
[[ -d "$CONDA_ROOT" ]] || CONDA_ROOT="$HOME/opt/miniconda3"
if [[ ! -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]]; then
  echo "Could not find conda at CONDA_ROOT=$CONDA_ROOT. Set CONDA_ROOT or edit this script." >&2
  exit 1
fi
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate wework
exec python run_mcp_server.py
