# Other AI Prompt

ChatGPT、Claude、Geminiなど、Claude Code以外で使う場合の短縮プロンプト。

```text
商談文字起こしから営業後送付メールを作ってください。

重要:
- 顧客発話と営業発話を分けてください。
- 営業担当の口調は、営業担当の実発話に出ている言い方だけ反映してください。
- `かと`、`かなと`、`できればと` などの余白表現は、営業担当が商談中に言っていなければ使わないでください。
- 季語は送付日に合わせて毎回調査してください。
- 冒頭には、商談で実際に話した内容を2〜4文で入れてください。
- 参考動画は、URLの前後に短く説明を入れてください。
- ZOOM URLは `ZOOM URL：〇〇〇` として営業が差し替えられるようにしてください。
- `伝わってまいりました` は使わないでください。

最後に、以下の評価エージェントに分けて評価してください。
- Source-Fact Agent
- Sales-Tone Agent
- Customer-Human Agent
- Risk-Compliance Agent
- Ops-Formatting Agent
- Final-Whole-Check Agent

90点未満、または重大指摘がある場合は、AIで本文を改善し、同じ評価エージェントで再評価してください。
```
