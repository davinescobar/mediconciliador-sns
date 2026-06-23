"""
MCP Client — MediConciliador SNS

Provides server parameters for ADK's MCPToolset integration.
Trace-logging wrapper wired in Session 3 when agents are connected.

Usage (Session 3):
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp.mcp_client import get_mcp_server_params

    tools, exit_stack = await MCPToolset.from_server(get_mcp_server_params())
"""

from pathlib import Path

from mcp.client.stdio import StdioServerParameters

SERVER_PATH = Path(__file__).parent / "mcp_server.py"


def get_mcp_server_params() -> StdioServerParameters:
    """Returns StdioServerParameters for use with ADK's MCPToolset."""
    return StdioServerParameters(
        command="python",
        args=[str(SERVER_PATH)],
    )
