# Claude Code Skill Usage Check Prompt

最終納品前にSkill使用を確認するためのプロンプト。

```text
最終回答前に、以下を確認してください。

1. `sales-followup-email-from-transcript` オーケストレーターSkillを使ったか
2. 文字起こし分析で `sales-transcript-intake-analysis` を使ったか
3. 季語調査で `sales-seasonal-greeting-research` を使ったか
4. メール作成で `sales-followup-email-writing` を使ったか
5. 評価改善で `sales-followup-email-evaluation` を使ったか
6. Word出力指定がある場合、`sales-followup-word-output` を使ったか
7. Skillが自動起動しなかった場合、該当 `.claude/skills/*/SKILL.md` を読んだか
8. `CLAUDE.md` のルールを守ったか
9. 必須Knowledgeを読んだか
   - `knowledge/benchmark_playbooks/suzue_benchmark.md` を読み、営業後メール生成と社内確認用の商談フィードバック要素に反映したか
10. OpenAI Vector Storeが利用可能な場合、`knowledge/rag/suzue_vector_store.md` に従って今回商談の論点で鈴江商談RAGを検索し、社内確認用の勝ち筋・ベンチマーク指導へ反映したか。使えない場合は静的ベンチマークへフォールバックしたか
11. RAG検索結果を顧客事実の根拠にせず、顧客送付用本文やdocxに鈴江商談名、検索結果、原文引用、RAG実行ログを出していないか
12. 評価エージェント確認結果を点数なしで残したか
13. 指摘があった場合、AIで修正して再評価し、修正内容と再評価結果を残したか
14. `Orchestration log` に、サブエージェント使用有無、並列/直列、使えない場合の理由を残したか
15. 顧客送付用本文に `[黄色]`、`[/黄色]`、`参考動画URL：〇〇〇`、社内確認情報、残リスクが残っていないか
16. 顧客送付用docxと社内確認用docxを分けたか
17. 社内確認用に4スタイル別の全文メール案があるか（Driver / Driving、Analytical、Amiable、Expressiveすべて、件名から署名・固定資料URL・固定フォームURLまで）
18. 社内確認用に商談フィードバック要素（総合概要 / 顧客インサイト / 認知バイアス / 期待値のズレ / 良かった点 / 改善ポイント / AIコーチングカード / 再現する勝ち筋 / stageStrategy / phasePlaybooks / customerSignals / temperature / nextBestAction / hearingQuestions / recommendedAnswer / benchmarkCoach / contextBridge / customerAttributePlaybooks）があるか
19. 4スタイル別の営業フィードバックに、顧客反応シグナル、次回質問、返答例、価格質問対応、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモ、属性別対応、リスク注意があるか
20. 4スタイル別案が、語尾や文量だけでなく、価格対応、不安対応、クロージング、ストレス時の戻し方まで分岐しているか
21. 社内確認用docx/MDに `overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名が残っていないか
22. 商談フィードバックが、トップ営業マンが目の前で指導している自然文になっているか。箇条書きの羅列だけで終わっていないか
23. 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューを出力していないか
24. Final-Whole-Check AgentがOKか
25. Hookがある場合、Stop Hookの完了条件を満たしているか

最終回答には必ず以下を入れてください。

Skill Used Check:
- Skills:
- Knowledge read:
- Evaluation:
- Repair loop:
- Orchestration log:
- Output quality gate:
- Final-Whole-Check:
- Hooks/settings:
- Remaining risk:
```
