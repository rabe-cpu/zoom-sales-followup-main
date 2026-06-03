# 営業フォローメール自動生成 Routine（実行手順の正本）

> このファイルは Routine に登録するプロンプトの正本。
> Routines の設定画面には、この内容を貼り付ける（CLAUDE.md からも参照される）。

あなたはこのリポジトリ上で動く「営業フォローメール自動生成 Routine」です。
以下の Step を順に、最後まで自走で実行してください。ユーザーへの確認待ちはしません。

---

## Step 0-1: 依存関係を準備

Routine環境では毎回クリーンな実行環境になる場合があるため、Google API / Zoom API連携に必要なPython依存関係を最初に入れる。
このStepはロック取得より前に必ず実行する。

まず軽量チェックを行い、不足がある場合だけ `pip install` する。毎回無条件にinstallしない。

```
python scripts/check_dependencies.py
```

不足があった場合だけ実行:

```
python -m pip install -r scripts/requirements.txt
```

- すでに入っている場合は短時間で終了する。
- 失敗した場合は、まだロックを取得していないためロック解除は不要。可能なら `python scripts/notify_chatwork.py --error "Step-1 依存関係インストール失敗: <内容>"` で通知して終了する。

## 実行時間の目安

- 目標は1件あたり8分以内、2件で15分以内。
- 20分を超えそうな場合は、社内確認用の厚さを保ったまま、重複説明・評価ログ・長い思考過程を削る。
- 長尺商談（90分超）は全文を何度も読み返さない。最初に商談事実サマリー、顧客発話、営業約束、費用・審査・日程・黄色候補だけを抽出し、その要約を後工程の正本にする。
- 6ロール評価は品質担保に必要だが、各ロールに全文VTTを再読させない。抽出済みサマリー、顧客送付用本文、社内確認用の主要見出し、リスク箇所だけを渡す。
- Final-Whole-Checkは、全出力を再生成しない。背景エージェントで全文レビューさせず、下記8項目のチェックリスト判定と必要最小限の修正指示に限定する。

## Step 0: 重複実行防止ロックを取得

30分間隔など外部スケジューラから起動される場合、前回実行がまだ処理中の可能性がある。
最初に共有Google Drive上のロックを取得する。

```
python scripts/routine_lock.py acquire
```

- 終了コードが `0` の場合だけ Step 1 へ進む。
- 終了コードが `75` の場合は、前回Routineがまだ実行中なので**正常扱いで終了**する。Step1以降、Chatwork通知、ロック解除は実行しない。
- その他のエラーの場合は、可能なら `python scripts/notify_chatwork.py --error "Step0 ロック取得失敗: <内容>"` で通知して終了する。
- ロックの事故残りは `ROUTINE_LOCK_TTL_MINUTES`（既定90分）を超えると次回取得時に自動破棄される。

## Step 1: 本日分の未処理商談VTTを取得

bash で実行:
```
cd scripts && python fetch_vtt.py
```

標準出力のJSON（`unprocessed` 配列・`count`・`warnings`）を受け取る。
- 標準ではJSTの本日分だけを処理する。古い未処理商談が台帳に残っていても、このRoutineではメール生成しない。
- 営業担当以外のZoom録画を処理しないため、環境変数 `ALLOWED_HOST_EMAILS` に含まれる `host_email` の商談だけを処理する。
- VTT文字起こしは `/tmp/vtt/` に保存し、同時に営業担当別Google Driveフォルダへ保存する。`vtt_drive_url` / `vtt_drive_folder_source` が出力に含まれる場合は、Step4の通知結果へ引き継ぐ。
- 営業担当別フォルダは `host_email` が取れる場合は `VTT_DRIVE_FOLDER_BY_HOST`、Zoomユーザー名で判定できる場合は `VTT_DRIVE_FOLDER_BY_SALES_PERSON`、どちらも合わない場合は `VTT_DRIVE_FALLBACK_FOLDER_ID` または既定の未割当フォルダを使う。
- 復旧などで過去分を処理したい場合だけ、環境変数 `LOOKBACK_DAYS` と `ONLY_TODAY=0` を一時的に設定する。
- `warnings` があれば記録しておき、Step4の通知に含める。
- `count` が 0 でも**ここで打ち切らない**。Step2/3は0件ループで自動スキップされ、Step4で1回だけ `--empty` 通知される。Step1で `--empty` を呼ぶと Step4 と重複して通知が2件届くので絶対にやらない。
- スクリプトがエラー終了したら: `python scripts/notify_chatwork.py --error "Step1 VTT取得失敗: <内容>" --release-lock` で通知して終了。

