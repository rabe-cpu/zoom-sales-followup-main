---
name: sales-followup-human-docx
description: Create warm Japanese post-sales follow-up emails and Word/docx deliverables from meeting transcripts, MTG文字起こし, Zoom/JamRoll CSV/txt files, 商談zip records, and human email templates. Use when the user asks for 営業後送付メール, 商談後メール, human-feeling sales email text, salesperson tone extraction, seasonal greeting research, yellow editable fields, ZOOM URL placeholders, evaluation loops, or Word output.
---

# Sales Follow-up Human DOCX

## Purpose

商談文字起こしから、営業担当の実発話、顧客との会話内容、送付日の季節感に準拠した営業後送付メールを作り、必要に応じてWord/docxで出力する。

このSkillは、文章を雑に崩して人間味を出すためではなく、実際に話した内容と営業担当の口調に寄せるために使う。

## Required References

必要になった時だけ読む。

- 指摘事項と禁止/許可ルール: `references/user_requirements.md`
- 評価ルーブリック: `references/evaluation_rubric.md`
- Word出力仕様と黄色欄: `references/docx_output.md`
- サブエージェント/オーケストレーション: `references/orchestration.md`
- 出力失敗パターン: `references/output_failure_patterns.md`

## Workflow

1. Source inventory
   - 入力ファイル、雛形、knowledge/video_catalog.md、出力先を列挙する。
   - 元ファイルは変更しない。
   - 多数の商談がある場合は、ユーザー指定がなければ3件を選んで処理する。

2. Transcript analysis
   - 顧客発話と営業発話を分離する。
   - 顧客の背景、悩み、判断軸、反応、次回予定、営業が約束した送付物を抽出する。
   - 営業担当の実発話から、頻出語、依頼表現、締め方、距離感、余白表現を抽出する。

3. Human tone gate
   - `かと`、`かなと`、`見ていただけると`、文を止める余白表現は、営業担当の実発話にある場合だけ使う。
   - 発話にない場合はゼロ。発話にある場合でも1通あたり0から1回を基本にする。
   - `思います` が多い場合は、言い換え、文分割、自然な着地で減らす。
   - 顧客向け最終メールでは、意図的な誤字を入れない。人間味は会話反映、営業口調、文末の自然な揺れで出す。

4. Seasonal research
   - 送付日、月内区分、二十四節気、時候挨拶の参照元を毎回確認する。
   - 季語は硬すぎる漢語調にせず、営業後メール向けの自然な一文へ変換する。

5. Draft email
   - 冒頭に、顧客と実際に話した内容を2から4文入れる。
   - 雛形の流れを尊重する。
   - 参考動画は内部で選定し、docxには候補動画一覧や選定理由の独立セクションを出さない。
   - `knowledge/benchmark_playbooks/suzue_benchmark.md` を必ず参照し、文字起こしベースの営業型として `benchmarkCoach`、`winningPatterns`、`phasePlaybooks`、`customerAttributePlaybooks` に反映する。
   - 鈴江ベンチマークは顧客事実の根拠ではない。顧客が話していない背景、金額、感情、成果期待を足さない。
   - 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューは出力しない。
   - メール本文を書く前に、商談フィードバック要素を内部抽出する。必須項目は 総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks。
   - 社内確認用docxの商談フィードバック要素では、`overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名を表示しない。日本語見出しと自然文に変換する。
   - フィードバックは、トップ営業マンが営業担当に目の前で指導している形にする。箇条書きの羅列ではなく、見立て、次の聞き方、返答案、NGの理由を文章でつなぐ。
   - 社内確認用には、Driver / Driving、Analytical、Amiable、Expressive の4スタイル別に、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を作る。差し替え段落だけで終わらせない。
   - 各スタイルの後ろに、顧客反応シグナル、効く理由、次回質問、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意を営業フィードバックとして入れる。
   - 4スタイルの違いは語尾や文量だけで出さない。Driverは結論・主導権・次アクション、Analyticalは根拠・条件・例外、Amiableは安心・合意形成・相談導線、Expressiveは未来像・承認・ストーリーで分ける。
   - 各スタイルに、価格質問対応、不安が出た時の戻し方、クロージング、ストレス反応へのリカバリーを入れる。
   - 参考動画は knowledge/video_catalog.md から選び、メール本文内では自然な案内文 → 実際のYouTube URL → どこを見ると判断材料になるか の順で短く書く。
   -参考動画URL：〇〇〇 やURL未確定のままなら完成扱いにしない。
   -ZOOMが必要な場合は ZOOM URL：〇〇〇 を残す。

6. Evaluate and repair
   - Claude Codeで `.claude/agents/` が使える場合は、`references/orchestration.md` のTeam Assignmentに従ってサブエージェントを並列または段階実行する。
   - Codexでユーザーがサブエージェント利用を明示した場合は、同じTeam Assignmentで独立評価を並列実行する。
   - サブエージェントが使えない環境では、同一AI内で6つの評価ロールを分け、各ロールの結果を残す。
   - Source-Fact、Sales-Tone、Customer-Human、Risk-Compliance、Ops-Formatting、Final-Whole-Check の6観点で評価する。
   - 評価エージェント別スコアは出さず、各観点をOK/要修正で判定する。
   - 未達またはblockingがあれば修正し、同じ観点で再評価する。最大2回改善する。

7. Word output
   - Word化の前に `references/output_failure_patterns.md` の未完成パターンを確認する。
   - 顧客送付用docxと社内確認用docxを分ける。
   - 本文に `[黄色:...]`、`[/黄色]`、社内ログ見出しを出さない。
   - 営業口調抽出、季語調査結果、参考動画選定理由は内部根拠として使い、docxの独立セクションには出さない。
   - 評価ログと残リスクは、顧客送付用docxにも社内確認用docxにも出さない。
   - `参考動画URL：〇〇〇` のままなら完成扱いにしない。
   - Word/docx指定がある場合は `scripts/create_followup_docx.py` を使える。
   - 黄色欄は営業が最後に触る箇所だけにする。原則は冒頭の確認差し替え欄と `ZOOM URL：〇〇〇`。
- メール本文、4スタイル別全文メール案、商談フィードバック要素、最終確認を同じdocxまたは別docxに残す。評価の詳細記録と残リスクは出さない。

## Output Checklist

最終回答または納品物に必ず含める。

- 作成したWord/docxのパス
- メール本文
- 黄色チェック箇所
- 商談フィードバック要素（総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks）
- 英語キーや `name=` 形式が出ておらず、トップ営業が指導している自然文になっていること
- 評価エージェント確認結果（点数なし）
- Final-Whole-Check
- Orchestration log: 使用したサブエージェント、並列/直列、未使用の場合の理由

## When Not To Use

- 商談文字起こしや面談メモがなく、一般的な定型お礼メールだけを作る場合。
- 会社公式文として硬く統一する文面が必要な場合。
- 契約、法務、成果保証、費用条件を新規に確定する文書を作る場合。
