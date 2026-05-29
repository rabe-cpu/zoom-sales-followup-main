---
name: sales-followup-email-from-transcript
description: Create Japanese post-sales follow-up emails and Word outputs from sales meeting transcripts, MTG文字起こし, Zoom/JamRoll CSV or txt files, and 商談zip records. Use when the user asks for営業後送付メール, 商談後メール, meeting transcript email generation, salesperson tone extraction, seasonal greeting research, evaluation agents, or Claude Code reusable workflow packaging.
---

# Sales Follow-up Email From Transcript

## Purpose

商談文字起こしから、営業担当の実発話・顧客との会話内容・送付日の季節感に準拠した営業後送付メールを作る。

このSkillは「人っぽく崩す」ためではなく、「実際の会話と営業担当の発話に準拠する」ために使う。

## Required Reading

商談後メールを作る作業では、作業開始時に以下を読む。時間がない場合でも `01_core_policy`、`02_sales_tone_extraction`、`04_email_generation_rules`、`05_quality_rubric_and_personas` は省略しない。

- `../../../knowledge/01_core_policy.md`
- `../../../knowledge/02_sales_tone_extraction.md`
- `../../../knowledge/03_seasonal_research.md`
- `../../../knowledge/04_email_generation_rules.md`
- `../../../knowledge/05_quality_rubric_and_personas.md`
- `../../../knowledge/07_self_improvement_agent_loop.md`
- `../../../knowledge/08_official_claude_code_setup.md`

## Specialized Skills

このSkillは全体オーケストレーター。実作業では、工程ごとに以下の専門Skillも使う。

- `sales-transcript-intake-analysis`: 文字起こし分析、顧客/営業発話分離、事実抽出、営業口調根拠
- `sales-seasonal-greeting-research`: 送付日に合う季語・時候の挨拶調査
- `sales-followup-email-writing`: 雛形に沿った営業後メール初稿作成
- `sales-followup-email-evaluation`: 評価エージェント、自己改善、Final-Whole-Check
- `sales-followup-word-output`: Word出力、黄色箇所、成果物一覧、出力検証

## Workflow

1. Source Inventory
   - 入力ファイル、雛形、動画カタログ、出力先を列挙する。
   - 読めないファイルがあれば明記する。

2. Transcript Analysis
   - Use `sales-transcript-intake-analysis`.
   - 顧客発話と営業発話を分離する。
   - 顧客の背景、悩み、判断軸、反応、次回予定、営業が約束した送付物を抽出する。

3. Salesperson Tone Extraction
   - 営業担当の実発話だけから、頻出語、依頼表現、締め方、距離感、余白表現を抽出する。
   - 顧客発話を営業口調として扱わない。

4. Slack Expression Gate
   - `かと`、`かなと`、`できればと`、`見ていただけると` は営業担当の発話にある場合だけ使う。
   - 発話にない場合はゼロ。
   - 発話にある場合でも1通あたり0〜1回を基本にする。

5. Seasonal Research
   - Use `sales-seasonal-greeting-research`.
   - 送付日を確認する。
   - 季語・時候の挨拶を毎回調査する。
   - 二十四節気は公的または信頼できる情報で確認する。

6. Video Recommendation
   - 顧客の属性・不安・判断軸に近い動画を選ぶ。
   - `なぜこの動画か` → `URL` → `見る観点を1文` の形にする。

7. Draft Email
   - Use `sales-followup-email-writing`.
   - 冒頭に商談で話した内容を2〜4文で入れる。
   - 黄色箇所は営業が最後に触るべき箇所だけにする。
   - ZOOMが必要なら `ZOOM URL：〇〇〇` を残す。

8. Evaluation Agents
   - Use `sales-followup-email-evaluation`.
   - `source-fact-agent`
   - `sales-tone-agent`
   - `customer-human-agent`
   - `risk-compliance-agent`
   - `ops-formatting-agent`
   - `final-whole-check-agent`

9. Repair Loop
   - 90点未満、Source-Fact/Riskが95点未満、またはblockingがあれば修正する。
   - 修正後、同じ評価エージェントで再評価する。
   - 3回改善しても届かない場合は不足入力を明記して止める。

10. Final Output
   - Use `sales-followup-word-output` when Word/docx output is requested.
   - メール本文、抽出した営業口調、季語調査、動画選定理由、評価ログ、最終チェック結果を出す。
   - 最終回答に `Skill Used Check` を含め、使った全Skillを列挙する。

## Non-Negotiables

- 営業担当がMTG中に言っていない余白表現を、人間味として足さない。
- `伝わってまいりました` は、営業担当の実発話または雛形に明確な根拠がある場合だけ使う。根拠が薄い場合は `伝わってきました`、`感じました`、`受け取りました` など自然な表現に寄せる。
- 顧客が言っていない背景・感情・成果期待を盛らない。
- 収益保証・成果保証の表現を使わない。
- 季語は毎回調査する。
- 評価エージェントとFinal-Whole-Checkを通さずに納品しない。

## When Not To Use

- 商談文字起こしや面談メモがなく、一般的な定型お礼メールだけを作る場合。
- 会社公式の法務文書、契約説明、成果保証に関わる表現を新規に作る場合。
- 営業担当個人の口調ではなく、ブランド文体へ完全統一する場合。

## Pass Conditions

- 6つのSales系Skillのうち、該当工程のSkill利用または明示読込が `Skill Used Check` に残っている。
- Source-Fact、Sales-Tone、Customer-Human、Risk-Compliance、Ops-Formatting、Final-Whole-Check の評価結果が残っている。
- 90点未満またはblockingありの項目は、修正ログと再評価結果が残っている。
