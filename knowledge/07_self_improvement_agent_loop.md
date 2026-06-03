# 07 Self Improvement Agent Loop

## 目的

営業後送付メールを、生成して終わりにしない。

評価エージェントが分担してチェックし、足りない点があれば修正担当AIが直し、再評価してから納品する。
評価エージェント別スコアは出力せず、OK / 要修正とblockingで判断する。

Routineでは速度を優先し、毎回のサブエージェント分担は行わない。
Source-Fact / Sales-Tone / Customer-Human / Risk-Compliance / Ops-Formatting / Final-Whole-Check の6観点を、1回の統合軽量チェックリストにまとめる。
独立エージェント評価は、ユーザーが明示的に求めた場合、またはblockingリスクが高い場合だけ使う。

## エージェント構成

Routineでは下記を個別実行せず、統合軽量チェックリストでまとめて確認する。
ユーザーが明示的に厳密評価を求めた場合、またはblockingリスクが高い場合だけ、Claude Codeでサブエージェント分担する。

使えない場合は、同じAIの中で以下の役割を分けて評価する。

| エージェント | 役割 | NG例 |
|---|---|---|
| Source-Fact Agent | 商談記録との事実一致、日付、次アクション、送付物を確認 | 顧客が言っていない不安を足している |
| Sales-Tone Agent | 営業担当の実発話に沿うか確認 | 発話にない `かと` を使っている |
| Customer-Human Agent | 顧客が人間味を感じるか確認 | 誰にでも送れる文章になっている |
| Risk-Compliance Agent | 成果保証、費用、契約、誤認リスクを確認 | `稼げます` のような断定 |
| Ops-Formatting Agent | 黄色箇所、ZOOM URL、動画URL前後、季語参照元を確認 | ZOOM URLが空、黄色箇所が多すぎる |
| Final-Whole-Check Agent | すべての修正後に横断確認 | 一部の修正で別のルールが壊れている |

## 評価エージェントの出力形式

Routineの統合軽量チェックでは、必ずこの形で出す。

```text
status: OK / 要修正
required_fix:
blocking:
```

厳密評価で各エージェントを個別実行する場合だけ、この形で出す。

```text
Agent:
status: OK / 要修正
findings:
evidence:
required_fix:
blocking:
```

`blocking` は、納品前に必ず直す必要があるものだけ `yes` にする。

## 改善ループ

1. Draft Writer が初稿を作る
2. Routineでは6観点の統合軽量チェックを1回行う。厳密評価時だけ5つの評価エージェントが評価する
3. Synthesis / Repair Agent が指摘を統合する
4. 重大度順に修正する
5. Routineでは同じ統合軽量チェックを再確認する。厳密評価時だけ同じ評価エージェントが再評価する
6. blockingなしになるまで繰り返す
7. RoutineではFinal-Whole-Checkを統合チェック内で見る。厳密評価時だけFinal-Whole-Check Agentが横断チェックする
8. NGが残っていれば該当箇所だけ直して再チェックする

## 合格条件

- Source-Fact Agent: OK
- Sales-Tone Agent: OK
- Customer-Human Agent: OK
- Risk-Compliance Agent: OK
- Ops-Formatting Agent: OK
- Final-Whole-Check Agent: OK

## 修正の優先順位

1. 事実誤り
2. 成果保証・危険表現
3. 営業担当の発話にない口調
4. 顧客との会話反映不足
5. ZOOM URL・黄色箇所・動画URLなど運用ミス
6. 季語のずれ
7. 細かい自然さ

## 止める条件

3回改善してもOKにならない場合は、文章を無理に整えない。

次のいずれかを報告する。

- 営業担当の発話量が足りない
- 顧客情報が不足している
- 次アクションが商談内で不明
- 季語を判断する送付日が不明
- `knowledge/video_catalog.md`に近い事例がない
