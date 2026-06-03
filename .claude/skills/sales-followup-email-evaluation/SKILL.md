---
name: sales-followup-email-evaluation
description: Evaluate and improve Japanese sales follow-up emails using source-fact, salesperson-tone, customer-human, risk-compliance, ops-formatting, and final-whole-check agents. Use before final delivery.
---

# Sales Follow-up Email Evaluation

## Purpose

営業後送付メールを、評価エージェントでチェックし、全観点が合格するまで改善する。
評価エージェント別スコアは出力しない。判断は `status: OK / 要修正` と `blocking` で残す。

## Evaluation Agents

- Source-Fact Agent: 事実・日付・次アクション
- Sales-Tone Agent: 営業口調・余白表現
- Customer-Human Agent: 人間味・会話反映
- Risk-Compliance Agent: 成果保証・危険表現
- Ops-Formatting Agent: 黄色箇所・ZOOM・動画・Word出力
- Final-Whole-Check Agent: 最終横断チェック。ただしRoutineでは軽量チェックリスト方式を優先し、全文再読や再生成をしない。

## Workflow

1. Run Agent Review
   - 各評価エージェントで評価する。
   - `status / findings / evidence / required_fix / blocking` を出す。

2. Repair
   - `status: 要修正` または `blocking=yes` なら修正する。
   - 修正は事実誤り、危険表現、営業口調、会話反映、運用ミス、季語、自然さの順で行う。

3. Re-evaluate
   - 同じ評価エージェントで再評価する。
   - 全観点がOKになるまで繰り返す。

4. Stop Rule
   - 3回改善してもOKにならない場合は、不足情報を明記して止める。

5. Final Check
   - Final-Whole-CheckがOKになるまで納品しない。
   - Routineでは重いサブエージェントを立てず、30〜60秒の軽量チェックリストで確認してよい。
   - Final-Whole-Checkは全成果物の再生成、全文VTT再読、4スタイル全文の再レビューをしない。NGを見つけた時だけ最小修正する。

## Output

```text
Evaluation summary:
Evaluation status:
Repair log:
Final-Whole-Check:
Remaining risk:
```

## When Not To Use

- まだメール初稿がなく、素材分析だけを行う場合。
- 人間レビューだけを求められており、AIによる修正を行わない場合。

## Pass Conditions

- Source-Fact / Sales-Tone / Customer-Human / Risk-Compliance / Ops-Formatting は `status / findings / evidence / required_fix / blocking` がある。
- Final-Whole-Checkは、Routineでは軽量チェックリスト8項目がOKであれば合格とする。
- 全観点がOKになっている。
- `status: 要修正` または `blocking=yes` の指摘は、修正内容と再評価結果が残っている。
- 評価エージェント別スコアを最終回答や社内確認用に出していない。
