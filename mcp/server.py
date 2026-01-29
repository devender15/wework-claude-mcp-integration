from mcp.server.mcpserver import MCPServer
from mcp.tools.wework import book_wework_desks

mcp = MCPServer("Personal Automation Suite")

@mcp.tool()
def wework_book_desks(
    dates: list[str],
    building: str
) -> str:
    return book_wework_desks(dates, building)

if __name__ == "__main__":
    mcp.run()
