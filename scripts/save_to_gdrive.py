#!/usr/bin/env python3
"""
save_to_gdrive.py - 生成メールを共有ドライブにGoogle Docs保存＋台帳更新（Routine Step3）
==========================================================================
1商談の生成物（顧客送付用MD・社内確認用MD）を共有ドライブに保存し、
営業担当のGmailに顧客送付用メールの下書きを作成する。
  1. {送付日}_{顧客名}/ サブフォルダを get_or_create
  2. 各MDを Google Docs に変換アップロード
  3. --gmail-user があれば、そのGmailに下書きを作成
  4. Drive保存とGmail下書きが成功したら meeting_id を処理済み台帳に追記（← ここで初めて「処理済み」）

台帳追記を最後に行うことで、途中で失敗した商談は未処理のまま残り、次回再処理される（冪等）。

使い方:
  python save_to_gdrive.py \
    --customer 山田太郎様 --send-date 2026-05-24 --meeting-id <uuid> \
    --customer-md /tmp/output/山田太郎様/01_山田太郎様_顧客送付用.md \
    --internal-md /tmp/output/山田太郎様/01_山田太郎様_社内確認用.md \
    --gmail-user kasai@example.com
"""

import argparse
import json
from pathlib import Path

from gdrive_client import GoogleDriveClient
from gmail_client import GmailDraftClient, build_draft_content


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--customer", required=True, help="顧客名")
    ap.add_argument("--send-date", required=True, help="送付日 YYYY-MM-DD")
    ap.add_argument("--meeting-id", required=True, help="Zoom meeting uuid（台帳キー）")
    ap.add_argument("--customer-md", required=True, help="顧客送付用MDのパス")
    ap.add_argument("--internal-md", required=True, help="社内確認用MDのパス")
    ap.add_argument("--gmail-user", help="下書きを作成する営業担当のGmailアドレス（通常はZoom host_email）")
    ap.add_argument("--draft-to", help="下書きのTo。未指定なら空欄の下書きを作成")
    args = ap.parse_args()

    gdrive = GoogleDriveClient()
    folder_id = gdrive.get_or_create_folder(f"{args.send_date}_{args.customer}")

    customer_md = Path(args.customer_md).read_text(encoding="utf-8")
    internal_md = Path(args.internal_md).read_text(encoding="utf-8")

    customer_url, customer_doc_id = gdrive.upload_md_as_doc(
        customer_md, f"01_{args.customer}_顧客送付用", folder_id
    )
    internal_url, internal_doc_id = gdrive.upload_md_as_doc(
        internal_md, f"01_{args.customer}_社内確認用", folder_id
    )

    # [黄色]...[/黄色] を実際の黄色ハイライトに変換（主に社内確認用。顧客用は通常0件）
    # Docs API が無効の場合は警告のみ（Drive保存・Gmail下書きは継続）
    highlight_count = 0
    try:
        gdrive.apply_yellow_highlights(customer_doc_id)
        highlight_count = gdrive.apply_yellow_highlights(internal_doc_id)
    except Exception as e:
        print(f"[WARNING] 黄色ハイライト変換スキップ（Docs API 未有効化）: {e}", flush=True)

    gmail_draft = None
    gmail_error = None
    gmail_auth_mode = None
    if args.gmail_user:
        try:
            subject, body = build_draft_content(customer_md, args.customer)
            gmail = GmailDraftClient(args.gmail_user)
            gmail_auth_mode = gmail.auth_mode
            gmail_draft = gmail.create_draft(subject, body, args.draft_to)
        except Exception as e:
            gmail_error = str(e)
            print(f"[WARNING] Gmail下書き作成スキップ: {e}", flush=True)

    # Drive保存が成功したら処理済みにする（Gmail失敗でも台帳更新する）
    gdrive.add_to_ledger(args.meeting_id)

    result = {
        "customer": args.customer,
        "customer_url": customer_url,
        "internal_url": internal_url,
        "yellow_highlights": highlight_count,
        "gmail_user": args.gmail_user,
        "gmail_auth_mode": gmail_auth_mode,
        "gmail_draft_id": gmail_draft.get("id") if gmail_draft else None,
        "gmail_message_id": gmail_draft.get("message", {}).get("id") if gmail_draft else None,
        "gmail_error": gmail_error,
        "meeting_id": args.meeting_id,
        "marked_processed": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