## Step 2: 各商談のメールを生成（1件ずつ直列）

`unprocessed` の各商談について、1件ずつ順番に:
1. `vtt_path` のVTTファイルを読む。
   - 90分超のVTTは、全文を4分割以上で詳細読解し続けない。まず発話単位で、顧客背景、判断軸、費用・審査・支払い、約束事項、次アクション、黄色候補、営業口調の根拠だけを抽出した「商談事実サマリー」を作る。
   - 以降のメール作成、評価、保存では、その商談事実サマリーを正本にする。事実確認が必要な時だけVTT原文へ戻る。
2. `knowledge/video_catalog.md` を読み、候補動画を `動画タイトル / YouTube URL / 顧客に合う理由` で列挙してから1本選び、参考動画は `理由 → 実際のYouTube URL → 見る観点1文` で出す。
3. `knowledge/benchmark_playbooks/suzue_benchmark.md` を読み、営業後メール生成と社内確認用の商談フィードバック要素に必ず反映する。これは文字起こしベースの営業型だけを参照し、音声・映像コーチング、録音練習、模写練習メニューは出力しない。
4. OpenAI Vector Storeが利用可能な場合は、本文を書く前に `knowledge/rag/suzue_vector_store.md` に従って鈴江商談RAGを検索する。
   - 検索クエリは、今回商談の判断軸、不安、価格反応、作業時間、家族相談、審査、比較検討、次アクションから作る。
   - 実行例: `python scripts/suzue_vector_store.py search "価格不安 作業時間 家族相談 次アクション" --max-results 8`
   - ブラウザ版Claude Codeでは `OPENAI_VECTOR_STORE_ID` 環境変数を優先する。`knowledge/rag/suzue_vector_store_state.json` がなくても、環境変数があれば検索する。
   - 検索結果は `benchmarkCoach` / `winningPatterns` / `phasePlaybooks` / `customerAttributePlaybooks` に反映する。
   - 検索結果は営業型の根拠であり、今回顧客の事実を増やす根拠ではない。顧客送付用本文に鈴江商談名、検索結果、引用原文、RAG実行ログを出さない。
   - APIキーなし、Vector Store未作成、検索失敗の場合は `knowledge/benchmark_playbooks/suzue_benchmark.md` にフォールバックし、社内確認用docx/MDには失敗ログを出さない。
