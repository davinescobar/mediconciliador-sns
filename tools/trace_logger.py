"""Execution trace logger — records tool calls during a reconciliation run."""

import json
from datetime import datetime, timezone


class TraceLogger:
    def __init__(self) -> None:
        self._trace: list[dict] = []

    def log(self, tool: str, args: dict | None = None, result_summary: str = "") -> None:
        self._trace.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "args": args or {},
            "result_summary": result_summary,
        })

    def get(self) -> list[dict]:
        return list(self._trace)

    def as_json(self) -> str:
        return json.dumps(self._trace, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        self._trace.clear()


_default_logger = TraceLogger()


def log_tool_call(tool: str, args: dict | None = None, result_summary: str = "") -> None:
    _default_logger.log(tool, args, result_summary)


def get_trace() -> list[dict]:
    return _default_logger.get()


def get_trace_json() -> str:
    return _default_logger.as_json()


def clear_trace() -> None:
    _default_logger.clear()
