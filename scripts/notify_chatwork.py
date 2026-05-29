#!/usr/bin/env python3
"""
notify_chatwork.py - 処理結果をChatwork通知（Routine Step4）
============================================================
3つの通知パターン:
  --results <JSONファイル or JSON文字列>  … 完了通知（件数・評価・Docs URL）
  --empty                                 … 処理対象0件の通知
  --error  "<メッセージ>"                  … エラー通知

results JSON の想定形（save_to_gdrive.py の出力を集約したもの）:
  {"results": [{"customer_name","host_email","evaluation_summary","customer_url","internal_url","gmail_draft_id"}, ...],
   "warnings": ["...", ...]}

必要な環境変数: CHATWORK_API_TOKEN / CHATWORK_ROOM_ID
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

CHATWORK_API = "https://api.chatwork.com/v2"


def send(message: str) -> None:
    token = os.environ["CHATWORK_API_TOKEN"]
    room_id = os.environ["CHATWORK_ROOM_ID"]
    resp = requests.post(
        f"{CHATWORK_API}/rooms/{room_id}/messages",
        headers={"X-ChatWorkToken": token},
        data={"body": message},
        timeout=30,
    )
    if resp.status_code != 200:
        sys.stderr.write(f"Chatwork通知失敗 {resp.status_code}: {resp.text}\n")
        sys.exit(1)


def build_completion_message(results: list, warnings: list) -> str:
    # Webhook版 lib/notifier.js の notifySuccess フォーマットに合わせる
    lines = [f"[info][title]✅ 営業フォローメール自動生成完了（{len(results)}件）[/title]"]
    for r in results:
        topic = r.get("topic") or r.get("customer_name", "")
        lines.append(f"商談: {topic}（{r.get('host_email', '')}、{r.get('duration_min', '')}分）")
        lines.append(f"評価: {r.get('evaluation_summary') or '6エージェント合格'}")
        lines.append("")
        lines.append("📄 顧客送付用:")
        lines.append(r.get("customer_url", ""))
        lines.append("📋 社内確認用:")
        lines.append(r.get("internal_url", ""))
        draft_id = r.get("gmail_draft_id")
        if draft_id:
            lines.append("✉️ Gmail下書き:")
            auth_mode = r.get("gmail_auth_mode")
            suffix = f" / {auth_mode}" if auth_mode else ""
            lines.append(f"{r.get('gmail_user') or r.get('host_email', '')} / draft_id: {draft_id}{suffix}")
        lines.append("")
        lines.append("⚠️ 営業確認必須:")
        risks = r.get("remaining_risks")
        if risks:
            for risk in (risks if isinstance(risks, list) else [risks]):
                lines.append(f"・{risk}")
        else:
            lines.append("・PDFのURL差し替え")
            lines.append("・次回ZOOM URL日程確定後追記")
        lines.append("")
    if warnings:
        lines.append("■ エラー・警告")
        for w in warnings:
            lines.append(f"・{w}")
    lines.append("[/info]")
    return "\n".join(lines)


def _load_results(raw: str):
    if raw and os.path.exists(raw):
        raw = Path(raw).read_text(encoding="utf-8")
    data = json.loads(raw)
    results = data.get("results", data.get("unprocessed", []))
    warnings = data.get("warnings", [])
    return results, warnings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", help="結果JSONファイルのパス or JSON文字列")
    ap.add_argument("--empty", action="store_true", help="処理対象0件の通知")
    ap.add_argument("--error", help="エラーメッセージ")
    args = ap.parse_args()

    if args.error:
        send(f"[info][title]営業フォローメール 自動生成 エラー[/title]{args.error}[/info]")
        return
    if args.empty:
        send("[info][title]営業フォローメール 自動生成[/title]処理対象の商談はありませんでした。[/info]")
        return

    results, warnings = _load_results(args.results or "{}")
    send(build_completion_message(results, warnings))


if __name__ == "__main__":
    main()