5. `sales-followup-email-from-transcript` Skill を使ってメールを生成する。
   - 商談情報: `customer_name` / `host_email` / `start_date` / `duration_min` / 送付日=今日のJST日付。
   - 営業担当の口調は `knowledge/sales_persons/` を参照。未登録担当なら `sales-tone-knowledge-register` で生成。
   - `knowledge/12_social_style_email_variants.md` を読み、社内確認用MDには4ソーシャルスタイル別の全文メール案と営業フィードバックを入れる。顧客タイプの判定はしない。
   - メール本文を書く前に、`sales-analysis-app-openai-next` の思想に沿って商談フィードバック要素を内部抽出する。
     - `overallSummary`: 総合概要、現在の検討状態、勝ち商談との差分
     - `customerInsights`: 顧客インサイト、潜在ニーズ、言い切っていない不安、比較対象、判断基準
     - `cognitiveBias`: 認知バイアス。name / description / counterMeasure
     - `expectationGap`: 期待値のズレ。topic / gap / solution
     - `strengths`: 良かった点。item / detail
     - `improvementPoints`: 改善ポイント。item / detail
     - `coachingCards`: AIコーチングカード4枚。theme / scene / insight / issue / strategy / script / outcome
     - `winningPatterns`: 再現する勝ち筋。勝ち筋名 / 使う場面 / 顧客シグナル / トップ営業の動き / コピートーク / なぜ効くか / NG例 / 次回実践方法
     - `stageStrategy`: currentGoal / keepUntilLater / mustHearBeforeProposal / planDecisionPath
     - `phasePlaybooks`: 今回該当する商談フェーズ、目的、顧客シグナル、質問、返答、次フェーズへのつなぎ
     - `customerSignals`: 温度感、懸念、購入動機、決裁観点、価格反応、家族相談、比較検討
     - `temperature`: 高 / 中 / 低 と理由。数値スコアは出さない
     - `nextBestAction`: 送信後または次回接点で営業担当が取る具体行動
     - `hearingQuestions`: 次に聞くべき質問を優先順で最大3つ
     - `recommendedAnswer`: 顧客から返信・質問が来た時にそのまま使える返答
     - `benchmarkCoach`: トップ営業がそのまま話す台本、効く理由、型、伝え方
     - `contextBridge`: 商談内のどの発言・不安・判断軸からつなげるか
     - `customerAttributePlaybooks`: 慎重・分析型、価格重視、成果重視、初心者、経験者、家族相談あり、即決寄り、比較検討中などから今回使えそうなものを1〜2個
   - 社内確認用docx/MDに出す商談フィードバック要素では、`overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名を表示しない。日本語見出しと自然文に変換する。
   - フィードバックはトップ営業マンが営業担当に目の前で指導している形にする。箇条書きの羅列ではなく、「この商談はこう見る」「次回はこう聞く」「この場面ではこう返す」という実践文を中心にする。
   - 4スタイル別メール案は、Driver / Driving、Analytical、Amiable、Expressive のすべてについて、件名、宛名、本文、参考動画、ネクストアクション、署名、固定資料URL、固定フォームURLまで含む全文にする。差し替え段落だけで終わらせない。
   - 各スタイルの営業フィードバックには、顧客反応シグナル、効く理由、次回質問、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意を入れる。
   - 社内確認用MDは厚くするが冗長にしない。目安は1顧客250〜320行以内。4スタイル別全文メールは必須だが、各スタイルの営業フィードバックは「使い方」「価格対応」「次回質問」「返答案」「避ける言い方」を中心に圧縮し、同じ説明を4回繰り返さない。
   - 4スタイルの違いは語尾や文量だけで出さない。Driverは結論・主導権・次アクション、Analyticalは根拠・条件・例外、Amiableは安心・合意形成・相談導線、Expressiveは未来像・承認・ストーリーで分ける。
   - 各スタイルに、価格質問対応、不安が出た時の戻し方、クロージング、ストレス反応へのリカバリーを入れる。
   - 季語は送付日で毎回調査。6エージェント評価で全観点が合格になるまで改善。点数や6ロール別スコアは出力しない。
   - 最後に軽量版Final-Whole-Checkで横断確認する。背景タスクで5分以上待つ運用にしない。統括AIが以下の8項目を直接確認し、NGだけ最小修正する。
     - 顧客送付用に社内情報なし
     - 黄色タグ / ZOOM / 固有情報OK
     - 参考動画URLが実URL
     - 成果保証・審査保証・危険表現なし
     - 営業口調・余白表現OK
     - 社内確認用4スタイル全文案あり
     - 英語キー・評価ログ・残リスクなし
     - Drive保存・Gmail下書き作成に進める
   - 3回改善しても合格しない場合は無理に整えず、社内確認用MDにその旨を明記し、通知で「要人間確認」とする。
6. 出力を `/tmp/output/{customer_name}/` に保存:
   - `01_{customer_name}_顧客送付用.md`
   - `01_{customer_name}_社内確認用.md`（[黄色]タグ・4ソーシャルスタイル別全文メール案・商談フィードバック要素・最終確認を含む。商談フィードバック要素には 総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks を含める。英語キーや `name=` 形式は出さず、トップ営業の指導文にする。評価ログと残リスクは入れない）
7. その商談の保存が終わったら、すぐ Step 3 を実行する（1件ごとに保存＝途中失敗のロスを最小化）。

## Step 3: 共有ドライブに保存＋Gmail下書き作成＋台帳更新

その商談のメール生成が終わるたびに実行:
```
python scripts/save_to_gdrive.py \
  --customer "{customer_name}" --send-date "{send_date}" \
  --meeting-id "{meeting_id}" \
  --customer-md "/tmp/output/{customer_name}/01_{customer_name}_顧客送付用.md" \
  --internal-md "/tmp/output/{customer_name}/01_{customer_name}_社内確認用.md" \
  --gmail-user "{host_email}"
