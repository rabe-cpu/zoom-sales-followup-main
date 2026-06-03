# CLAUDE.md

このプロジェクトは、商談文字起こしから営業後送付メールを作るためのClaude Code用プロジェクトです。

Claude Codeをこのフォルダで起動したら、以下を必ず守ってください。

## 最重要ルール

- ユーザーが商談文字起こし、MTG文字起こし、Zoom文字起こし、JamRoll文字起こし、CSV、txt、商談zipを渡したら、必ず `sales-followup-email-from-transcript` Skillを使う。
- Word/docx出力、黄色チェック欄、ZOOM URL差し替え欄まで一気通貫で求められた場合は、統合Skill `sales-followup-human-docx` も使う。
- さらに工程ごとに、必要な専門Skillを使う。
  - `sales-transcript-intake-analysis`
  - `sales-seasonal-greeting-research`
  - `sales-followup-email-writing`
  - `sales-followup-email-evaluation`
  - `sales-followup-word-output`
  - `sales-followup-human-docx`
  - `sales-tone-knowledge-register`
- Skillが自動起動しない場合でも、統括Skillと該当工程の `.claude/skills/*/SKILL.md` を読んでから作業する。
- 顧客発話と営業発話を分離し、営業担当の実発話だけを口調反映に使う。
- `かと`、`かなと`、`できればと`、`見ていただけると` は、営業担当の実発話にある場合だけ使う。発話にない場合はゼロ。
- 季語・時候の挨拶は毎回調査する。過去の表現を使い回さない。
- 参考動画は必ず `knowledge/video_catalog.md` を優先して読み、顧客の属性・不安・判断軸に近い動画を選ぶ。
- メール本文を書く前に、`sales-analysis-app-openai-next` の思想に沿って商談フィードバック要素を内部抽出する。必須項目は stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks。
- 出力前に評価エージェントを通す。
- サブエージェントが使える場合は、Source/Tone/Human/Risk/Opsを独立評価として分け、最後にFinal-Whole-Checkを実行する。使えない場合も同一AI内で6ロールに分け、`Orchestration log` に理由を残す。
- 顧客送付用本文に `[黄色`、`[/黄色]`、`参考動画URL：〇〇〇`、社内確認情報、残リスク、営業口調抽出を残さない。
- 顧客送付用docxと社内確認用docxを分ける。
- 最後に `Final-Whole-Check Agent` で横断チェックし、NGがあればAIで修正して再評価する。
- 最終回答には必ず `Skill Used Check` を入れ、使用したSkill、読んだKnowledge、評価実施有無、修正有無、Hook/Final Checkの結果、残リスクを短く書く。評価エージェント別スコアは出さない。

## 読むべきナレッジ

詳細ルールは以下を参照する。

@knowledge/01_core_policy.md
@knowledge/02_sales_tone_extraction.md
@knowledge/sales_persons/_index.md
@knowledge/03_seasonal_research.md
@knowledge/04_email_generation_rules.md
@knowledge/05_quality_rubric_and_personas.md
@knowledge/07_self_improvement_agent_loop.md
@knowledge/08_official_claude_code_setup.md
@knowledge/example_success_email.md

## Claude Code公式構成

このフォルダはClaude Code公式構成に合わせている。

- Project memory: `CLAUDE.md`
- Project Skills: 統括 `.claude/skills/sales-followup-email-from-transcript/SKILL.md`、工程別 `.claude/skills/sales-*/SKILL.md`、統合DOCX Skill `.claude/skills/sales-followup-human-docx/SKILL.md`
- Project subagents: `.claude/agents/*.md`
- Project hooks/settings: `.claude/settings.json`

Claude Code内では、必要に応じて以下を確認する。

- `/memory`: `CLAUDE.md` が読み込まれているか確認
- `/hooks`: Stop Hook が有効か確認
- `/agents`: 評価エージェントが見えるか確認
- `What Skills are available?`: 7つのSales系Skillが見えるか確認

## 標準実行フロー

1. 入力ファイル一覧を作る
2. `sales-transcript-intake-analysis` で商談文字起こしを分析する
3. `sales-tone-knowledge-register` で営業担当の登録有無を確認し、未登録なら `knowledge/sales_persons/{担当}.md` を新規作成、既存なら `.draft.md` でdiff提示する
4. `sales-seasonal-greeting-research` で季語を調査し、参照元を残す
5. `sales-followup-email-writing` でメール初稿を作る
6. `sales-followup-email-evaluation` で評価・改善・再評価する。評価エージェント別スコアは出さず、OK/要修正と修正内容だけ残す
7. `sales-followup-human-docx` のOrchestrationに従い、サブエージェントまたは同一AI内ロールの実行ログを残す
   - 社内確認用には、Driver / Driving、Analytical、Amiable、Expressive の4スタイル別に、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を入れる
   - 社内確認用の商談フィードバック要素には、stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks を入れる
   - 各スタイルに商談フィードバック要素（顧客反応シグナル、次回質問、返答例、価格質問対応、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意）を入れる
8. 出力失敗パターンをチェックし、顧客送付用と社内確認用を分ける
9. `Final-Whole-Check Agent` で最終確認する
10. Word指定がある場合は `sales-followup-word-output` で出力する
11. `Skill Used Check` を最終回答に入れる

## 最終回答に必ず含めるもの（短縮形・標準）

短縮形を標準とする。Stop Hookの必須キーは満たしつつ、対話の圧迫感を最小にするため、4行構成で固定する。

```text
Skill Used Check:
- Skills: <発動Skill列挙> / 発動あり・なし
- Knowledge: CLAUDE.md / knowledge読込あり
- 評価: 6ロール確認済み / 修正有無 / サブエージェント / Output quality gate / Final-Whole-Check
- 残リスク / remaining risk: <なし、または1〜2行>
```

書き方ルール:

- Word/.docx/黄色/ZOOM URL を出力した回は、Skills行に `sales-followup-word-output` を必ず含める。
- 評価行には点数や6ロール別スコアを出さず、確認済みか、修正したか、Final-Whole-Checkが通ったかだけを書く。
- 残リスクが本当にない場合も「残リスク / remaining risk: なし」と書く（キー欠落でHookが落ちるため）。
- 詳細を残したい場合のみ、別途長文版を補足できる（標準は短縮形）。

---

## Routine自動実行モード

このセッションが Routine（スケジュール実行 / Run now）として起動された場合は、
ユーザーの入力を待たず、@routine/ROUTINE_PROMPT.md の手順を最初から最後まで自走で実行する。

- 対象は「未処理の商談録画」のみ（共有ドライブの処理済み台帳 `processed_meetings.json` で判定。冪等）
- 1件ずつ直列で：メール生成 → 共有ドライブ保存 → 台帳更新、最後に Chatwork 通知
- 最終送信はしない（人間が社内確認して手動送信）
- 詳細手順は @routine/ROUTINE_PROMPT.md、失敗時は @routine/MANUAL_FALLBACK.md を参照
