# 他アカウント導入フロー

作成日: 2026-05-24  
対象: `zoom-sales-followup` を別の担当者・別会社アカウントの Claude Routine で動かす時の導入手順  
目的: Zoomクラウド録画からVTTを取得し、営業フォローメールを生成してGoogle Driveへ保存し、Chatworkへ通知する状態を再現する。

## 前提

この手順は Claude Routine 用。Zoom Webhook は使わない。  
未処理録画は、Routine が定期実行時にZoom APIへ取りに行くポーリング方式で判定する。

この運用は、送信まで自動化しない。Routine が行うのは以下まで。

1. Zoomクラウド録画とVTT文字起こしの取得
2. 顧客送付用・社内確認用メールの生成
3. Google Driveへの保存
4. 営業担当Gmailへの下書き作成
5. 処理済み台帳 `processed_meetings.json` の更新
6. Chatwork通知

メール本文の最終確認・黄色箇所確認・送信は人間が行う。

## 0. 最初に決めること

| 項目 | 決める内容 | 推奨 |
|---|---|---|
| Zoomの対象範囲 | 個人の録画だけか、組織内の全営業担当分か | 全営業担当分ならZoom管理者権限が必要 |
| 保存先Googleアカウント | 誰のDrive容量でGoogle Docsを作るか | 運用責任者のGoogleアカウント |
| Gmail下書き作成方式 | 営業担当本人のGmailに作るか、単一アカウントに作るか | Workspaceドメインワイド委任で営業担当本人のGmail |
| 通知先 | Chatworkルーム、Slack、LINE等 | 現行コードはChatwork |
| Routine所有者 | 誰のClaudeアカウントでRoutineを作るか | 実運用の責任者アカウント |
| 実行頻度 | 毎時、毎日、手動Run now等 | 初期は手動Run now、安定後に定期実行 |
| 送信責任 | 誰が社内確認して顧客送信するか | 自動送信は禁止のまま |

## 1. Zoom管理者権限を取得する

### 依頼する権限

Zoomアカウントのオーナーまたは既存管理者に、以下を依頼する。

- 対象者にZoomの管理者権限、またはカスタムロールを付与
- Server-to-Server OAuth App の閲覧・編集権限
- 必要スコープをアプリに追加できるロール権限
- 録画・文字起こし設定を確認、変更できる権限
- 全ユーザーの録画を扱う場合は、ユーザー一覧とユーザー録画にアクセスできる権限

Zoom公式では、Server-to-Server OAuthアプリ作成者に対して、S2S OAuth App の View/Edit 権限と、追加するスコープに対応した権限を管理者が付与する必要がある。  
公式: https://developers.zoom.us/docs/internal-apps/

### 管理者に送る依頼文

```text
Zoomクラウド録画から商談文字起こしを自動取得する連携設定のため、
以下の権限付与をお願いします。

1. Zoom App MarketplaceでServer-to-Server OAuth Appを作成・編集できる権限
2. ユーザー一覧とクラウド録画を読み取るためのスコープを追加できる権限
3. Account Management > Account Settings > Recording & Transcript を確認・変更できる権限
4. Account Management > Recording and Transcript Management で録画一覧を確認できる権限

用途は、営業商談のクラウド録画からVTT文字起こしを取得し、
社内確認用のフォローメール下書きを作成するためです。
メール送信は自動化せず、人間が確認して手動送信します。
```

## 2. Zoom録画・文字起こし設定を確認する

Zoom Web Portalで以下を確認する。

### アカウント条件

- Zoomプランが Pro / Business / Education / Enterprise のいずれか
- 対象ホストが Licensed user
- Cloud Recording が有効
- Audio transcript が有効
- 録画保存容量に余裕がある

Zoom公式では、クラウド録画の有効化には対象プラン、管理者権限、Licensed user が必要。  
公式: https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0063923

### 設定画面

Account Management > Account Settings > Recording & Transcript

確認項目:

- `Cloud Recording`: ON
- `Create audio transcript`: ON
- `Record audio-only file`: 任意だがON推奨
- `Display participants' names in the recording`: 任意
- `Add a timestamp to the recording`: 任意
- `Delete cloud recordings after a specified number of days`: 運用上問題ない日数か確認
- `Only the host can download cloud recordings` 系の制限が、API取得を阻害しないか確認

Zoom公式では、音声文字起こしはクラウド録画に対してVTTファイルとして作られる。`Create audio transcript` を有効化する必要がある。  
公式: https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0065911

### 録画一覧の確認

Account Management > Recording and Transcript Management > Recordings

確認項目:

- 対象ホストの録画が見える
- テスト録画が完全に処理済みになっている
- 録画詳細に `Audio transcript` またはVTT相当のファイルがある
- 会議トピックから顧客名を抽出できる命名になっている

