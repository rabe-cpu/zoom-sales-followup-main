"""
Gmail draft client for sales follow-up Routine.

Preferred auth:
  Google Workspace domain-wide delegation with a service account.
  The draft is created in the Gmail mailbox of the Zoom host / salesperson.

Fallback auth:
  User OAuth refresh token. This creates drafts only in the authenticated user's
  mailbox, so it is mainly for local tests or single-account operation.

Required scope:
  https://www.googleapis.com/auth/gmail.compose
"""

from __future__ import annotations

import base64
import json
import os
import re
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import httplib2
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
TOKEN_URI = "https://oauth2.googleapis.com/token"
YELLOW_TAG_RE = re.compile(r"\[/?黄色\]")
_CA_CERTS = os.environ.get("SSL_CERT_FILE", "/etc/ssl/certs/ca-certificates.crt")


class GmailDraftClient:
    def __init__(self, user_email: Optional[str] = None):
        self.user_email = (user_email or os.getenv("GMAIL_IMPERSONATE_USER", "")).strip()
        _has_oauth = bool(os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN"))
        self.auth_mode = "oauth_user" if _has_oauth else ("domain_wide_delegation" if _load_service_account_info() else "none")
        creds = _build_credentials(self.user_email)
        http = httplib2.Http(ca_certs=_CA_CERTS)
        auth_http = AuthorizedHttp(creds, http=http)
        self.service = build("gmail", "v1", http=auth_http, cache_discovery=False)

    def create_draft(self, subject: str, body: str, to_email: Optional[str] = None) -> dict:
        message = EmailMessage()
        message["Subject"] = subject
        if to_email:
            message["To"] = to_email
        message.set_content(body)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        draft = self.service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}},
        ).execute()
        return draft


def build_draft_content(md_text: str, customer_name: str) -> tuple[str, str]:
    """Extract a subject and plain-text body from the generated customer MD."""
    lines = md_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    subject = ""
    kept_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not subject:
            m = re.match(r"^(?:件名|Subject)\s*[:：]\s*(.+)$", stripped, re.IGNORECASE)
            if m:
                subject = m.group(1).strip()
                continue
            m = re.match(r"^【件名】\s*(.+)$", stripped)
            if m:
                subject = m.group(1).strip()
                continue
        kept_lines.append(line)

    if not subject:
        subject = f"本日はありがとうございました／{customer_name}"

    body = "\n".join(kept_lines).strip()
    body = _clean_customer_body(body)
    return subject, body


def _clean_customer_body(text: str) -> str:
    text = YELLOW_TAG_RE.sub("", text)
    cleaned_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped in {"```text", "```markdown", "```"}:
            continue
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            if "営業後送付" in title or "顧客送付" in title:
                continue
        cleaned_lines.append(line.rstrip())
    return "\n".join(cleaned_lines).strip()


def _build_credentials(user_email: str):
    # OAuth user credentials (refresh token) are preferred when available,
    # as service account domain-wide delegation may not be configured.
    refresh_token = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    if refresh_token and client_id and client_secret:
        return Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri=TOKEN_URI,
        )

    service_account_info = _load_service_account_info()
    if service_account_info:
        if not user_email:
            raise RuntimeError(
                "Gmail draft creation with domain-wide delegation requires --gmail-user "
                "or GMAIL_IMPERSONATE_USER."
            )
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=GMAIL_SCOPES,
        )
        return creds.with_subject(user_email)

    raise RuntimeError(
        "Gmail credentials not found. Set GOOGLE_SERVICE_ACCOUNT_JSON or "
        "GOOGLE_CREDENTIALS_PATH for Workspace domain-wide delegation, or set "
        "GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET / "
        "GOOGLE_OAUTH_REFRESH_TOKEN for single-user OAuth."
    )


def _load_service_account_info() -> Optional[dict]:
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    raw_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64", "").strip()
    path = os.getenv("GOOGLE_CREDENTIALS_PATH", "").strip()

    if raw_b64:
        decoded = base64.b64decode(raw_b64).decode("utf-8")
        return json.loads(decoded)

    if raw:
        if raw.startswith("{"):
            return json.loads(raw)
        candidate = Path(raw)
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))

    if path:
        candidate = Path(path)
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))

    return None
