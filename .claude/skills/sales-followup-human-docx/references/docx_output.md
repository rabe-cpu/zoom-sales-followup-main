# DOCX Output Rules

## Word出力

- `.docx` で出す。
- 元ファイルは変更しない。
- 新しい出力フォルダまたは新しいファイル名にする。
- 複数商談の場合は、個別docxとまとめdocxのどちらが自然か判断する。
- 顧客送付用docxと社内確認用docxは分ける。
- 顧客送付用docxに評価ログ、営業口調抽出、残リスクを混ぜない。
- `[黄色:...]` や `[/黄色]` は本文に出さず、Wordのハイライトへ変換する。

## 黄色欄

黄色欄は営業が最後に触る箇所だけ。

原則:

1. 冒頭の確認差し替え欄
2. `ZOOM URL：〇〇〇`

必要がある場合だけ追加:

- 次回日時が未確定
- 営業担当署名が未確定
- 動画URLが未確定

## 推奨Word構成

1. 営業後送付メール
2. 営業チェック欄
3. 抽出した営業口調
4. 季語調査結果と参照元
5. 参考動画選定理由
6. 評価ログ
7. Final-Whole-Check
8. 残リスク

顧客送付用は1のみを基本にする。2以降は社内確認用に分ける。

## スクリプト

`scripts/create_followup_docx.py` は、構造化JSONからWordを作る。

最小JSON:

```json
{
  "title": "営業後送付メール",
  "subject": "件名",
  "recipient": "宛名",
  "body": ["本文1", "本文2"],
  "yellow_fields": ["ZOOM URL：〇〇〇"],
  "analysis": {"営業口調": "根拠"},
  "evaluation": [{"agent": "Source-Fact", "score": 96, "finding": "OK"}],
  "remaining_risk": ["Speaker分離に一部不確実性"]
}
```
