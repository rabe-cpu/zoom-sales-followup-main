# 06 Claude Code Handoff

## 目的

このフォルダを受け取った別担当者が、Claude Codeで同じ品質の営業後送付メールを作れるようにする。

2026-05-14にClaude Code公式ドキュメントを確認し、実配置は以下に更新済み。

- `CLAUDE.md`
- `.claude/skills/sales-followup-email-from-transcript/SKILL.md`
- `.claude/skills/` 配下の工程別5 Skill
- `.claude/agents/*.md`
- `.claude/settings.json`
- `.claude/hooks/stop_sales_followup_gate.py`

## 推奨フォルダ構成

Claude Codeで作業するフォルダに、次を入れる。

```text
project/
  商談文字起こし/
  雛形/
  動画カタログ/
  CLAUDE.md
  .claude/
    settings.json
    hooks/
      stop_sales_followup_gate.py
    skills/
      sales-followup-email-from-transcript/
        SKILL.md
      sales-transcript-intake-analysis/
        SKILL.md
      sales-seasonal-greeting-research/
        SKILL.md
      sales-followup-email-writing/
        SKILL.md
      sales-followup-email-evaluation/
        SKILL.md
      sales-followup-word-output/
        SKILL.md
    agents/
      source-fact-agent.md
      sales-tone-agent.md
      customer-human-agent.md
      risk-compliance-agent.md
      ops-formatting-agent.md
      final-whole-check-agent.md
  knowledge/
  prompts/
  tests/
```

## Claude Codeでの実行手順

1. 作業フォルダをClaude Codeで開く
2. `/memory` で `CLAUDE.md` が読み込まれているか確認する
3. `/hooks` でStop Hookが有効か確認する
4. `/agents` で評価エージェントが見えるか確認する
5. `What Skills are available?` で7つのSales系Skillが見えるか確認する
6. `prompts/CLAUDE_CODE_MASTER_PROMPT.md` を貼る
7. 商談文字起こし、雛形、knowledge/video_catalog.md の場所を指定する
8. まず分析だけ出させる
9. 営業口調・余白表現・季語調査・動画選定理由を確認する
10. 問題なければメール本文を生成する
11. 評価エージェントを通す
12. 90点未満があればAIで改善・再評価させる
13. `Final-Whole-Check Agent` で最終チェックさせる
14. `Skill Used Check` を最終回答に入れさせる

## Claude Codeへの追加指示例

```text
このフォルダの CLAUDE.md、.claude/skills/ 配下の7つのSales系Skill、knowledge/ をルールとして使ってください。
商談文字起こしから営業後送付メールを作成してください。
営業担当の発話にない余白表現は使わないでください。
季語は送付日に合わせて毎回調査してください。
評価エージェントを通し、90点を超えるまで評価改善してください。
最後にSkill Used Checkを出してください。
```

## 他AIに渡す場合

Claude Code以外では、ファイル操作やWordの色付けが弱い場合がある。

その場合は、次の順で渡す。

1. `prompts/OTHER_AI_PROMPT.md`
2. 商談文字起こし
3. 雛形本文
4. `knowledge/video_catalog.md`
5. `knowledge/02_sales_tone_extraction.md`
6. `knowledge/05_quality_rubric_and_personas.md`

Word化や黄色ハイライトは、Claude Code / Codex 側で最後に処理するのが安定する。

## 起動後の確認

Claude Codeで開始したら、最初に以下を確認する。

```text
/memory
/hooks
/agents
What Skills are available?
```

期待状態:

- `CLAUDE.md` が読み込まれている
- `.claude/settings.json` のStop Hookが見える
- 6つの評価エージェントが見える
- `sales-followup-email-from-transcript` と `sales-followup-human-docx` を含む7つのSales系Skillが見える

## 運用上の注意

- 一度作ったメールを正解扱いしない
- 営業担当ごとに口調を毎回抽出する
- 季語は毎回調査する
- `knowledge/video_catalog.md`が更新されたら、必ず最新を読む
- Speaker名が崩れている場合は、営業担当名を人間が補足する
