"""
ADK-native observability callbacks for MediConciliador SNS.

Demonstrates Day 4a of the Kaggle 5-day agents course: agent observability
using ADK's built-in callback hooks (before_tool_callback, after_tool_callback)
instead of custom instrumentation.

Usage:
    from agents.callbacks import before_tool_log, after_tool_log

    agent = LlmAgent(
        ...
        before_tool_callback=before_tool_log,
        after_tool_callback=after_tool_log,
    )

The callbacks write structured JSON lines to stderr so they are visible in
the terminal during a demo run without polluting stdout (which carries the
agent's output).
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any


def before_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
) -> dict | None:
    """Called by ADK before each tool invocation. Returns None to let the tool run."""
    entry = {
        "event": "tool_start",
        "tool": getattr(tool, "name", str(tool)),
        "args": {k: str(v)[:120] for k, v in args.items()},
        "agent": getattr(tool_context, "agent_name", "unknown"),
        "t": time.time(),
    }
    print(json.dumps(entry, ensure_ascii=False), file=sys.stderr)
    return None


def after_tool_log(
    tool: Any,
    args: dict[str, Any],
    tool_context: Any,
    tool_response: dict,
) -> dict | None:
    """Called by ADK after each tool invocation. Returns None to keep original response."""
    result_preview = str(tool_response)[:200] if tool_response else ""
    entry = {
        "event": "tool_end",
        "tool": getattr(tool, "name", str(tool)),
        "ok": tool_response is not None,
        "preview": result_preview,
        "t": time.time(),
    }
    print(json.dumps(entry, ensure_ascii=False), file=sys.stderr)
    return None