Zoom公式では、管理者は Recording and Transcript Management からアカウント内の録画を確認でき、音声文字起こし内のキーワード検索もできる。  
公式: https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067567

## 3. Zoom Server-to-Server OAuth Appを作成する

### 作成場所

Zoom App Marketplace > Develop > Build App > Server-to-Server OAuth App

Zoom公式では、S2S OAuthアプリ作成時に Account ID / Client ID / Client Secret が発行される。  
公式: https://developers.zoom.us/docs/internal-apps/create/

### アプリ情報

| 項目 | 設定例 |
|---|---|
| App name | Sales Followup Mail Generator |
| Short description | Download Zoom cloud recording transcripts for internal follow-up email draft generation |
| Developer contact | 運用責任者の連絡先 |
| Event subscriptions | OFF。Routine運用では使わない |

### 必要スコープ

現行スクリプトは以下を使う。

| 処理 | API | 必要スコープの考え方 |
|---|---|---|
| ユーザー一覧取得 | `GET /users` | ユーザー一覧を読める管理者スコープ |
| ユーザー別録画取得 | `GET /users/{userId}/recordings` | 全ユーザーのクラウド録画を読める管理者スコープ |
| VTTダウンロード | recording file の `download_url` | recording系スコープ |

既存コードコメント上の前提:

```text
recording:read:admin
user:read:admin
```

Zoom側がGranular Scopes表示の場合は、名前が細分化されている可能性がある。画面上では「List users」「View users」「List user recordings」「View cloud recordings」相当の最小権限を選ぶ。録画取得・VTT取得が失敗する場合は、録画ファイルのdownload URLを返すエンドポイントに対応するRecording系のread scopeを追加する。

Zoom公式は、Server-to-Server OAuthではアカウント認証情報でアクセストークンを発行し、トークンの有効期限は1時間、アプリが無効化されるとトークンも使えなくなるとしている。  
公式: https://developers.zoom.us/docs/internal-apps/s2s-oauth/

### 取得する値

Routine環境変数に登録するため、以下を安全な場所に控える。

```text
ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID
ZOOM_CLIENT_SECRET
```

シークレットはチャットやドキュメントに平文で貼らない。Routine環境変数またはパスワード管理ツールで扱う。

## 4. Google Drive保存先を準備する

### 保存先フォルダ

Google Driveに、Routine出力用フォルダを作る。

例:

```text
営業フォローメール_自動生成_仮置き/
```

現行の生成メール保存先:

```text
https://drive.google.com/drive/folders/1KeBeszfV4g1ORx8nQdni0EEdh9mrSBzB
GOOGLE_DRIVE_FOLDER_ID=1KeBeszfV4g1ORx8nQdni0EEdh9mrSBzB
```

必要な共有:

- 運用責任者: 編集可
- 確認担当者: 閲覧またはコメント可
- 送信担当者: 閲覧可

### Google OAuthを準備する

Drive/Docs保存は本人OAuthのrefresh tokenでGoogle Docsを作る。
Gmail下書きは、Workspaceドメインワイド委任のサービスアカウントがある場合、Zoomの `host_email` を対象ユーザーとして営業担当本人のGmailに作成する。
サービスアカウントが無い場合は、本人OAuthのアカウントに下書きを作るフォールバックになるため、営業担当別Gmail運用ではドメインワイド委任を使う。

必要な環境変数:

```text
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_OAUTH_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
```

refresh token取得:

```bash
cd zoom-sales-followup/scripts
python get_refresh_token.py /path/to/oauth.keys.json
```

出力される `scripts/.oauth_secrets.env` の値をRoutine環境変数に登録する。ファイル自体は共有しない。

### Gmail下書き用のWorkspaceドメインワイド委任

Google Cloud Consoleでサービスアカウントを作り、Gmail APIを有効化する。
Google Workspace Admin Consoleの Domain-wide delegation に、そのサービスアカウントのClient IDと以下のOAuth scopeを登録する。

```text
https://www.googleapis.com/auth/gmail.compose
```

Routine環境変数には、以下のどちらかを登録する。

```text
GOOGLE_SERVICE_ACCOUNT_JSON={サービスアカウントJSONの中身}
```

JSONをそのまま貼りづらい環境では、base64化して以下で登録してもよい。

```text
GOOGLE_SERVICE_ACCOUNT_JSON_B64={サービスアカウントJSONをbase64化した文字列}
```

または、ファイルとして置ける環境では:

```text
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json
```

Gmail下書き作成時は、`save_to_gdrive.py --gmail-user "{host_email}"` により、ZoomホストメールアドレスのGmailへ下書きを作成する。

