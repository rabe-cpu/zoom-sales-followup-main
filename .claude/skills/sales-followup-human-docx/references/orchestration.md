# Subagent Orchestration

## Goal

商談後メール作成で、分析、文体、リスク、Word出力の確認を1つの視点に寄せない。
Claude Codeで `.claude/agents/` が使える場合は、サブエージェントで分担する。
Codexでユーザーがサブエージェントや並列実行を明示した場合も、同じ分担で実行する。

## Team Assignment

### Phase A: Draft前の並列分析

可能なら独立に並列実行する。

| Lane | Agent/Role | Responsibility |
|---|---|---|
| Source lane | Source-Fact Agent | 商談事実、日付、約束、次回予定、送付物を抽出 |
| Tone lane | Sales-Tone Agent | 営業担当の実発話、余白表現、禁止表現を抽出 |
| Human lane | Customer-Human Agent | 顧客との会話冒頭に入れる話題、温度感を抽出 |

### Phase B: Draft後の並列評価

メール初稿後に並列評価する。

| Lane | Agent/Role | Responsibility |
|---|---|---|
| Fact review | Source-Fact Agent | 本文が商談事実と一致するか |
| Tone review | Sales-Tone Agent | 口調が営業発話に準拠しているか |
| Human review | Customer-Human Agent | 人間味、会話反映、AIっぽさを評価 |
| Risk review | Risk-Compliance Agent | 成果保証、断定、契約/費用リスクを評価 |
| Ops review | Ops-Formatting Agent | Word、黄色欄、ZOOM URL、動画URL前後説明を評価 |

### Phase C: Repair

未達またはblockingがある場合、メインAIが修正する。
修正後、該当Agent/Roleだけ再評価する。
最大2回改善する。

### Phase D: Final Gate

Final-Whole-Check Agentを最後に1回実行する。
全Agentの指摘、修正ログ、Word出力、黄色欄、Skill Used Check、残リスクを横断確認する。

## Required Orchestration Log

最終回答またはWord評価ログに以下を残す。

```text
Orchestration log:
- Mode: subagents / same-AI roles
- Parallel lanes:
- Sequential gates:
- Agents used:
- Agents not used and reason:
- Repair loops:
- Final-Whole-Check:
```

## Fallback Rule

Claude Codeで `/agents` に対象エージェントが表示されない場合は、同一AI内でロール分担する。
その場合も、`same-AI roles` と明記し、6 Agent相当の評価を省略しない。

## Pass Conditions

- Draft前にSource/Tone/Humanの分析がある。
- Draft後にFact/Tone/Human/Risk/Opsの評価がある。
- 最後にFinal-Whole-Checkがある。
- サブエージェントを使ったか、使えない場合の理由が記録されている。
