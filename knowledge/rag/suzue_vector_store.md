# 鈴江商談 OpenAI Vector Store RAG

## 目的

`C:\Users\r_abe\OneDrive\Desktop\鈴江商談` の商談文字起こしをOpenAI Vector Storeに投入し、営業後メール生成時に「トップ営業の勝ち筋」として検索参照する。

このRAGは顧客事実を増やすためではなく、鈴江商談に出ている営業の型、質問順、反論処理、価格不安の戻し方、クロージング、次アクションの置き方を再利用するために使う。

## 初回準備

```powershell
python -m pip install -r scripts/requirements.txt
python scripts\suzue_vector_store.py prepare
$env:OPENAI_API_KEY = "<OpenAI API key>"
python scripts\suzue_vector_store.py upload
```

`prepare` はローカルでUTF-8 markdownを作るだけ。`upload` を実行した時点で、鈴江商談の文字起こしがOpenAI Vector Storeへ送信される。課金と社外API送信が発生するため、実行前に運用者が確認する。

生成物:

- `knowledge/rag/generated/suzue_vector_store_upload/`: 投入用markdownとmanifest
- `knowledge/rag/suzue_vector_store_state.json`: 作成されたVector Store ID

上記2つはgit管理しない。

## メール生成時の検索

営業後メールを書く前に、今回商談の論点から検索クエリを作る。

```powershell
python scripts\suzue_vector_store.py search "価格不安 審査 作業時間 家族相談 次アクション" --max-results 8
```

検索クエリには、今回の文字起こしから出た判断軸、不安、検討ステージ、顧客属性を入れる。例:

- `価格不安 回収期間 初心者 作業時間`
- `家族相談 予算感 審査 フォーム誘導`
- `比較検討 副業 本業忙しい 次回連絡`
- `成果重視 事例動画 クロージング`

## 反映先

検索結果は社内確認用の以下に反映する。

- 再現する勝ち筋
- トップ営業ならどう見るか
- 次回聞くべき質問
- そのまま使える返答例
- 価格・費用質問への返し方
- 不安が出た時の戻し方
- クロージング
- `benchmarkCoach`
- `phasePlaybooks`
- `customerAttributePlaybooks`

## 禁止

- 顧客送付用メールに、鈴江商談の顧客名、検索結果、原文引用、RAG実行ログを出さない。
- 今回顧客が話していない背景、金額、感情、成果期待を足さない。
- 音声、映像、声色、話速、表情、模写練習メニューには使わない。
- 社内確認用docxに、Vector Store検索ログ、評価ログ、残リスク、英語キー、`name=` 形式を出さない。

## フォールバック

`OPENAI_API_KEY` がない、`suzue_vector_store_state.json` がない、検索が失敗した場合は、静的ナレッジ `knowledge/benchmark_playbooks/suzue_benchmark.md` を使う。

この場合もdocxには失敗ログを出さず、通常どおりトップ営業の指導文として自然に反映する。
