---
name: sales-followup-email-evaluation
description: Evaluate and improve Japanese sales follow-up emails using source-fact, salesperson-tone, customer-human, risk-compliance, ops-formatting, and final-whole-check agents. Use before final delivery.
---

# Sales Follow-up Email Evaluation

## Purpose

営業後送付メールを、評価エージェントでチェックし、全観点が合格するまで改善する。
評価エージェント別スコアは出力しない。判断は `status: OK / 要修正` と `blocking` で残す。
Routineでは速度を優先し、6つの独立エージェントを毎回立てない。6観点を1つの統合チェックリストに畳み込み、NGがある場合だけ最小修正する。

## Evaluation Agents

- Source-Fact Agent: 事実・日付・次アクション
- Sales-Tone Agent: 営業口調・余白表現
- Customer-Human Agent: 人間味・会話反映
- Risk-Compliance Agent: 成果保証・危険表現
- Ops-Formatting Agent: 黄色箇所・ZOOM・動画・Word出力
- Final-Whole-Check Agent: 最終横断チェック。ただしRoutineでは軽量チェックリスト方式を優先し、全文再読や再生成をしない。

## Workflow

1. Routine Lightweight Review
   - Routine実行では、Source-Fact / Sales-Tone / Customer-Human / Risk-Compliance / Ops-Formatting / Final-Whole-Check を1回の統合チェックリストで確認する。
   - サブエージェント並列、全文VTT再読、4スタイル全文の再レビューは行わない。
   - 入力は、商談事実サマリー、顧客送付用本文、社内確認用の主要見出し、黄色/ZOOM/固有情報、リスク候補だけに限定する。
   - 出力は `status: OK / 要修正`、`blocking`、`required_fix` だけでよい。各ロールごとの詳細findingsはRoutineでは省略する。

2. Full Agent Review
   - ユーザーが明示的に「厳密評価」「レビューを厚く」「6ロールで確認」と依頼した場合だけ、各評価エージェントで評価する。
   - その場合は `status / findings / evidence / required_fix / blocking` を出す。

3. Repair
   - `status: 要修正` または `blocking=yes` なら修正する。
   - 修正は事実誤り、危険表現、営業口調、会話反映、運用ミス、季語、自然さの順で行う。

4. Re-evaluate
   - Routineでは、修正後に統合チェックリストだけを再確認する。
   - 同じ評価エージェントでの個別再評価は、blocking修正があった場合、またはユーザーが明示した場合だけ行う。

5. Stop Rule
   - 3回改善してもOKにならない場合は、不足情報を明記して止める。

6. Final Check
   - Routineでは、Final-Whole-Checkを独立工程として追加で走らせない。上記の統合チェックリスト内に含める。
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

- Routineでは、統合チェックリスト8項目がOKであれば合格とする。
- Source-Fact / Sales-Tone / Customer-Human / Risk-Compliance / Ops-Formatting の個別 `findings / evidence` は、通常Routineでは不要。
- 全観点がOKになっている。
- `status: 要修正` または `blocking=yes` の指摘は、修正内容と再評価結果が残っている。
- 評価エージェント別スコアを最終回答や社内確認用に出していない。
