---
name: sales-transcript-intake-analysis
description: Analyze Japanese sales meeting transcripts, Zoom/JamRoll CSVs, txt files, and 商談zip records. Use before writing follow-up emails to separate customer speech from salesperson speech, extract facts, next actions, promises, and salesperson tone evidence.
---

# Sales Transcript Intake Analysis

## Purpose

商談文字起こしから、メール生成に必要な事実と営業口調の根拠を抽出する。

このSkillはメール本文を書かない。事実・発話・判断材料を整理する。

## Inputs

- 商談文字起こし: txt / csv / zip
- 参加者名
- 営業担当名
- 送付日
- 雛形・動画カタログがあれば参照可

## Workflow

1. Source Inventory
   - 読んだファイルを列挙する。
   - 読めないファイル、文字化け、Speaker不明を明記する。

2. Speaker Split
   - 顧客発話と営業発話を分ける。
   - Speaker名が崩れている場合は、文脈で仮判定し、信頼度を付ける。

3. Customer Context
   - 顧客背景
   - 悩み
   - 判断軸
   - 質問
   - 前向き反応
   - 不安
   - 次回予定
   - 営業が約束した送付物

4. Salesperson Tone Evidence
   - 営業担当の実発話から、頻出語、依頼表現、締め表現、余白表現を抜く。
   - `かと`、`かなと`、`できればと` は出現有無と回数を数える。
   - 顧客発話は営業口調として扱わない。

5. Output Analysis Block

```text
Source coverage:
Customer facts:
Customer decision axes:
Sales promises / next actions:
Salesperson tone evidence:
Slack expression gate:
Confidence / gaps:
```

## Non-Negotiables

- 顧客が言っていない内容を足さない。
- 営業発話にない余白表現を「人間味」として許可しない。
- 不明点は不明として出す。

## When Not To Use

- すでに信頼できる分析ブロックがあり、発話分離・事実抽出・営業口調抽出が完了している場合。
- 音声や文字起こしがなく、営業担当の記憶だけでメールを書く場合。

## Pass Conditions

- 顧客発話と営業発話の分離結果、または分離できない理由がある。
- 営業担当の実発話に基づく口調根拠がある。
- `かと` 系など余白表現の出現有無と使用可否が明記されている。
