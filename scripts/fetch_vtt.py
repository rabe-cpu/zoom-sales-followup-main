#!/usr/bin/env python3
"""
fetch_vtt.py - 未処理の商談録画VTTを取得（Routine Step1）
==========================================================
処理の流れ:
  1. 共有ドライブの処理済み台帳 processed_meetings.json を読む
  2. 全営業担当の録画を過去14日分まとめて取得（管理者権限）
  3. 台帳にない（=未処理の）録画だけを抽出
  4. shouldProcess でフィルタ（パーソナルMTG/10分未満/キャンセル/TRANSCRIPT無し を除外）
  5. 顧客名を抽出し、VTTを /tmp/vtt/ に保存
  6. 未処理商談の一覧を JSON で標準出力（後続のメール生成が読む）

台帳方式の利点: エラーで止まっても未処理分は次回拾う＆何度実行しても重複しない（冪等）。
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from zoom_client import ZoomClient, get_transcript_file
from gdrive_client import GoogleDriveClient

JST = timezone(timedelta(hours=9))
LOOKBACK_DAYS = 14  # 広めに見て、台帳で重複を防ぐ（エラー時の遡り取りこぼし防止）
VTT_DIR = Path(os.getenv("VTT_DIR", "/tmp/vtt"))

# 顧客名抽出パターン（webhook_server/config/extractors.js から移植・空白入り名前対応に改善）
# `[^】]+?`（非貪欲）で「山口 宗大 様」のような姓名に空白が入る名前も拾う。
CUSTOMER_PATTERNS = [
    r"個別面談\s*([^】]+?(?:さま|様|さん))",
    r"相談会\s*([^】]+?(?:さま|様|さん))",
    r"面談\s*([^】]+?(?:さま|様|さん))",
    r"相談\s*([^】]+?(?:さま|様|さん))",
    r"MTG\s*([^】]+?(?:さま|様|さん))",
]


def extract_customer_name(topic: str) -> str:
    for pattern in CUSTOMER_PATTERNS:
        m = re.search(pattern, topic, re.IGNORECASE)
        if m:
            # 姓名間の空白を除去して 5/19 形式に統一（「 山口 宗大 様」→「山口宗大様」）
            return re.sub(r"\s+", "", m.group(1).strip())
    # フォールバック: topic先頭40文字をファイル名安全化（空白も除去）
    return re.sub(r"\s+", "", _safe(topic))[:40]


def should_process(meeting: dict) -> bool:
    """処理対象判定（extractors.js shouldProcess から移植）"""
    topic = meeting.get("topic", "")
    if "パーソナルミーティングルーム" in topic:
        return False
    if "アクセス無料オンライン説明会" in topic:
        # 合同説明会は個人商談向けフォローメールの対象外
        return False
    if meeting.get("duration", 0) < 10:
        return False
    if "キャンセル済み" in topic:
        return False
    if get_transcript_file(meeting) is None:
        return False
    return True


def _safe(name: str) -> str:
    return re.sub(r'[/\\:*?"<>|]', "_", name)


def main() -> None:
    now = datetime.now(JST)
    from_date = (now - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    to_date = now.strftime("%Y-%m-%d")

    zoom = ZoomClient()
    gdrive = GoogleDriveClient()

    processed, _ = gdrive.read_ledger()
    meetings, warnings = zoom.list_all_recordings(from_date, to_date)

    VTT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for m in meetings:
        meeting_id = m.get("uuid") or str(m.get("id"))
        if meeting_id in processed:
            continue
        if not should_process(m):
            continue
        transcript = get_transcript_file(m)
        try:
            vtt_text = zoom.download_vtt_text(transcript["download_url"])
        except RuntimeError as e:
            warnings.append(f"VTT取得失敗 [{m.get('topic', '')}]: {e}")
            continue
        customer = extract_customer_name(m.get("topic", ""))
        start_date = (m.get("start_time", "") or "")[:10]
        vtt_path = VTT_DIR / f"{start_date}_{_safe(customer)}.vtt"
        vtt_path.write_text(vtt_text, encoding="utf-8")
        results.append({
            "meeting_id": meeting_id,
            "topic": m.get("topic", ""),
            "customer_name": customer,
            "host_email": m.get("_host_email", m.get("host_email", "")),
            "start_date": start_date,
            "duration_min": m.get("duration", 0),
            "vtt_path": str(vtt_path),
        })

    print(json.dumps(
        {"unprocessed": results, "count": len(results), "warnings": warnings},
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
