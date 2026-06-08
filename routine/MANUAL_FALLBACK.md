# 手動フォールバック手順

Routine が失敗した / research preview が不調なときに、手元（ローカルのClaude Code）で同じ処理を回す手順。
台帳（`processed_meetings.json`）があるので、手動で回しても重複しない。

## 前提（認証情報）
ローカルで動かす場合、scripts/ から参照できる場所に以下を用意:
- Zoom: `ZOOM_ACCOUNT_ID` / `ZOOM_CLIENT_ID` / `ZOOM_CLIENT_SECRET`
- Google Drive保存: `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` / `GOOGLE_DRIVE_FOLDER_ID`
- Gmail下書き: Workspaceドメインワイド委任を使う場合は `GOOGLE_SERVICE_ACCOUNT_JSON`（JSON文字列またはパス）、`GOOGLE_SERVICE_ACCOUNT_JSON_B64`、または `GOOGLE_CREDENTIALS_PATH`
- Chatwork: `CHATWORK_API_TOKEN` / `CHATWORK_ROOM_ID`
- 担当者別の通知先ルームを使う場合: `CHATWORK_ROOM_ID_BY_HOST` または `CHATWORK_ROOM_ID_BY_SALES_PERSON`
- 担当者メンションを入れる場合: `CHATWORK_ACCOUNT_ID_BY_HOST` または `CHATWORK_ACCOUNT_ID_BY_SALES_PERSON`

Chatworkの担当者account_idを確認する:

```
python scripts/list_chatwork_members.py
```

出力された `account_id` と `name` を見て、`CHATWORK_ACCOUNT_ID_BY_SALES_PERSON` に設定する。
`CHATWORK_ROOM_ID` はデフォルト通知先グループチャットのIDであり、担当者メンションには使えない。

担当者別に投稿先ルームを分ける場合は、下記のどちらかを追加する。host_email指定を優先する。

```
CHATWORK_ROOM_ID_BY_HOST={"new1@example.com":"111111111","new2@example.com":"222222222"}
```

または

```
CHATWORK_ROOM_ID_BY_SALES_PERSON={"新担当A":"111111111","新担当B":"222222222"}
```

担当者メンションを飛ばすには、別途下記のどちらかを追加する。

```
CHATWORK_ACCOUNT_ID_BY_SALES_PERSON={"森田":"123456789","松谷":"987654321"}
```

または

```
CHATWORK_ACCOUNT_ID_BY_HOST={"yu_morita@nextjp.co.jp":"123456789","m_matsuya@nextjp.co.jp":"987654321"}
```

## 1. 未処理VTTを取得
```
cd scripts && python fetch_vtt.py
```
→ `/tmp/vtt/` にVTT、標準出力に未処理商談一覧JSONが出る。

## 2. メール生成（このリポジトリをClaude Codeで開く）
未処理一覧の各VTTについて、Claude Code に
「このVTT（パス）から営業フォローメールを作って」と渡す。
→ `sales-followup-email-from-transcript` Skill が発動し、顧客送付用／社内確認用MDができる。
`/tmp/output/{顧客名}/` に保存する。

## 3. 共有ドライブに保存＋台帳更新
```
python scripts/save_to_gdrive.py \
  --customer "{顧客名}" --send-date "{送付日}" --meeting-id "{uuid}" \
  --customer-md "/tmp/output/{顧客名}/01_{顧客名}_顧客送付用.md" \
  --internal-md "/tmp/output/{顧客名}/01_{顧客名}_社内確認用.md" \
  --gmail-user "{Zoomのhost_email}"
```

## 4. 通知（任意）
```
python scripts/notify_chatwork.py --results '<results JSON>'
```
