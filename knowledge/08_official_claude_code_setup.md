# 08 Official Claude Code Setup

2026-05-14にClaude Code公式ドキュメントを確認して、このプロジェクト構成へ反映した内容。

## 公式仕様から反映したこと

### CLAUDE.md

Claude Codeでは、`CLAUDE.md` がプロジェクトメモリとして読み込まれる。

このプロジェクトでは、ルートに `CLAUDE.md` を置き、営業後送付メールの必須ルールとKnowledgeへのimportを記載した。

確認方法:

- Claude Code内で `/memory`

### Project Skills

プロジェクトSkillは `.claude/skills/<skill-name>/SKILL.md` に置く。

このプロジェクトでは以下に配置した。

```text
.claude/skills/sales-followup-email-from-transcript/SKILL.md
.claude/skills/sales-transcript-intake-analysis/SKILL.md
.claude/skills/sales-seasonal-greeting-research/SKILL.md
.claude/skills/sales-followup-email-writing/SKILL.md
.claude/skills/sales-followup-email-evaluation/SKILL.md
.claude/skills/sales-followup-word-output/SKILL.md
.claude/skills/sales-followup-human-docx/SKILL.md
```

Claude Codeでは、Skillのdescriptionが自動起動の判断に使われるため、統括Skillには `商談文字起こし`、`営業後送付メール`、`Zoom/JamRoll CSV`、`季語`、`評価エージェント` などのトリガー語を入れた。
工程別Skillには、文字起こし分析、季語調査、メール作成、評価改善、Word出力の各トリガー語を入れた。
統合DOCX Skillには、黄色欄、ZOOM URL、90点評価、Word出力などユーザー指摘事項のトリガー語を入れた。

確認方法:

- `What Skills are available?`
- または `.claude/skills/*/SKILL.md` を直接確認

### Project Subagents

プロジェクトSubagentは `.claude/agents/` にMarkdownファイルとして置く。

このプロジェクトでは、評価エージェントを以下で定義した。

```text
.claude/agents/source-fact-agent.md
.claude/agents/sales-tone-agent.md
.claude/agents/customer-human-agent.md
.claude/agents/risk-compliance-agent.md
.claude/agents/ops-formatting-agent.md
.claude/agents/final-whole-check-agent.md
```

確認方法:

- Claude Code内で `/agents`

### Hooks

Claude CodeのHooksは `.claude/settings.json` に設定できる。

このプロジェクトでは、公式形式のcommand HookとしてStop Hookを置き、`.claude/hooks/stop_sales_followup_gate.py` で最終回答前に以下が抜けていないかを確認する。

- `Skill Used Check`
- Skill使用またはSkill読込
- Knowledge読込
- 評価エージェント
- 評価エージェント別スコア
- 修正ループの有無
- Final-Whole-Check
- 残リスク

前提:

- Hookは `python .claude/hooks/stop_sales_followup_gate.py` を実行するため、Claude Codeを動かす環境で `python` コマンドが使える必要がある。
- `python` が使えない環境では、`.claude/settings.json` のcommandを環境に合わせて `py -3 ...` などへ変更する。
- Hookは最終回答の証跡不足を検出する補助であり、本文品質は評価エージェントとFinal-Whole-Checkで確認する。

Hook確認方法:

- Claude Code内で `/hooks`

## なぜHookを入れるか

この用途では、メールを作って終わりでは不十分。

必ず最後に、Skillを使ったか、Knowledgeを読んだか、評価エージェントを通したか、Final-Whole-CheckがOKかを確認する必要がある。

そのため、Stop Hookを最終ゲートとして入れている。

## 公式ドキュメント参照

- Claude Code Skills: https://code.claude.com/docs/en/skills
- Claude Code Memory / CLAUDE.md: https://code.claude.com/docs/en/memory
- Claude Code Hooks: https://code.claude.com/docs/en/hooks
- Claude Code Settings: https://code.claude.com/docs/en/settings
- Claude Code Subagents: https://code.claude.com/docs/en/sub-agents
