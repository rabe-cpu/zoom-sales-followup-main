---
name: sales-tone-knowledge-register
description: Register or update Japanese salesperson tone knowledge files under knowledge/sales_persons/. Use after sales-transcript-intake-analysis to auto-create per-salesperson files for new salespersons, or to propose diffs for existing ones. Triggers on 営業担当登録, 新担当, 口調登録, salesperson knowledge update.
---

# Sales Tone Knowledge Register

## Purpose

商談文字起こしから抽出した営業担当の口調を、`knowledge/sales_persons/{担当}.md` および `knowledge/sales_persons/{担当}.docx` に1ファイル1担当で蓄積する。

未登録の担当は自動でファイル生成、既存の担当は `.draft.md` / `.draft.docx` で差分提示し、人間レビュー後に正本へ反映する。

## Dual Output Rule（絶対）

- `.md` と `.docx` は **必ず両方** 出力する。片方だけ出力する状態を作らない。
- `.md` は CLAUDE.md からの `@import` 用（AIが参照する正本）。
- `.docx` は人間レビュー・営業マネージャー承認用（Word上でレビューしやすい形）。
- `.md` を書き換えたら、対応する `.docx` も同時に再生成する。
- 既存の `.md` だけが存在して `.docx` が欠けている場合は、`--mode regen` で `.docx` を後付け生成する。

## When To Use

- `sales-transcript-intake-analysis` を実行した直後
- 文字起こしの Speaker に新しい営業担当名が現れたとき
- 既存担当の口調情報を更新したいとき

## When Not To Use

- 文字起こしに営業発話が極端に少なく、抽出根拠が薄いとき（ファイルを汚染しない）
- 営業担当が複数人混在しており、Speaker分離の信頼度が低いとき

## Inputs

- 文字起こしから抽出した営業担当名
- `Salesperson tone evidence` ブロック（`sales-transcript-intake-analysis` の出力）
- 既存ファイル: `knowledge/sales_persons/{担当}.md`
- 既存index: `knowledge/sales_persons/_index.md`

## Workflow

1. Detect Salesperson
   - 文字起こしの Speaker欄から営業担当名を抽出する。
   - 表記ゆれは姓のみで正規化する（例: `NEXT_笠井理生` → `笠井`）。

2. Check Existing
   - `knowledge/sales_persons/{担当}.md` が存在するか確認する。

3a. New Registration
   - 存在しない場合、`scripts/register_sales_person.py --mode new` で `.md` と `.docx` を同時生成する。
   - 同時に `_index.md` の `## 登録済み` セクションへ `@{担当}.md` を追記する。
   - 抽出根拠の文字起こしパスを frontmatter の `source_transcripts` に記録する。

3b. Diff Proposal
   - 存在する場合、`scripts/register_sales_person.py --mode draft` で `{担当}.draft.md` と `{担当}.draft.docx` を同時作成する。
   - 既存ファイルは変更しない。
   - 差分は `.docx` をWordで開いてレビューし、合意後に正本へマージする。

3c. Docx Backfill
   - 既存の `.md` に対応する `.docx` が欠けている場合、`scripts/register_sales_person.py --mode regen --md-path knowledge/sales_persons/{担当}.md` で後付け生成する。
   - `.md` の内容は変更しない。

4. Report
   - 新規作成 or draft提示のどちらが起きたかを最終回答に明記する。
   - Skill Used Check の `Knowledge read` に追加した担当ファイル名も残す。

## Non-Negotiables

- `.md` と `.docx` を必ず両方出力する。片方だけ作って終わらせない。
- 既存ファイル（`.md` も `.docx` も）を自動で上書きしない。新規は `new`、更新案は `draft` で提示する。
- 抽出根拠（文字起こしパス、観測した発話例）を必ずfrontmatterまたは本文に残す。
- 口調抽出は営業発話だけを根拠にする。顧客発話を混入させない。
- 余白表現（かと/かなと/できればと/見ていただけると）の出現有無と頻度を必ず記録する。

## Output Format

新規作成ファイルは以下のテンプレートに従う。

```markdown
---
name: {担当姓}
display_name: {表示名}
company: {会社・部署}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
source_transcripts:
  - {path1}
---

# {表示名}さん

## 商談内で見えた特徴

- {頻出語1}
- {頻出語2}

## 一人称・距離感

- 一人称: {僕／私／弊社}
- 顧客への呼び方: {〇〇さん／〇〇さま}

## メール反映の定型

- {依頼表現}
- {確認表現}
- 締め: {締め定型}

## 余白表現の出現

- かなと: あり/なし（頻度）
- かと: あり/なし（頻度）
- できればと: あり/なし（着地ルール）
- 見ていただけると: あり/なし

## 禁止候補

- {禁止候補1}
```

## Pass Conditions

- 新担当の場合、`knowledge/sales_persons/{担当}.md` と `knowledge/sales_persons/{担当}.docx` の **両方** が生成され、`_index.md` への追記が完了している。
- 既存担当の場合、`{担当}.draft.md` と `{担当}.draft.docx` の **両方** が生成され、既存ファイルは未変更である。
- 既存.mdに対するregenの場合、`{担当}.docx` が `.md` の内容と一致している。
- frontmatter に `source_transcripts` が記録されている。
- 余白表現の出現有無が本文に記載されている。

## Script

`scripts/register_sales_person.py` を使う。

最小JSON入力:

```json
{
  "name": "笠井",
  "display_name": "笠井 理生",
  "company": "NEXT セールス部",
  "source_transcripts": ["path/to/transcript.csv"],
  "features": ["一旦", "確認", "ご質問ご不明点"],
  "first_person": "僕",
  "customer_address": "〇〇さま",
  "email_phrases": ["一旦こちらのメールにご返信いただいてもよろしいでしょうか"],
  "closing": "引き続きどうぞよろしくお願いいたします",
  "slack_expressions": {
    "かなと": "あり（複数回）",
    "かと": "限定的",
    "できればと": "あり（着地必須）",
    "見ていただけると": "なし"
  },
  "prohibitions": ["伝わってまいりました"]
}
```

実行:

```text
# 新規登録（.md + .docx + _index.md追記を同時実行）
python scripts/register_sales_person.py --input person.json --knowledge-dir knowledge/sales_persons --mode new

# 既存担当のdiff提示（.draft.md + .draft.docx を生成、正本は不変）
python scripts/register_sales_person.py --input person.json --knowledge-dir knowledge/sales_persons --mode draft

# 自動判定（未登録ならnew、既存ならdraft）
python scripts/register_sales_person.py --input person.json --knowledge-dir knowledge/sales_persons --mode auto

# 既存.mdに対応する.docxを後付け生成（.mdは変更しない）
python scripts/register_sales_person.py --md-path knowledge/sales_persons/笠井.md --knowledge-dir knowledge/sales_persons --mode regen
```
