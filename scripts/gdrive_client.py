"""
Google Drive クライアント（Routine用・OAuth方式・黄色ハイライト対応）
==================================================================
まなさん本人のOAuth（refresh_token）でマイドライブのフォルダにアクセスし、
- 顧客別フォルダ作成（get_or_create）
- MD → Google Docs 変換アップロード
- [黄色]...[/黄色] タグ → Google Docs上の実際の黄色ハイライトに変換（apply_yellow_highlights）
- 処理済み台帳 processed_meetings.json の読み書き（冪等性のキモ）
を行う。

黄色ハイライトは webhook_server/lib/docs.js の applyYellowHighlights を Python(Docs API)へ移植。
Docs API は drive スコープで動くため、refresh_token の取り直しは不要。

必要な環境変数:
    GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET / GOOGLE_OAUTH_REFRESH_TOKEN
    GOOGLE_DRIVE_FOLDER_ID … 保存先フォルダID（まなさんのマイドライブ内）
"""

import io
import os
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

LEDGER_NAME = "processed_meetings.json"
FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/drive"]  # Docs APIもこのスコープで動く

YELLOW_OPEN = "[黄色]"
YELLOW_CLOSE = "[/黄色]"
YELLOW_RGB = {"red": 1.0, "green": 0.9490196, "blue": 0.4509804}


class GoogleDriveClient:
    def __init__(self):
        self.root_folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
        creds = Credentials(
            token=None,
            refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"],
            client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
            token_uri=TOKEN_URI,
            scopes=SCOPES,
        )
        self.service = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.docs = build("docs", "v1", credentials=creds, cache_discovery=False)

    # ------------------------------------------------------------------
    # フォルダ
    # ------------------------------------------------------------------
    def _find_child(self, name, parent_id, mime_type=None):
        safe = name.replace("\\", "\\\\").replace("'", "\\'")
        q = f"name = '{safe}' and '{parent_id}' in parents and trashed = false"
        if mime_type:
            q += f" and mimeType = '{mime_type}'"
        resp = self.service.files().list(q=q, fields="files(id, name)").execute()
        files = resp.get("files", [])
        return files[0]["id"] if files else None

    def get_or_create_folder(self, name, parent_id=None):
        parent_id = parent_id or self.root_folder_id
        existing = self._find_child(name, parent_id, FOLDER_MIME)
        if existing:
            return existing
        meta = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]}
        folder = self.service.files().create(body=meta, fields="id").execute()
        return folder["id"]

    # ------------------------------------------------------------------
    # MD → Google Docs 変換アップロード（doc_id も返す）
    # ------------------------------------------------------------------
    def upload_md_as_doc(self, md_text, doc_name, folder_id):
        media = MediaIoBaseUpload(
            io.BytesIO(md_text.encode("utf-8")), mimetype="text/markdown", resumable=False
        )
        meta = {"name": doc_name, "parents": [folder_id], "mimeType": DOC_MIME}
        f = self.service.files().create(
            body=meta, media_body=media, fields="id, webViewLink"
        ).execute()
        url = f.get("webViewLink", f"https://docs.google.com/document/d/{f['id']}/edit")
        return url, f["id"]

    # ------------------------------------------------------------------
    # [黄色]...[/黄色] → 実際の黄色ハイライト（lib/docs.js から移植）
    # ------------------------------------------------------------------
    def apply_yellow_highlights(self, document_id):
        """ペアになった [黄色]...[/黄色] を黄色背景に変換し、タグ文字を削除。変換数を返す。"""
        doc = self.docs.documents().get(documentId=document_id).execute()
        text, segments = _flatten_body(doc)
        spans = _find_yellow_spans(text, segments)
        if not spans:
            return 0
        requests = _build_highlight_requests(spans)
        self.docs.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()
        return len(spans)

    # ------------------------------------------------------------------
    # 処理済み台帳（冪等性のキモ）
    # ------------------------------------------------------------------
    def read_ledger(self):
        fid = self._find_child(LEDGER_NAME, self.root_folder_id)
        if not fid:
            return set(), None
        content = self.service.files().get_media(fileId=fid).execute()
        try:
            data = json.loads(content)
            return set(data.get("processed", [])), fid
        except (ValueError, TypeError):
            return set(), fid

    def add_to_ledger(self, meeting_id):
        processed, fid = self.read_ledger()
        if meeting_id in processed:
            return
        processed.add(meeting_id)
        body_bytes = json.dumps(
            {"processed": sorted(processed)}, ensure_ascii=False, indent=2
        ).encode("utf-8")
        media = MediaIoBaseUpload(io.BytesIO(body_bytes), mimetype="application/json", resumable=False)
        if fid:
            self.service.files().update(fileId=fid, media_body=media).execute()
        else:
            self.service.files().create(
                body={"name": LEDGER_NAME, "parents": [self.root_folder_id]},
                media_body=media, fields="id",
            ).execute()


# ----------------------------------------------------------------------
# 黄色ハイライト用ヘルパー（lib/docs.js のロジックをPython移植）
# ----------------------------------------------------------------------
def _flatten_body(doc):
    """Docのbodyを1本のテキストに連結し、各textRunのdocument開始indexを記録。"""
    text = ""
    segments = []
    for item in doc.get("body", {}).get("content", []):
        para = item.get("paragraph")
        if not para:
            continue
        for el in para.get("elements", []):
            content = el.get("textRun", {}).get("content")
            if not content:
                continue
            gstart = len(text)
            text += content
            segments.append({"gstart": gstart, "gend": len(text), "dstart": el["startIndex"]})
    return text, segments


def _to_doc_index(segments, gindex):
    for s in segments:
        if s["gstart"] <= gindex <= s["gend"]:
            return s["dstart"] + (gindex - s["gstart"])
    raise ValueError(f"index mapping failed: {gindex}")


def _find_yellow_spans(text, segments):
    spans = []
    at = 0
    while True:
        op = text.find(YELLOW_OPEN, at)
        if op == -1:
            break
        cl = text.find(YELLOW_CLOSE, op + len(YELLOW_OPEN))
        if cl == -1:
            at = op + len(YELLOW_OPEN)
            continue
        spans.append({
            "marker_start": _to_doc_index(segments, op),
            "text_start": _to_doc_index(segments, op + len(YELLOW_OPEN)),
            "text_end": _to_doc_index(segments, cl),
            "close_start": _to_doc_index(segments, cl),
            "marker_end": _to_doc_index(segments, cl + len(YELLOW_CLOSE)),
        })
        at = cl + len(YELLOW_CLOSE)
    return spans


def _build_highlight_requests(spans):
    requests = []
    # まず背景色を付ける（textStart〜textEnd）
    for span in spans:
        requests.append({
            "updateTextStyle": {
                "range": {"startIndex": span["text_start"], "endIndex": span["text_end"]},
                "textStyle": {"backgroundColor": {"color": {"rgbColor": YELLOW_RGB}}},
                "fields": "backgroundColor",
            }
        })
    # タグ文字を削除（後ろから順に＝indexずれ防止）
    delete_ranges = []
    for span in spans:
        delete_ranges.append({"startIndex": span["close_start"], "endIndex": span["marker_end"]})
        delete_ranges.append({"startIndex": span["marker_start"], "endIndex": span["text_start"]})
    delete_ranges.sort(key=lambda r: r["startIndex"], reverse=True)
    for r in delete_ranges:
        requests.append({"deleteContentRange": {"range": r}})
    return requests
