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
- 営業メール雛形
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

Step 3. 評価エージェントを立てる
`sales-followup-email-evaluation` を使い、以下の6つの評価エージェントでレビューしてください。

1. Source-Fact Agent
2. Sales-Tone Agent
3. Customer-Human Agent
4. Risk-Compliance Agent
5. Ops-Formatting Agent
6. Final-Whole-Check Agent

各エージェントは必ず以下で出してください。
- score:
- findings:
- evidence:
- required_fix:
- blocking:

Step 4. 修正
- scoreが90点未満、Source-Fact/Riskが95点未満、またはblocking=yesがある場合は修正してください。
- 修正は、事実誤り、危険表現、営業口調、会話反映、運用ミス、季語、自然さの順で行ってください。
- 修正した箇所と理由を改善ログに残してください。

Step 5. 再評価
- 同じ評価エージェントで再評価してください。
- 全評価が基準を超えるまで繰り返してください。
- 3回改善しても超えない場合は、足りない入力情報を明記して止めてください。

Step 6. 最終全体チェック
Final-Whole-Check Agentで以下を横断確認してください。
- 商談事実
- 営業口調
- 余白表現
- 季語と参照元
- 参考動画の選定理由
- URL前後の説明
- ZOOM URL：〇〇〇
- 黄色箇所
- 禁止表現
- Word出力可否

出力:
1. 最終メール本文
2. 営業口調抽出結果
3. 季語調査結果と参照元
4. 評価エージェント別レビュー
5. 改善ログ
6. 最終全体チェック結果
7. Skill Used Check

Skill Used Checkには、使用したSkill、読んだKnowledge、評価エージェント別スコア、修正有無、Orchestration log、Output quality gate、Final-Whole-Check、Hook/settings、残リスクを必ず入れてください。
```
