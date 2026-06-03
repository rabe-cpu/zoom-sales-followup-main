#!/usr/bin/env python3
"""Stop hook gate for sales follow-up email tasks.

Claude Code hooks receive a JSON payload on stdin. This gate is intentionally
conservative: it only blocks when the transcript/email task keywords are visible
and the final response lacks evidence that the required pipeline ran.
"""

from __future__ import annotations

import json
import sys
from typing import Any


SALES_TASK_KEYWORDS = [
    "営業後送付メール",
    "営業送付メール",
    "商談",
    "文字起こし",
    "MTG",
    "Zoom",
    "JamRoll",
]

REQUIRED_MARKERS = [
    ("Skill Used Check", ["Skill Used Check", "Skills:"]),
    ("orchestrator Skill", ["sales-followup-email-from-transcript"]),
    ("transcript analysis Skill", ["sales-transcript-intake-analysis"]),
    ("seasonal research Skill", ["sales-seasonal-greeting-research", "季語"]),
    ("email writing Skill", ["sales-followup-email-writing"]),
    ("evaluation Skill", ["sales-followup-email-evaluation", "評価エージェント"]),
    ("repair loop evidence", ["Repair loop", "改善ログ", "修正有無"]),
    ("orchestration evidence", ["Orchestration log", "subagents", "same-AI roles", "サブエージェント"]),
    ("output quality gate", ["Output quality gate", "顧客送付用", "出力失敗パターン"]),
    ("Knowledge or CLAUDE.md", ["knowledge/", "CLAUDE.md", "ナレッジ"]),
    ("Final-Whole-Check", ["Final-Whole-Check"]),
    ("remaining risk", ["残リスク", "remaining risk", "リスク"]),
]

WORD_MARKERS = ["Word", "ワード", ".docx", "黄色", "ZOOM URL"]


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"{key}: {flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "\n".join(flatten(item) for item in value)
    return "" if value is None else str(value)


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
        text = flatten(payload)
    except json.JSONDecodeError:
        text = raw

    if not any(keyword in text for keyword in SALES_TASK_KEYWORDS):
        return 0

    missing = [
        label
        for label, markers in REQUIRED_MARKERS
        if not any(marker in text for marker in markers)
    ]

    if any(marker in text for marker in WORD_MARKERS):
        if "sales-followup-word-output" not in text:
            missing.append("Word output Skill")

    if missing:
        sys.stderr.write(
            "Missing required sales follow-up completion evidence: "
            + ", ".join(missing)
            + "\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
