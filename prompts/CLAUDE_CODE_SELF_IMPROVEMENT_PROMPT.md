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
- メール本文を書く前に、`sales-analysis-app-openai-next` の思想に沿って商談フィードバック要素を内部抽出してください。必須項目は stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks です。
- 社内確認用には、Driver / Driving、Analytical、Amiable、Expressive の4スタイル別に、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を作ってください。差し替え段落だけで終わらせないでください。
- 各スタイルに、顧客反応シグナル、効く理由、次回質問、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意を営業フィードバックとして入れてください。
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
Final-Whole-Check Agentで以下を横断確認してください。
- 商談事実
- 営業口調
- 余白表現
- 季節の結び
- 参考動画URL前後の案内文
- URL前後の説明
- ZOOM URL：〇〇〇
- 黄色箇所
- 禁止表現
- Word出力可否

出力:
1. 最終メール本文
2. ソーシャルスタイル別全文メール案と商談フィードバック（社内確認用）
   - 商談フィードバックには stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks を含める
3. 最終確認
4. Skill Used Check

営業口調抽出、季語調査結果、参考動画選定理由は内部根拠として使い、docxや最終回答の独立セクションには出さないでください。
評価ログと残リスクはdocxに出さないでください。

Skill Used Checkには、使用したSkill、読んだKnowledge、評価実施有無、修正有無、Orchestration log、Output quality gate、Final-Whole-Check、Hook/settings、残リスクを必ず入れてください。評価エージェント別スコアは入れないでください。
```