## 5. Chatwork通知先を準備する

必要な環境変数:

```text
CHATWORK_API_TOKEN
CHATWORK_ROOM_ID
```

確認項目:

- APIトークンの発行者が対象ルームに投稿できる
- ルームIDが正しい
- 自動生成通知を受け取るメンバーが入っている
- 通知文にDocs URLが含まれても問題ない権限設計になっている

## 6. Claude Routineを作成する

Claude RoutineはResearch Previewのため、仕様や制限が変わる可能性がある。2026-05-24時点の公式ドキュメントでは、Routineはスケジュール、API、GitHubイベントで起動でき、Anthropic管理のクラウド環境で動く。  
公式: https://code.claude.com/docs/ja/routines

### Routine作成前チェック

- Claude Code on the web が使えるプランか
- Team / Enterpriseの場合、管理者がRoutinesを無効化していないか
- Routine所有者のGitHub接続が済んでいるか
- 対象リポジトリをRoutineがcloneできるか
- 環境変数をRoutineのEnvironmentに登録できるか
- `*.zoom.us`（`zoom.us`・`api.zoom.us` に加え、録画ファイル配信の地域別サブドメイン `us02web.zoom.us` 等を含む。これが無いとVTTダウンロードが403になる）/ `oauth2.googleapis.com` / `www.googleapis.com` / `api.chatwork.com` への外向き通信が許可されているか

Routine公式では、Remote Routineはクラウド上で動き、リポジトリ、環境変数、ネットワークアクセス、コネクタで到達範囲が決まる。必要なものだけに絞る。  
公式: https://code.claude.com/docs/en/routines

### Routine設定項目

| 項目 | 設定 |
|---|---|
| Name | Sales followup mail generator |
| Repository | この `zoom-sales-followup` を含むリポジトリ |
| Branch | 本番運用ブランチ |
| Prompt | `routine/ROUTINE_PROMPT.md` の全文 |
| Environment variables | 下記一覧 |
| Network | Zoom / Google / Chatwork APIへ接続可能にする |
| Trigger | 初期は手動Run now。安定後、毎時または毎営業日で設定 |

依存関係セットアップ:

```bash
cd zoom-sales-followup
python -m pip install -r scripts/requirements.txt
```

Routine側にSetup command欄がある場合は上記を登録する。Setup command欄がない場合は、初回Run nowでStep1前に同じコマンドを実行できるか確認する。依存関係が入らないと、Zoom取得は通ってもGoogle Drive保存時に `googleapiclient` などのimportで失敗する。

環境変数一覧:

```text
ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID
ZOOM_CLIENT_SECRET
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
GOOGLE_OAUTH_REFRESH_TOKEN
GOOGLE_DRIVE_FOLDER_ID
GOOGLE_SERVICE_ACCOUNT_JSON
GOOGLE_SERVICE_ACCOUNT_JSON_B64
CHATWORK_API_TOKEN
CHATWORK_ROOM_ID
VTT_DIR=/tmp/vtt
```

### Routineプロンプト

`routine/ROUTINE_PROMPT.md` をそのまま貼る。特に以下を変えない。

- 未処理判定は `processed_meetings.json`
- 1件ずつ直列処理
- 保存成功後にだけ台帳更新
- Gmail下書きは作成するが、メール送信はしない
- Chatwork通知に「送信前に黄色箇所・ZOOM URL・固有情報を確認」を入れる

## 7. 初回テスト

### テスト録画を作る

対象Zoomアカウントで、以下の条件のテスト商談を1件作る。

- 10分以上
- Cloud Recording
- Audio transcriptが生成される
- トピックに顧客名が入る

推奨トピック例:

```text
【物販システム アクセス】ウェビナー個別面談 山田太郎様
```

### ローカルでZoom取得だけ確認する

Routine前に、可能ならローカルでStep1だけ確認する。

```bash
cd zoom-sales-followup/scripts
python fetch_vtt.py
```

期待結果:

- JSONの `count` が1以上
- `unprocessed[].vtt_path` にVTTが保存される
- `warnings` が空、または原因が説明できる内容
- `host_email` が入る
- `customer_name` が想定通り

### RoutineでRun nowする

Routine詳細画面で `Run now` を実行する。

確認項目:

- Runのステータスだけで成功判断しない。実行ログを開いてStep1〜4を確認する
- Google Driveに顧客別フォルダが作成される
- 顧客送付用Google Docsが作成される
- 社内確認用Google Docsが作成される
- `processed_meetings.json` にmeeting_idが追加される
- ChatworkにDocs URL付き通知が届く
- 顧客送付用に黄色タグ・社内確認情報・余計なメモが混入していない

