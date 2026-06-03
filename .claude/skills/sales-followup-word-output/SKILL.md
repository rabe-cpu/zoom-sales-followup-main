---
name: sales-followup-word-output
description: Create final Word/docx deliverables for Japanese sales follow-up emails, including yellow editable fields, ZOOM URL placeholder, summary docs, final checks, and output folder checklists.
---

# Sales Follow-up Word Output

## Purpose

営業後送付メールと社内確認情報を、Word出力にまとめる。評価の詳細記録は出さない。

## Workflow

1. Prepare Output Folder
   - 元ファイルを変更しない。
   - 新しいフォルダを作る。
   - 日付と版名をフォルダ名に入れる。

2. Create Word Files
   - 成果物一覧
   - 個別メール
   - 複数メールまとめ版
   - 社内確認用のソーシャルスタイル別全文メール案
   - 社内確認用の商談フィードバック要素
     - 総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ
     - 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋
     - stageStrategy / phasePlaybooks / customerSignals / temperature
     - nextBestAction / hearingQuestions / recommendedAnswer
     - benchmarkCoach / contextBridge / customerAttributePlaybooks
      - `knowledge/benchmark_playbooks/suzue_benchmark.md` を参照した文字起こしベースの営業型
   - 最終確認
   - 運用ルール
   - 評価ログと残リスクはWord/docxに出さない。
   - 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューはWord/docxに出さない。
   - `overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名はWord/docxに出さない。日本語見出しと自然文に変換する。
   - 商談フィードバック要素は、トップ営業マンが目の前で指導している形にする。箇条書きだけの分析メモにしない。

3. Highlight Fields
   - 営業が最後に書く箇所を黄色にする。
   - `ZOOM URL：〇〇〇` を黄色にする。
   - 不必要に色を増やさない。

4. Final File Check
   - ファイル数
   - docx存在
   - 黄色箇所
   - ZOOM URL
   - ソーシャルスタイル別全文メール案と商談フィードバック要素が社内確認用だけに入っているか
   - 最終確認
   - 元ファイル未変更

## Non-Negotiables

- 元ファイルを変更しない。
- 営業チェック箇所以外をむやみに黄色にしない。
- ソーシャルスタイル別メール案を顧客送付用docxに混ぜない。
- 鈴江ベンチマークは顧客事実の根拠にせず、顧客が話していない背景、金額、感情、成果期待を足さない。
- 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューを出さない。
- Word出力指定がある場合、Markdownだけで終わらせない。

## When Not To Use

- ユーザーが明確にWord出力不要と言っている場合。
- メール本文・営業チェック箇所がまだ確定していない場合。

## Pass Conditions

- 新しい出力フォルダにdocxが作成されている。
- 黄色箇所は営業入力欄と `ZOOM URL：〇〇〇` など必要箇所に限定されている。
- 社内確認用には、商談フィードバック要素が構造化され、総合概要、顧客インサイト、認知バイアス、期待値のズレ、良かった点、改善ポイント、AIコーチングカード、再現する勝ち筋、次回商談で使える質問・返答・ベンチマーク営業台本が入っている。
- 英語キーや `name=` 形式が表示されず、営業担当が次回どう話すか分かる指導文になっている。
- 元ファイル未変更、成果物一覧、最終確認結果が残っている。
