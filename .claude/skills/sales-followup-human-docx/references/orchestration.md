# Subagent Orchestration

## Goal

商談後メール作成で、分析、文体、リスク、Word出力の確認を1つの視点に寄せない。
Routineでは速度を優先し、下記の分担を毎回は実行しない。
Source-Fact / Sales-Tone / Customer-Human / Risk-Compliance / Ops-Formatting / Final-Whole-Check の6観点を1回の統合軽量チェックリストにまとめる。
Claude Codeでユーザーが「厳密評価」「6ロールで確認」を明示した場合、またはblockingリスクが高い場合だけ、下記のサブエージェント分担を使う。

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

RoutineではFinal-Whole-Check Agentを独立実行しない。統合軽量チェックリストに含める。
厳密評価時だけ、全Agentの指摘、修正ログ、Word出力、黄色欄、Skill Used Check、残リスクを横断確認する。

## Required Orchestration Log

最終確認に以下を短く残す。

```text
Orchestration log:
- Mode: integrated-lightweight / subagents / same-AI roles
- Parallel lanes:
- Sequential gates:
- Agents used:
- Agents not used and reason:
- Repair loops:
- Final-Whole-Check:
```

## Fallback Rule

Routineでは `/agents` の有無に関係なく `integrated-lightweight` を標準とする。
ユーザーが厳密評価を明示した場合に `/agents` が使えなければ、`same-AI roles` と明記し、6 Agent相当の評価を省略しない。

## Pass Conditions

- Routineでは6観点の統合軽量チェックがある。
- 厳密評価時はDraft前にSource/Tone/Humanの分析、Draft後にFact/Tone/Human/Risk/Opsの評価がある。
- Final-Whole-CheckはRoutineでは統合、厳密評価時は最後に独立確認する。
- サブエージェントを使ったか、使わない場合は `integrated-lightweight` と記録されている。
