#!/usr/bin/env python3
"""
preset_ledger.py - 初回テスト用：最新N件だけ未処理に残し、他を処理済み台帳に登録
====================================================================================
過去14日の未処理録画のうち、最新 KEEP 件だけを「未処理」として残し、
残りを処理済み台帳に一括登録する。Run now で少数だけテストしたいとき用。

使い方:
    python preset_ledger.py        # 最新1件を残す（既定）
    KEEP=2 python preset_ledger.py # 最新2件を残す
"""

import io
import json
import os
from datetime import datetime, timedelta, timezone

from googleapiclient.http import MediaIoBaseUpload

from zoom_client import ZoomClient
from gdrive_client import GoogleDriveClient, LEDGER_NAME
from fetch_vtt import should_process, extract_customer_name

JST = timezone(timedelta(hours=9))
KEEP = int(os.getenv("KEEP", "1"))


def main() -> None:
    now = datetime.now(JST)
    from_date = (now - timedelta(days=14)).strftime("%Y-%m-%d")
    to_date = now.strftime("%Y-%m-%d")

    zoom = ZoomClient()
    gdrive = GoogleDriveClient()

    meetings, warnings = zoom.list_all_recordings(from_date, to_date)
    targets = [m for m in meetings if should_process(m)]
    targets.sort(key=lambda m: m.get("start_time", ""), reverse=True)  # 新しい順

    keep = targets[:KEEP]
    preset = targets[KEEP:]

    print(f"処理対象 {len(targets)}件 / 残す(テスト用) {len(keep)}件 / 処理済みにする {len(preset)}件\n")
    print("★ テストで処理される（未処理のまま残す）:")
    for m in keep:
        print(f"   {m.get('start_time','')[:10]}  {extract_customer_name(m.get('topic',''))}")

    # 台帳を1回読んで、preset分を追加し、1回で書き戻す（効率化）
    processed, fid = gdrive.read_ledger()
    for m in preset:
        processed.add(m.get("uuid") or str(m.get("id")))
    body = json.dumps({"processed": sorted(processed)}, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(body), mimetype="application/json", resumable=False)
    if fid:
        gdrive.service.files().update(fileId=fid, media_body=media).execute()
    else:
        gdrive.service.files().create(
            body={"name": LEDGER_NAME, "parents": [gdrive.root_folder_id]},
            media_body=media, fields="id",
        ).execute()

    print(f"\n✅ {len(preset)}件を処理済み台帳に登録しました。Run nowで上記の{len(keep)}件だけ処理されます。")


if __name__ == "__main__":
    main()
