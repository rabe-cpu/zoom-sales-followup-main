---
name: sales-followup-email-evaluation
description: Evaluate and improve Japanese sales follow-up emails using source-fact, salesperson-tone, customer-human, risk-compliance, ops-formatting, and final-whole-check agents. Use before final delivery.
---

# Sales Follow-up Email Evaluation

## Purpose

営業後送付メールを、評価エージェントでチェックし、90点以上まで改善する。

## Evaluation Agents

- Source-Fact Agent: 事実・日付・次アクション
- Sales-Tone Agent: 営業口調・余白表現
- Customer-Human Agent: 人間味・会話反映
- Risk-Compliance Agent: 成果保証・危険表現
- Ops-Formatting Agent: 黄色箇所・ZOOM・動画・Word出力
- Final-Whole-Check Agent: 最終横断チェック

## Workflow

1. Run Agent Review
   - 各評価エージェントで評価する。
   - `score / findings / evidence / required_fix / blocking` を出す。

2. Repair
   - 90点未満、Source-Fact/Riskが95点未満、またはblocking=yesなら修正する。
   - 修正は事実誤り、危険表現、営業口調、会話反映、運用ミス、季語、自然さの順で行う。

3. Re-evaluate
   - 同じ評価エージェントで再評価する。
   - 全基準を超えるまで繰り返す。

4. Stop Rule
   - 3回改善しても届かない場合は、不足情報を明記して止める。

5. Final Check
   - Final-Whole-Check AgentがOKになるまで納品しない。

## Output

```text
Evaluation summary:
Agent scores:
Repair log:
Final-Whole-Check:
Remaining risk:
```

## When Not To Use

- まだメール初稿がなく、素材分析だけを行う場合。
- 人間レビューだけを求められており、AIによる修正を行わない場合。

## Pass Conditions

- 6つの評価エージェントすべてに `score / findings / evidence / required_fix / blocking` がある。
- Source-Fact と Risk-Compliance は95点以上、その他は90点以上になっている。
- 90点未満またはblockingありの指摘は、修正内容と再評価結果が残っている。
