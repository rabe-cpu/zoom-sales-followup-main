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
- knowledge/benchmark_playbooks/suzue_benchmark.md

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

7. Deal Feedback Extraction For Internal Review
   - 顧客送付用メールを書く前に、`sales-analysis-app-openai-next` のフィードバック思想に沿って、内部で商談フィードバックを整理する。
   - `knowledge/benchmark_playbooks/suzue_benchmark.md` を必ず参照し、文字起こしベースの営業型として `benchmarkCoach`、`winningPatterns`、`phasePlaybooks`、`customerAttributePlaybooks` に反映する。
   - 鈴江ベンチマークは顧客事実の根拠ではない。顧客が話していない背景、金額、感情、成果期待を足さない。
   - 音声・映像コーチング、声色・話速評価、録音練習、模写練習メニューは出力しない。
   - `overallSummary`: 総合概要、現在の検討状態、トップ営業・勝ち商談との差分
   - `customerInsights`: 潜在ニーズ、言い切っていない不安、比較対象、判断基準、購買温度感
   - `cognitiveBias`: name / description / counterMeasure
   - `expectationGap`: topic / gap / solution
   - `strengths`: 良かった点。item / detail
   - `improvementPoints`: 改善ポイント。item / detail
   - `coachingCards`: 4枚。theme / scene / insight / issue / strategy / script / outcome
   - `winningPatterns`: 再現する勝ち筋。勝ち筋名 / 使う場面 / 顧客シグナル / トップ営業の動き / コピートーク / なぜ効くか / NG例 / 次回実践方法
   - `talkStyleModel`: 再現すべき営業像、語尾、質問順、つなぎ台詞、クロージングのリズム
   - `textDeliveryModel`: メール文量、説明順、質問の置き方、資料URLやフォームへの接続
   - `objectionPatterns`: 反論・不安へのベンチマーク返答、深掘り質問、NG返答
   - `stageStrategy`: currentGoal / keepUntilLater / mustHearBeforeProposal / planDecisionPath
   - `phasePlaybooks`: 今回該当する商談フェーズ、目的、顧客シグナル、次回質問、返答、次フェーズへのつなぎ
   - `customerSignals`: 温度感、懸念、購入動機、決裁観点、価格反応、家族相談、比較検討
   - `temperature`: 高 / 中 / 低 と理由。数値スコアは出さない。
   - `nextBestAction`: 送信後または次回接点で営業担当が取る具体行動
   - `hearingQuestions`: 次に聞くべき質問を優先順で最大3つ
   - `recommendedAnswer`: 顧客から返信・質問が来た時にそのまま使える2〜6文の返答
   - `benchmarkCoach`: script / whyItWorks / benchmarkPattern / delivery
   - `contextBridge`: sourceMoment / insight / recommendedTalk / evidence
   - `customerAttributePlaybooks`: 慎重・分析型、価格重視、成果重視、初心者、経験者、家族相談あり、即決寄り、比較検討中などから今回使えそうなものを1〜2個
   - この抽出結果は顧客送付用本文に混ぜず、社内確認用の「商談フィードバック要素」にだけ入れる。
   - 評価ログ、残リスク、営業口調抽出、季語調査結果、参考動画選定理由としては出さない。
   - docx表示では `overallSummary`、`hiddenNeeds`、`name=`、`item=`、`theme=`、`benchmarkCoach.script` などの内部キー名を出さない。必ず日本語見出しと自然文に変換する。
   - 商談フィードバックは、トップ営業マンが営業担当に目の前で指導している形にする。「この場面ではこう見ます」「次回はこう聞きます」「この返答なら刺さります」のように、実践に移せる文章を中心にする。
   - 箇条書きだけで終わらせない。箇条書きは次回質問・確認項目・NG例など、営業がチェックする用途に限定する。

8. Social Style Variants For Internal Review
   - 顧客送付用メールとは別に、社内確認用として4スタイル別メール案を作る。
   - 顧客の発話からスタイルを判定しない。
   - 同じ商談事実を Driver / Driving、Analytical、Amiable、Expressive の4つの伝え方に変換する。
   - 各スタイルに、件名から署名・固定資料URL・固定フォームURLまで含む全文メール案を入れる。差し替え段落案だけで終わらせない。
   - 各スタイルに、この文面が効く理由、顧客反応シグナル、営業担当が選ぶ目安、次回商談での質問例、そのまま使える返答例、価格・費用質問への返し方、避ける言い方、伝え方メモ、次の一手、ベンチマーク営業トーク、ベンチマーク営業台本、文脈接続メモを入れる。
   - 4スタイルの違いは語尾や文量だけで出さない。Driverは結論・主導権・次アクション、Analyticalは根拠・条件・例外、Amiableは安心・合意形成・相談導線、Expressiveは未来像・承認・ストーリーで分ける。
   - 各スタイルに、価格質問対応、不安が出た時の戻し方、クロージング、ストレス反応へのリカバリーを入れる。
   - 商談フィードバック要素（overallSummary / customerInsights / cognitiveBias / expectationGap / strengths / improvementPoints / coachingCards / winningPatterns / stageStrategy / phasePlaybooks / customerSignals / temperature / cues / decisionLogic / effectiveQuestions / effectiveReplies / priceQuestionHandling / avoidedTalk / delivery / nextBestAction / benchmarkTalk / benchmarkCoach / contextBridge / customerAttributePlaybooks / riskAlerts）を社内確認用に反映する。
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
- 社内確認用に4スタイル別の全文メール案、総合概要、顧客インサイト、認知バイアス、期待値のズレ、良かった点、改善ポイント、AIコーチングカード、再現する勝ち筋、商談フェーズ別フィードバック、ベンチマーク営業台本、属性別対応があり、顧客送付用本文に混ざっていない。
- 社内確認用docxに英語キーや `name=` 形式が出ておらず、トップ営業の指導文として読める。
- 4スタイル別案が、価格対応、不安対応、クロージング、ストレス時の戻し方まで分岐している。
