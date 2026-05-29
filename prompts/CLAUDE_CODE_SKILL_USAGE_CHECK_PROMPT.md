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
10. 評価エージェント別スコアを残したか
11. 指摘があった場合、AIで修正して再評価し、修正内容と再評価結果を残したか
12. `Orchestration log` に、サブエージェント使用有無、並列/直列、使えない場合の理由を残したか
13. 顧客送付用本文に `[黄色]`、`[/黄色]`、`参考動画URL：〇〇〇`、評価ログ、残リスクが残っていないか
14. 顧客送付用docxと社内確認用docxを分けたか
15. Final-Whole-Check AgentがOKか
16. Hookがある場合、Stop Hookの完了条件を満たしているか

最終回答には必ず以下を入れてください。

Skill Used Check:
- Skills:
- Knowledge read:
- Evaluation agents and scores:
- Repair loop:
- Orchestration log:
- Output quality gate:
- Final-Whole-Check:
- Hooks/settings:
- Remaining risk:
```
