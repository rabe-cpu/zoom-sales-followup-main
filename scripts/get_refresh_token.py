#!/usr/bin/env python3
"""
get_refresh_token.py - Google Drive用 refresh_token を1回だけ取得
==============================================================================
無料Googleアカウントは共有ドライブを作れず、サービスアカウントではマイドライブに
新規ファイルを作れない（容量0でstorageQuotaExceeded）。そのため本人OAuthを使う。

実行すると:
  1. 認証URLが表示される（ブラウザが自動で開くことも）
  2. まなさんのGoogleアカウントでログイン＆Drive権限を許可
  3. 取得した3つの値を scripts/.oauth_secrets.env に保存（.gitignore済み・画面には出さない）
→ そのファイルの値を Routine の環境変数に登録すれば完了。

使い方:
    python get_refresh_token.py                       # 既定の鍵を使う
    python get_refresh_token.py /path/to/oauth.keys.json
"""

import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_KEYS = "/Users/mana/gcp-oauth.keys.json"


def main() -> None:
    keys_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KEYS
    flow = InstalledAppFlow.from_client_secrets_file(keys_path, SCOPES)
    # open_browser=True: 可能ならブラウザ自動オープン。無理でも認証URLを表示する。
    creds = flow.run_local_server(port=0, open_browser=True,
                                  authorization_prompt_message="\n▼ このURLをブラウザで開いて許可してください:\n{url}\n")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".oauth_secrets.env")
    with open(out_path, "w") as f:
        f.write(f"GOOGLE_OAUTH_CLIENT_ID={creds.client_id}\n")
        f.write(f"GOOGLE_OAUTH_CLIENT_SECRET={creds.client_secret}\n")
        f.write(f"GOOGLE_OAUTH_REFRESH_TOKEN={creds.refresh_token}\n")

    print("\n" + "=" * 56)
    print("✅ 取得成功。秘密3つを下記に保存しました（画面には出しません）:")
    print(f"   {out_path}")
    print("（.gitignore済みなのでGitHubには上がりません）")
    print("=" * 56)


if __name__ == "__main__":
    main()
