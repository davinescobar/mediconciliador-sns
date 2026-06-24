---
name: validate-mcp
description: |
  Validates the MCP Server requirement for the Kaggle capstone.
  Trigger when asked to audit, validate or review the MCP implementation.
  Use before Kaggle submission to confirm all best practices from Day 2 are met.
source: Day 2 (MCP tools and interoperability), Day 5 (MCP server implementation)
---

# Validation: MCP Server

## What the whitepaper requires (Day 2 + Day 5)

- MCP server exposing data tools (FastMCP or raw `mcp.server.Server`)
- Read-only mode enforced — no INSERT/UPDATE/DELETE at the transport layer
- No hardcoded credentials in the server
- Server scoped to a specific project (not a generic proxy)
- Tools must have clear descriptions for LLM discovery
- Day 5 pattern: `mcp_client.py` demonstrates `StdioServerParameters` connection

## Checklist — files to inspect

- [ ] `mcp/mcp_server.py` — FastMCP, tool definitions, read-only enforcement
- [ ] `mcp/mcp_client.py` — client connecting via StdioServerParameters
- [ ] `agents/discharge_parser_agent.py` — McpToolset wiring

## Current status (as of 2026-06-24)

| Element | File | Status |
|---------|------|--------|
| MCP server (FastMCP) | mcp/mcp_server.py | ✅ |
| 9 read-only tools | mcp/mcp_server.py | ✅ |
| SELECT-only enforcement | mcp/mcp_server.py | ✅ |
| No hardcoded credentials | mcp/mcp_server.py | ✅ |
| Project-scoped tools | mcp/mcp_server.py | ✅ |
| Tool descriptions | mcp/mcp_server.py | ✅ |
| MCP client | mcp/mcp_client.py | ✅ |
| MCPToolset in agent | discharge_parser_agent.py | ✅ |

## Status: FULLY COVERED

No gaps. All Day 2 best practices implemented:
- Read-only: enforced via SELECT-only queries
- No credentials: SQLite file path only, no API keys
- Project-scoped: tools return only mediconciliador synthetic data