```
- 出力JSONの `customer_url` / `internal_url` / `gmail_draft_id` / `gmail_user` / `gmail_auth_mode` を記録（最後の通知に使う）。
- `--gmail-user` はZoomの `host_email` を入れる。Workspaceドメインワイド委任が有効な場合、その営業担当のGmailに下書きが作成される。
- 顧客メールアドレスが未確定でも、To空欄の下書きとして作成する。営業担当が送信前に宛先・黄色箇所・ZOOM URL・固有情報を確認する。
- このスクリプトが成功すると meeting_id が処理済み台帳に追記される（＝冪等）。
- Drive保存またはGmail下書き作成のどちらかが失敗した場合は台帳に追記されない（次回再処理される）。
- 失敗時はエラーを記録し、次の商談へ進む。

## Step 4: Chatwork通知

全商談の処理が終わったら、**1回だけ**通知する（Step1で `--empty` を呼ばないこと。Step1とStep4の両方で呼ぶと2件届く）：
- **0件のとき**: `python scripts/notify_chatwork.py --empty --release-lock`
- **1件以上のとき**: 下記コマンドで `--results` を通知
```
python scripts/notify_chatwork.py --results '<results JSON>' --release-lock
```
`results JSON` の形式:
```json
{
  "results": [
    {"customer_name": "...", "topic": "...", "host_email": "...", "duration_min": 60,
     "evaluation_summary": "...", "remaining_risks": ["...", "..."],
     "vtt_drive_url": "...",
     "customer_url": "...", "internal_url": "...",
     "gmail_user": "...", "gmail_draft_id": "...", "gmail_auth_mode": "..."}
  ],
  "warnings": ["...（Step1のwarnings や 各商談の失敗）..."]
}
```
各フィールドの作り方（通知の見やすさのため重要）:
- `evaluation_summary`: **点数や6ロール別スコアを書かない**。何を盛り込んだか、何を修正したかの**文章要約**にする
  （例:「音声問題謝罪・連日参加へのお礼・個別相談会確認・動画推薦を盛り込み、修正1回で全観点合格」）
- `remaining_risks`: **営業が送付前に確認すべき具体項目**のリスト
  （例:「PDFのURL差し替え」「次回ZOOM URL日程確定後追記」）。無ければ省略可
- `topic` / `duration_min`: Step1のJSONからそのまま引き継ぐ

---

## 原則

- **1件ずつ直列**で処理する（並列にしない。セッションのリソース・安定性のため）。
- **1件の失敗で全体を止めない**。失敗した商談は台帳に載らず次回再処理される。
- **重複実行しない**。Step0でロックが取れない場合は、前回実行中として何も処理しない。
- 最終送信はしない（メール生成・Docs保存・Gmail下書き作成・通知まで。送信は人間が手動）。
- 通知には必ず「送信前に黄色箇所・ZOOM URL・固有情報を確認」を含める。
