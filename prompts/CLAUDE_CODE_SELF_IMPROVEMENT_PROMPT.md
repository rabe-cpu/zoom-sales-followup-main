# Claude Code Self Improvement Prompt

Claude Codeで、評価エージェント付きの自己改善ループを明示的に回すためのプロンプト。

```text
以下の手順で、営業後送付メールを生成・評価・改善してください。

前提:
- CLAUDE.md
- .claude/skills/sales-followup-email-from-transcript/SKILL.md
- .claude/skills/sales-transcript-intake-analysis/SKILL.md
- .claude/skills/sales-seasonal-greeting-research/SKILL.md
- .claude/skills/sales-followup-email-writing/SKILL.md
- .claude/skills/sales-followup-email-evaluation/SKILL.md
- .claude/skills/sales-followup-word-output/SKILL.md
- knowledge/01_core_policy.md
- knowledge/02_sales_tone_extraction.md
- knowledge/03_seasonal_research.md
- knowledge/04_email_generation_rules.md
- knowledge/05_quality_rubric_and_personas.md
- knowledge/benchmark_playbooks/suzue_benchmark.md
- knowledge/rag/suzue_vector_store.md
- knowledge/07_self_improvement_agent_loop.md

をルールとして使ってください。

Step 1. 入力確認
- 商談文字起こし
- `knowledge/video_catalog.md` 
- 動画カタログ
- 送付日
- 出力形式
を確認してください。

Step 2. 初稿生成
- `sales-transcript-intake-analysis` で顧客発話と営業発話を分けてください。
- `sales-transcript-intake-analysis` で営業担当の実発話から口調を抽出してください。
- 発話にない余白表現は使わないでください。
- `sales-seasonal-greeting-research` で季語は毎回調査してください。
- `sales-followup-email-writing` でメール初稿を作ってください。
- `knowledge/benchmark_playbooks/suzue_benchmark.md` を必ず読み、文字起こしベースの営業型として、商談フィードバック要素の `benchmarkCoach`、`winningPatterns`、`phasePlaybooks`、`customerAttributePlaybooks` に反映してください。顧客が話していない事実を足す根拠にはしないでください。
- OpenAI Vector Storeが利用可能な場合は、メール本文を書く前に `knowledge/rag/suzue_vector_store.md` に従い、今回商談の論点で鈴江商談RAGを検索してください。検索結果は似た場面の営業型として `benchmarkCoach`、`winningPatterns`、`phasePlaybooks`、`customerAttributePlaybooks`、価格質問対応、不安が出た時の戻し方、クロージングに反映してください。
- RAG検索結果は顧客事実の根拠にしないでください。顧客送付用本文に鈴江商談名、検索結果、原文引用、RAG実行ログを出さないでください。使えない場合は静的ベンチマークへフォールバックしてください。
- 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューは出力しないでください。
- メール本文を書く前に、`sales-analysis-app-openai-next` の思想に沿って商談フィードバック要素を内部抽出してください。必須項目は 総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks です。
- 社内確認用docx/MDに出す商談フィードバック要素では、`overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名を表示しないでください。日本語見出しと自然文に変換してください。
- フィードバックはトップ営業マンが営業担当に目の前で指導している形にしてください。箇条書きの羅列ではなく、「この商談はこう見る」「次回はこう聞く」「この場面ではこう返す」という実践文を中心にしてください。
- 社内確認用には、Driver / Driving、Analytical、Amiable、Expressive の4スタイル別に、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を作ってください。差し替え段落だけで終わらせないでください。
- 各スタイルに、顧客反応シグナル、効く理由、次回質問、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意を営業フィードバックとして入れてください。
- 4スタイルの違いは語尾や文量だけで出さないでください。Driverは結論・主導権・次アクション、Analyticalは根拠・条件・例外、Amiableは安心・合意形成・相談導線、Expressiveは未来像・承認・ストーリーで分けてください。
- 各スタイルに、価格質問対応、不安が出た時の戻し方、クロージング、ストレス反応へのリカバリーを入れてください。
- 価格・費用質問への返し方では、価格は隠さず、ただし価格だけで終わらせず、目的・作業時間・予算感・導入時期・意思決定者・不安の種類を確認してからプラン判断へ戻してください。

Step 3. 評価エージェントを立てる
`sales-followup-email-evaluation` を使い、以下の6つの評価エージェントでレビューしてください。

1. Source-Fact Agent
2. Sales-Tone Agent
3. Customer-Human Agent
4. Risk-Compliance Agent
5. Ops-Formatting Agent
6. Final-Whole-Check Agent

各エージェントは必ず以下で出してください。
- status: OK / 要修正
- findings:
- evidence:
- required_fix:
- blocking:

Step 4. 修正
- `status: 要修正` またはblocking=yesがある場合は修正してください。
- 修正は、事実誤り、危険表現、営業口調、会話反映、運用ミス、季語、自然さの順で行ってください。
- 修正した箇所は最終確認に短く反映してください。詳細な評価記録や改善記録は出力しないでください。

Step 5. 再評価
- 同じ評価エージェントで再評価してください。
- 全評価がOKになるまで繰り返してください。
- 3回改善してもOKにならない場合は、足りない入力情報を明記して止めてください。

Step 6. 最終全体チェック
Final-Whole-Checkは重い全文再読ではなく、軽量チェックリスト方式で行ってください。新しい文章案は作らず、NGがある場合だけ最小修正してください。

```text
Final-Whole-Check:
- 顧客送付用に社内情報なし
- 黄色タグ / ZOOM / 固有情報OK
- 参考動画URLが実URL
- 成果保証・審査保証・危険表現なし
- 営業口調・余白表現OK
- 社内確認用4スタイル全文案あり
- 英語キー・評価ログ・残リスクなし
- Drive保存・Gmail下書き作成に進める
```

出力:
1. 最終メール本文
2. ソーシャルスタイル別全文メール案と商談フィードバック（社内確認用）
   - 商談フィードバックには 総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks を含める
3. 最終確認
4. Skill Used Check

営業口調抽出、季語調査結果、参考動画選定理由は内部根拠として使い、docxや最終回答の独立セクションには出さないでください。
評価ログと残リスクはdocxに出さないでください。
音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューはdocxにも最終出力にも出さないでください。
英語キーや `name=` 形式はdocxにも最終出力にも出さないでください。

Skill Used Checkには、使用したSkill、読んだKnowledge、評価実施有無、修正有無、Orchestration log、Output quality gate、Final-Whole-Check、Hook/settings、残リスクを必ず入れてください。評価エージェント別スコアは入れないでください。
```
