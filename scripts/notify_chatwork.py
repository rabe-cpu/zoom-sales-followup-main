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
任意の環境変数:
  CHATWORK_ACCOUNT_ID_BY_HOST={"sales@example.com":"123456"}
  CHATWORK_ACCOUNT_ID_BY_SALES_PERSON={"森田":"123456","松谷":"234567"}
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

CHATWORK_API = "https://api.chatwork.com/v2"


def _load_json_mapping(env_name: str, lower_keys: bool = False) -> dict[str, str]:
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    result = {}
    for key, value in data.items():
        k = str(key).strip()
        v = str(value).strip()
        if not k or not v:
            continue
        result[k.lower() if lower_keys else k] = v
    return result


def _normalize_person_name(value: str) -> str:
    value = (value or "").strip()
    for suffix in ("さん", "さま", "様"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value.replace(" ", "").replace("　", "")


def _chatwork_account_id_for(result: dict, host_map: dict[str, str], person_map: dict[str, str]) -> str:
    host_email = (result.get("host_email") or result.get("gmail_user") or "").strip().lower()
    if host_email and host_email in host_map:
        return host_map[host_email]

    candidates = [
        result.get("salesperson_name", ""),
        result.get("salesperson", ""),
        result.get("host_name", ""),
        result.get("gmail_user", ""),
    ]
    normalized_map = {_normalize_person_name(k): v for k, v in person_map.items()}
    for candidate in candidates:
        normalized = _normalize_person_name(str(candidate))
        if normalized and normalized in normalized_map:
            return normalized_map[normalized]
    return ""


def _chatwork_to_line(account_id: str) -> str:
    return f"[To:{account_id}]"


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


def release_routine_lock() -> None:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from routine_lock import release

    release()


def build_completion_message(results: list, warnings: list) -> str:
    # Webhook版 lib/notifier.js の notifySuccess フォーマットに合わせる
    host_map = _load_json_mapping("CHATWORK_ACCOUNT_ID_BY_HOST", lower_keys=True)
    person_map = _load_json_mapping("CHATWORK_ACCOUNT_ID_BY_SALES_PERSON")

    lines = [f"[info][title]✅ 営業フォローメール自動生成完了（{len(results)}件）[/title]"]
    mention_lines = []
    seen_mentions = set()
    for r in results:
        account_id = _chatwork_account_id_for(r, host_map, person_map)
        if account_id and account_id not in seen_mentions:
            seen_mentions.add(account_id)
            mention_lines.append(_chatwork_to_line(account_id))
    if mention_lines:
        lines.append(" ".join(mention_lines))
        lines.append("担当商談のメール下書きと社内確認用Docが作成されました。送信前確認をお願いします。")
        lines.append("")

    for r in results:
        topic = r.get("topic") or r.get("customer_name", "")
        account_id = _chatwork_account_id_for(r, host_map, person_map)
        assignee_prefix = f"{_chatwork_to_line(account_id)} " if account_id else ""
        salesperson = r.get("salesperson_name") or r.get("salesperson") or r.get("host_name") or r.get("host_email", "")
        lines.append(f"{assignee_prefix}商談: {topic}（担当: {salesperson} / {r.get('duration_min', '')}分）")
        lines.append(f"評価: {r.get('evaluation_summary') or '6エージェント合格'}")
        lines.append("")
        vtt_url = r.get("vtt_drive_url")
        if vtt_url:
            lines.append("📝 文字起こしVTT:")
            lines.append(vtt_url)
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
    ap.add_argument("--release-lock", action="store_true", help="通知後にRoutine重複防止ロックを解除")
    args = ap.parse_args()

    try:
        if args.error:
            send(f"[info][title]営業フォローメール 自動生成 エラー[/title]{args.error}[/info]")
            return
        if args.empty:
            send("[info][title]営業フォローメール 自動生成[/title]処理対象の商談はありませんでした。[/info]")
            return

        results, warnings = _load_results(args.results or "{}")
        send(build_completion_message(results, warnings))
    finally:
        if args.release_lock:
            release_routine_lock()


if __name__ == "__main__":
    main()
