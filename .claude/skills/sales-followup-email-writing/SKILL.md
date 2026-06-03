---
name: sales-followup-email-writing
description: Write warm Japanese sales follow-up emails from analyzed transcript facts, salesperson tone evidence, a human template, seasonal greeting research, and video catalog. Use after transcript analysis and before evaluation.
---

# Sales Follow-up Email Writing

## Purpose

分析済みの商談情報をもとに、営業後送付メールの初稿を作る。

## Required Inputs

- Transcript analysis block
- Salesperson tone evidence
- Seasonal greeting result
- Human template or reference email
- knowledge/video_catalog.md / selected video
- Next action information
- knowledge/12_social_style_email_variants.md

## Workflow

1. Keep Template Structure
   - 雛形の流れを維持する。
   - 不自然に長い説明を増やさない。

2. Conversation Opening
   - 冒頭に、お客様と実際に話した内容を2〜4文で入れる。
   - 顧客背景、判断軸、営業が受け止めた自然な一文を入れる。

3. Sales Tone Application
   - 営業担当の実発話にある表現だけ使う。
   - `かと` 系は、発話にある場合のみ0〜1回。
   - 依頼文は途中で止めず、自然に着地させる。
   - 金額、日数、時間、回数、割合は原則アラビア数字で書く。特に金額は `7万円`、`330万円`、`22,000円` のようにし、`七万円`、`三百三十万円`、`二万二千円` と書かない。

4. Video Section
   - knowledge/video_catalog.md から顧客の属性・不安・判断軸に近い動画を1本選ぶ。
   - 下書き前の社内確認用には候補動画を 動画タイトル / YouTube URL / 顧客に合う理由 で列挙する。
   - URL前: なぜこの動画を選んだか
   - URL: カタログ内の実際のYouTube URLをそのまま入れる。
   - URL後: どこを見ると判断材料になるかを1文。
   -参考動画URL：〇〇〇 やURL未確定のまま出さない。

5. Human Edit Marking
   - 黄色箇所は営業が最後に触るべきところだけ。
   - ZOOMが必要なら `ZOOM URL：〇〇〇` を残す。

6. Output Draft
   - 件名
   - 宛名
   - 本文
   - 営業チェック箇所
   - 使用した根拠

7. Social Style Variants For Internal Review
   - 顧客送付用メールとは別に、社内確認用として4スタイル別メール案を作る。
   - 顧客の発話からスタイルを判定しない。
   - 同じ商談事実を Driver / Driving、Analytical、Amiable、Expressive の4つの伝え方に変換する。
   - 各スタイルに、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を入れる。差し替え段落案だけで終わらせない。
   - 各スタイルに、この文面が効く理由、顧客反応シグナル、営業担当が選ぶ目安、次回商談での質問例、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、文脈接続メモを入れる。
   - 商談フィードバック要素（cues / decisionLogic / effectiveQuestions / effectiveReplies / priceQuestionHandling / avoidedTalk / delivery / nextBestAction / benchmarkTalk / contextBridge / riskAlerts）を社内確認用に反映する。
   - スタイル別案と営業フィードバックは社内確認用だけに入れ、顧客送付用本文には混ぜない。

## Non-Negotiables

- 顧客事実を盛らない。
- 顧客のソーシャルスタイルを判定しない。スタイル別案は表現候補としてだけ作る。
- 成果保証をしない。
- `伝わってまいりました` は根拠がある場合だけ使う。根拠が薄い場合は、営業担当の口調に合わせて `伝わってきました` などに寄せる。
- 営業発話にない余白表現を足さない。
- 金額を漢数字で書かない。

## When Not To Use

- Transcript analysis block、営業口調根拠、季語調査結果がまだない場合。
- 評価済みの完成稿をWord化するだけの場合。

## Pass Conditions

- 冒頭に商談で実際に話した内容が2〜4文入っている。
- 営業担当の実発話にない余白表現を足していない。
- 動画URLの前後に、選定理由と見る観点が短く入っている。
- 営業が最後に触る箇所だけが黄色候補として明記されている。
- 金額表記がアラビア数字に統一されている。
- 社内確認用に4スタイル別の全文メール案と営業フィードバックがあり、顧客送付用本文に混ざっていない。