Claude公式では、Routineの緑ステータスはインフラ上の実行完了を示すだけで、タスク自体の成功を意味しない。必ずRunの中身を確認する。  
公式: https://code.claude.com/docs/en/routines

## 8. 本番化

初回テストが通ったら、以下を行う。

- テスト録画の出力を削除するか、テストであることをフォルダ名に明記
- `processed_meetings.json` にテストmeeting_idが残って問題ないか確認
- 実行頻度を設定
- 通知先メンバーに運用開始を共有
- 「自動生成後、人間が確認して送信」の責任者を明確にする
- 初回1週間は毎回Runログと出力Docsを目視確認する

推奨スケジュール:

| 運用段階 | Trigger |
|---|---|
| 初期検証 | 手動Run nowのみ |
| 小規模運用 | 毎営業日18:00 |
| 安定後 | 1時間ごと、または商談終了が集中する時間帯 |

## 9. よくある失敗と確認先

| 症状 | 主な原因 | 確認先 |
|---|---|---|
| Zoom認証エラー | Account ID / Client ID / Secret不一致、アプリ未Activate | Zoom App Marketplace |
| `GET /users` が失敗 | user read系の管理者スコープ不足 | Zoom S2S App Scopes / Role |
| 録画が取れない | recording read系スコープ不足、対象ホストがLicensedでない | Zoom録画設定 / App Scopes |
| VTTがない | Audio transcript未ON、録画処理中、ローカル録画だった | Recording & Transcript |
| download_urlが使えない | 録画ダウンロード制限、scope不足、トークン付与方式不一致 | Recording management settings |
| Google保存で失敗 | refresh token無効、Drive folder ID誤り、権限不足 | Google OAuth / Drive |
| Gmail下書き作成で失敗 | Gmail API未有効、Domain-wide delegation未承認、`gmail.compose` scope不足、host_email不一致 | Google Cloud / Workspace Admin |
| Chatwork通知失敗 | token/room ID誤り、投稿権限なし | Chatwork |
| Routineだけ失敗 | 環境変数未登録、ネットワーク許可不足、repo clone不可 | Routine Environment / Run log |

## 10. 切り戻し・停止

問題が出た場合の停止順:

1. Claude RoutineのTriggerをPause
2. 必要ならRoutine環境変数からシークレットを削除
3. Zoom S2S AppをDeactivate
4. Google OAuth refresh tokenを無効化
5. Chatwork API tokenを無効化または再発行
6. Drive出力フォルダの共有範囲を見直す

台帳を消すと過去録画が再処理される。再処理したくない場合、`processed_meetings.json` は削除しない。

## 11. 導入完了チェックリスト

### Zoom

- [ ] 管理者権限または必要なカスタムロールが付与されている
- [ ] Cloud Recording がON
- [ ] Create audio transcript がON
- [ ] 対象ホストがLicensed user
- [ ] 録画保存容量に余裕がある
- [ ] テスト録画にVTTが生成されている
- [ ] S2S OAuth AppがActivated
- [ ] `ZOOM_ACCOUNT_ID` / `ZOOM_CLIENT_ID` / `ZOOM_CLIENT_SECRET` を取得済み
- [ ] 最小限のユーザー・録画read権限だけを付与している

### Google Drive

- [ ] 保存先フォルダを作成済み
- [ ] 確認担当者の共有権限を設定済み
- [ ] OAuth refresh tokenを取得済み
- [ ] `GOOGLE_DRIVE_FOLDER_ID` を取得済み
- [ ] テストDocs作成に成功
- [ ] Gmail APIを有効化済み
- [ ] Workspace Domain-wide delegationに `gmail.compose` を登録済み
- [ ] サービスアカウントJSONをRoutine環境変数に登録済み
- [ ] テスト営業担当のGmailに下書き作成成功

### Chatwork

- [ ] API tokenを取得済み
- [ ] Room IDを取得済み
- [ ] テスト通知に成功

### Claude Routine

- [ ] Routine所有者アカウントを決定済み
- [ ] 対象リポジトリを選択済み
- [ ] `routine/ROUTINE_PROMPT.md` を登録済み
- [ ] 必要な環境変数を登録済み
- [ ] Zoom / Google / Chatworkへのネットワークアクセスを許可済み
- [ ] Run nowでStep1〜4が完了
- [ ] Drive保存・Gmail下書き・台帳更新・Chatwork通知まで確認済み
- [ ] 緑ステータスだけでなくRunログを確認済み

### 運用

- [ ] 送信前の人間確認担当者が決まっている
- [ ] 自動送信しない運用が共有されている
- [ ] 初回1週間の目視確認担当者が決まっている
- [ ] 切り戻し手順を関係者が把握している
