"""
Prompt injection detection for user-supplied clinical documents.

sanitize_document  — checks text for injection patterns and returns a
                     SanitizationResult with warnings and a sanitized copy.
"""

import re
from dataclasses import dataclass, field

_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(previous|all|prior|above)\s+(instructions?|prompts?|context)", "instruction override"),
    (r"forget\s+(everything|all|previous|prior|what)\s+(you|i|was)", "context erasure"),
    (r"you\s+are\s+now\s+a?\s*\w+", "identity reassignment"),
    (r"act\s+as\s+(if\s+you\s+are|a|an)\s+\w+", "role injection"),
    (r"<\s*system\s*>", "system tag injection"),
    (r"<\s*/?INST\s*>", "instruction tag injection"),
    (r"\[SYSTEM\]", "system bracket injection"),
    (r"developer\s+mode", "developer mode trigger"),
    (r"jailbreak", "jailbreak attempt"),
    (r"DAN\b", "DAN jailbreak"),
    (r"do\s+anything\s+now", "DAN jailbreak"),
    (r"pretend\s+(you\s+are|to\s+be)\s+\w+", "identity pretend"),
    (r"new\s+persona", "persona injection"),
    (r"disregard\s+(your\s+)?(previous|prior|original)\s+(instructions?|training|guidelines?)", "guideline override"),
    (r"reveal\s+(your\s+)?(system\s+prompt|instructions?|context)", "prompt extraction"),
    (r"print\s+your\s+(system\s+prompt|instructions?|full\s+prompt)", "prompt extraction"),
    (r"translate\s+.*\s+into\s+.*\s+and\s+execute", "execution injection"),
    (r"execute\s+this\s+code", "code execution injection"),
]

_COMPILED = [(re.compile(pat, re.IGNORECASE), label) for pat, label in _PATTERNS]


@dataclass
class SanitizationResult:
    is_clean: bool
    warnings: list[str] = field(default_factory=list)
    sanitized_text: str = ""


def sanitize_document(text: str) -> SanitizationResult:
    """
    Scans text for prompt injection patterns.

    Returns a SanitizationResult:
    - is_clean: True if no patterns detected
    - warnings: list of human-readable warning strings
    - sanitized_text: original text (content is never silently altered —
                      the caller decides whether to proceed or block)
    """
    warnings = []
    for pattern, label in _COMPILED:
        match = pattern.search(text)
        if match:
            snippet = text[max(0, match.start() - 20):match.end() + 20].strip()
            warnings.append(f"[{label}] detectado: «...{snippet}...»")

    return SanitizationResult(
        is_clean=len(warnings) == 0,
        warnings=warnings,
        sanitized_text=text,
    )
