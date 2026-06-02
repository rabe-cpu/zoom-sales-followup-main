#!/usr/bin/env python3
"""
fetch_vtt.py - 未処理の商談録画VTTを取得（Routine Step1）
==========================================================
処理の流れ:
  1. 共有ドライブの処理済み台帳 processed_meetings.json を読む
  2. 全営業担当の本日分録画を取得（管理者権限）
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
# 標準はJSTの本日分だけ。再処理や復旧時だけ環境変数で遡る。
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "0"))
ONLY_TODAY = os.getenv("ONLY_TODAY", "1").lower() not in {"0", "false", "no"}
VTT_DIR = Path(os.getenv("VTT_DIR", "/tmp/vtt"))
ALLOWED_HOST_EMAILS = {
    email.strip().lower()
    for email in os.getenv("ALLOWED_HOST_EMAILS", "").split(",")
    if email.strip()
}

# VTT保存先Driveフォルダ。環境変数で上書きできる。
# 推奨:
#   VTT_DRIVE_FOLDER_BY_HOST={"kasai@example.com":"folderId"}
#   VTT_DRIVE_FOLDER_BY_SALES_PERSON={"笠井":"folderId"}
#   VTT_DRIVE_FALLBACK_FOLDER_ID=folderId
DEFAULT_VTT_DRIVE_FOLDER_BY_SALES_PERSON = {
    "鈴江": "1mSxrGnBnu-coQ_w-_b5c8Y9m3HFUJLlG",
    "荒木": "1UvpzMxst2FTVEPNX_LMA9he5FMVawYHg",
    "谷口": "1upX4T3w02nTQsnGC1gp4Oin2B66jQErC",
    "松谷": "1VgfJtpanqXCqygC-cH2bI4cYwvT7cOO5",
    "森田": "1kExkYUFH8D1PBV4hHafNWg0HFjJhtB3u",
    "前田": "1TpuWiCRMYfLYBJhBE2fgq72pnzGVMM3G",
}
DEFAULT_VTT_DRIVE_FALLBACK_FOLDER_ID = "1V0CW2ZK7TyV9oxIHSMdWCHKnugOxhDKX"

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


def meeting_start_date_jst(meeting: dict) -> str:
    raw = meeting.get("start_time", "") or ""
    if not raw:
        return ""
    try:
        # Zoom returns ISO8601 strings such as 2026-05-29T03:15:00Z.
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone(JST).strftime("%Y-%m-%d")
    except ValueError:
        return raw[:10]


def meeting_host_email(meeting: dict) -> str:
    return (meeting.get("_host_email") or meeting.get("host_email") or "").strip().lower()


def meeting_host_name(meeting: dict) -> str:
    return (meeting.get("_host_name") or meeting.get("host_name") or "").strip()


def _load_json_mapping(env_name: str, warnings: list[str], lower_keys: bool = False) -> dict:
    raw = os.getenv(env_name, "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        warnings.append(f"{env_name} のJSON解析に失敗: {e}")
        return {}
    if not isinstance(data, dict):
        warnings.append(f"{env_name} はJSON objectで指定してください")
        return {}
    if lower_keys:
        return {str(k).strip().lower(): str(v).strip() for k, v in data.items() if str(v).strip()}
    return {str(k).strip(): str(v).strip() for k, v in data.items() if str(v).strip()}


def _normalize_name(value: str) -> str:
    value = re.sub(r"\s+", "", value or "")
    value = re.sub(r"(さん|さま|様)$", "", value)
    return value


def load_vtt_drive_config(warnings: list[str]) -> tuple[dict, dict, str]:
    host_map = _load_json_mapping("VTT_DRIVE_FOLDER_BY_HOST", warnings, lower_keys=True)
    person_map = dict(DEFAULT_VTT_DRIVE_FOLDER_BY_SALES_PERSON)
    person_map.update(_load_json_mapping("VTT_DRIVE_FOLDER_BY_SALES_PERSON", warnings))
    fallback = os.getenv("VTT_DRIVE_FALLBACK_FOLDER_ID", DEFAULT_VTT_DRIVE_FALLBACK_FOLDER_ID).strip()
    return host_map, person_map, fallback


def resolve_vtt_drive_folder(
    host_email: str,
    host_name: str,
    host_map: dict,
    person_map: dict,
    fallback_folder_id: str,
) -> tuple[str, str, str]:
    if host_email and host_email in host_map:
        return host_map[host_email], "host_email", host_email

    normalized_host = _normalize_name(host_name)
    for person_name, folder_id in person_map.items():
        normalized_person = _normalize_name(person_name)
        if normalized_person and (
            normalized_person == normalized_host
            or normalized_person in normalized_host
            or normalized_host in normalized_person
        ):
            return folder_id, "sales_person_name", normalized_person

    return fallback_folder_id, "fallback_unassigned", "未割当"


def main() -> None:
    now = datetime.now(JST)
    from_date = (now - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    to_date = now.strftime("%Y-%m-%d")
    today_jst = now.strftime("%Y-%m-%d")

    zoom = ZoomClient()
    gdrive = GoogleDriveClient()

    processed, _ = gdrive.read_ledger()
    meetings, warnings = zoom.list_all_recordings(from_date, to_date)
    vtt_host_map, vtt_person_map, vtt_fallback_folder_id = load_vtt_drive_config(warnings)

    VTT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for m in meetings:
        meeting_id = m.get("uuid") or str(m.get("id"))
        if meeting_id in processed:
            continue
        host_email = meeting_host_email(m)
        if ALLOWED_HOST_EMAILS and host_email not in ALLOWED_HOST_EMAILS:
            continue
        start_date = meeting_start_date_jst(m)
        if ONLY_TODAY and start_date != today_jst:
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
        vtt_path = VTT_DIR / f"{start_date}_{_safe(customer)}.vtt"
        vtt_path.write_text(vtt_text, encoding="utf-8")
        host_name = meeting_host_name(m)
        folder_id, folder_source, salesperson_name = resolve_vtt_drive_folder(
            host_email,
            host_name,
            vtt_host_map,
            vtt_person_map,
            vtt_fallback_folder_id,
        )
        vtt_drive_url = None
        vtt_drive_file_id = None
        if folder_id:
            vtt_drive_name = f"{start_date}_{_safe(salesperson_name)}_{_safe(customer)}_商談文字起こし.vtt"
            try:
                vtt_drive_url, vtt_drive_file_id = gdrive.upload_text_file(
                    vtt_text,
                    vtt_drive_name,
                    folder_id,
                    mimetype="text/vtt",
                )
            except Exception as e:
                warnings.append(f"VTT Drive保存失敗 [{m.get('topic', '')}]: {e}")
        else:
            warnings.append(f"VTT Drive保存先未設定 [{m.get('topic', '')}] host={host_email} name={host_name}")
        results.append({
            "meeting_id": meeting_id,
            "topic": m.get("topic", ""),
            "customer_name": customer,
            "host_email": host_email,
            "host_name": host_name,
            "salesperson_name": salesperson_name,
            "start_date": start_date,
            "duration_min": m.get("duration", 0),
            "vtt_path": str(vtt_path),
            "vtt_drive_url": vtt_drive_url,
            "vtt_drive_file_id": vtt_drive_file_id,
            "vtt_drive_folder_id": folder_id,
            "vtt_drive_folder_source": folder_source,
        })

    print(json.dumps(
        {"unprocessed": results, "count": len(results), "warnings": warnings},
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
