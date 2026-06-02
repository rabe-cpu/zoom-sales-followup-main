"""
Zoom API クライアント（Routine用・全社録画対応）
=================================================
喜納さんアカウント（管理者権限）の Server-to-Server OAuth で、
全営業担当のクラウド録画とVTT文字起こしを取得する。

既存 05_Zoomダウンロード/ZOOMダウンロード/02_zoom_api_client.py をベースに、
- 管理者APIで全ユーザー分の録画を取得（user_id=me → 全社へ拡張）
- ページネーション対応
- VTTはテキストで取得（ファイル保存は呼び出し側）
を追加。

必要な環境変数:
    ZOOM_ACCOUNT_ID / ZOOM_CLIENT_ID / ZOOM_CLIENT_SECRET
必要なZoomスコープ（管理者）:
    recording:read:admin, user:read:admin
"""

import os
import time
import requests


class ZoomClient:
    BASE_URL = "https://api.zoom.us/v2"
    OAUTH_URL = "https://zoom.us/oauth/token"

    def __init__(self):
        self.account_id = os.environ["ZOOM_ACCOUNT_ID"]
        self.client_id = os.environ["ZOOM_CLIENT_ID"]
        self.client_secret = os.environ["ZOOM_CLIENT_SECRET"]
        self._token = None
        self._token_expiry = 0.0

    # ------------------------------------------------------------------
    # 認証
    # ------------------------------------------------------------------
    def _get_token(self):
        """S2S OAuthトークンを取得（有効期限内はキャッシュ）"""
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        resp = requests.post(
            self.OAUTH_URL,
            params={"grant_type": "account_credentials", "account_id": self.account_id},
            auth=(self.client_id, self.client_secret),
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Zoom認証エラー {resp.status_code}: {resp.text}")
        data = resp.json()
        self._token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 3600)
        return self._token

    def _get(self, endpoint, params=None):
        """GETリクエスト（401時はトークン再取得して1回リトライ）"""
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(2):
            headers = {"Authorization": f"Bearer {self._get_token()}"}
            resp = requests.get(url, headers=headers, params=params, timeout=60)
            if resp.status_code == 401 and attempt == 0:
                self._token = None  # 強制再取得
                continue
            return resp
        return resp

    # ------------------------------------------------------------------
    # 録画取得
    # ------------------------------------------------------------------
    def list_users(self):
        """アカウント内の有効ユーザー一覧（管理者スコープ）。ページング対応。"""
        users = []
        next_page_token = ""
        while True:
            params = {"status": "active", "page_size": 300}
            if next_page_token:
                params["next_page_token"] = next_page_token
            resp = self._get("/users", params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"ユーザー一覧取得エラー {resp.status_code}: {resp.text}")
            data = resp.json()
            users.extend(data.get("users", []))
            next_page_token = data.get("next_page_token", "")
            if not next_page_token:
                break
        return users

    def list_user_recordings(self, user_id, from_date, to_date):
        """指定ユーザーの録画一覧を期間取得。ページング対応。

        Args:
            user_id: ユーザーID or "me"
            from_date / to_date: "YYYY-MM-DD"
        Returns:
            meeting dict のリスト（recording_files 付き）
        """
        meetings = []
        next_page_token = ""
        while True:
            params = {"from": from_date, "to": to_date, "page_size": 300}
            if next_page_token:
                params["next_page_token"] = next_page_token
            resp = self._get(f"/users/{user_id}/recordings", params=params)
            if resp.status_code != 200:
                # 個別ユーザーの失敗は致命的にしない（録画権限のないユーザー等）
                raise RuntimeError(f"録画取得エラー(user={user_id}) {resp.status_code}: {resp.text}")
            data = resp.json()
            meetings.extend(data.get("meetings", []))
            next_page_token = data.get("next_page_token", "")
            if not next_page_token:
                break
        return meetings

    def list_all_recordings(self, from_date, to_date):
        """全営業担当（全ユーザー）の録画を横断取得。

        管理者権限で list_users → 各ユーザーの録画を集約する。
        個別ユーザーでエラーが出ても全体は止めず、warnings に記録する。

        Returns:
            (meetings, warnings)
        """
        meetings = []
        warnings = []
        for user in self.list_users():
            uid = user.get("id")
            email = user.get("email", "")
            host_name = (
                user.get("display_name")
                or " ".join(part for part in [user.get("last_name", ""), user.get("first_name", "")] if part).strip()
                or user.get("name", "")
            )
            try:
                user_meetings = self.list_user_recordings(uid, from_date, to_date)
                for m in user_meetings:
                    m["_host_email"] = email  # 後段で営業担当特定に使う
                    m["_host_name"] = host_name
                meetings.extend(user_meetings)
            except RuntimeError as e:
                warnings.append(f"user={email}: {e}")
        return meetings, warnings

    # ------------------------------------------------------------------
    # VTTダウンロード
    # ------------------------------------------------------------------
    def download_vtt_text(self, download_url):
        """TRANSCRIPT(VTT)をテキストで取得。

        S2S OAuthトークンを Authorization: Bearer ヘッダーで送る
        （URLパラメータ ?access_token= 方式は403で弾かれるため。webhook版 lib/zoom.js と同方式）。
        Webhook経由ではないので download_token は不要。
        """
        token = self._get_token()
        resp = requests.get(
            download_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"VTTダウンロード失敗 {resp.status_code}")
        resp.encoding = resp.encoding or "utf-8"
        return resp.text


def get_transcript_file(meeting):
    """meeting の recording_files から TRANSCRIPT(VTT) のファイル情報を返す。無ければ None。"""
    for f in meeting.get("recording_files", []):
        if f.get("file_type") == "TRANSCRIPT" and f.get("download_url"):
            return f
    return None
