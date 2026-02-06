# Ensure project root is on path so imports work even when Claude runs with a different cwd
import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from mcp.server.fastmcp import FastMCP
from app_mcp.tools.wework import book_wework_desks

mcp = FastMCP("Personal Automation Suite", json_response=True)

@mcp.tool()
def wework_book_desks(
    dates: list[str],
    building: str
) -> str:
    return book_wework_desks(dates, building)

if __name__ == "__main__":
    try:
        mcp.run(transport="stdio")
    except TypeError:
        # Older MCP SDK may not accept transport=
        mcp.run()
