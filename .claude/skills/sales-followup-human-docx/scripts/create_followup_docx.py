#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


YELLOW = "FFF2CC"
BLUE = "D9EAF7"
GREEN = "E2F0D9"
INLINE_YELLOW_WITH_LABEL = re.compile(r"\[黄色:([^\]]*)\]([^\[]*?)\[/黄色\]")
INLINE_YELLOW_NO_LABEL_CLOSE = re.compile(r"\[黄色:([^\[]*?)\[/黄色\]")
BLOCK_YELLOW_START = re.compile(r"^\[黄色:[^\]]+\]$")


def shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_font(document: Document) -> None:
    style = document.styles["Normal"]
    style.font.name = "Yu Gothic"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Yu Gothic")
    style.font.size = Pt(10.5)


def add_table(document: Document, headers: list[str], rows: list[list[str]], fill: str) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = str(header)
        shade_cell(cell, fill)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].text = "" if value is None else str(value)


def stringify(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {item}" for key, item in value.items())
    return "" if value is None else str(value)


def add_structured_value(document: Document, value: Any, level: int = 2) -> None:
    if value is None or value == "":
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if item is None or item == "" or item == [] or item == {}:
                continue
            document.add_heading(str(key), level=min(level, 4))
            add_structured_value(document, item, level + 1)
        return
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                add_structured_value(document, item, level)
            else:
                document.add_paragraph(str(item), style="List Bullet")
        return
    add_body(document, str(value).splitlines())


def add_key_values(document: Document, title: str, values: dict[str, Any], fill: str = BLUE) -> None:
    if not values:
        return
    document.add_heading(title, level=1)
    add_table(document, ["項目", "内容"], [[str(k), stringify(v)] for k, v in values.items()], fill)


def add_text_section(document: Document, title: str, value: Any) -> None:
    if not value:
        return
    document.add_heading(title, level=1)
    add_structured_value(document, value, level=2)


def add_highlighted_run(paragraph, text: str) -> None:
    if not text:
        return
    run = paragraph.add_run(text)
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def add_paragraph_with_inline_yellow(document: Document, text: str, block_yellow: bool = False) -> None:
    paragraph = document.add_paragraph()
    if block_yellow:
        add_highlighted_run(paragraph, text)
        return

    cursor = 0
    matched = False
    for match in INLINE_YELLOW_WITH_LABEL.finditer(text):
        matched = True
        paragraph.add_run(text[cursor:match.start()])
        yellow_text = match.group(2) or match.group(1)
        add_highlighted_run(paragraph, yellow_text)
        cursor = match.end()
    remainder = text[cursor:]

    rebuilt = INLINE_YELLOW_NO_LABEL_CLOSE.search(remainder)
    if rebuilt:
        matched = True
        paragraph.add_run(remainder[:rebuilt.start()])
        add_highlighted_run(paragraph, rebuilt.group(1))
        paragraph.add_run(remainder[rebuilt.end():])
    elif matched:
        paragraph.add_run(remainder)
    else:
        paragraph.add_run(text)


def add_body(document: Document, body: list[Any]) -> None:
    block_yellow = False
    for raw in body:
        text = str(raw)
        stripped = text.strip()
        if not stripped:
            document.add_paragraph("")
            continue
        if BLOCK_YELLOW_START.match(stripped):
            block_yellow = True
            continue
        if stripped == "[/黄色]":
            block_yellow = False
            continue
        add_paragraph_with_inline_yellow(document, text, block_yellow)


def build_document(data: dict[str, Any], output: Path) -> None:
    document = Document()
    set_font(document)

    title = data.get("title") or "営業後送付メール"
    heading = document.add_heading(title, 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if data.get("subject"):
        p = document.add_paragraph()
        run = p.add_run(f"件名: {data['subject']}")
        run.bold = True
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    if data.get("recipient"):
        document.add_paragraph(str(data["recipient"]))

    document.add_heading("営業後送付メール", level=1)
    add_body(document, data.get("body", []))

    yellow_fields = data.get("yellow_fields", [])
    if yellow_fields:
        document.add_heading("営業チェック欄", level=1)
        table = document.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        for index, header in enumerate(["区分", "黄色チェック項目", "確認結果"]):
            cell = table.rows[0].cells[index]
            cell.text = header
            shade_cell(cell, YELLOW)
        for field in yellow_fields:
            cells = table.add_row().cells
            cells[0].text = "営業確認"
            cells[1].text = str(field)
            cells[2].text = "未確認"
            shade_cell(cells[1], YELLOW)

    include_internal = data.get("include_internal_sections", True)
    if include_internal:
        add_text_section(
            document,
            "ソーシャルスタイル別全文メール案（社内確認用）",
            data.get("social_style_variants") or data.get("social_style_emails"),
        )
        add_text_section(
            document,
            "商談フィードバック要素",
            data.get("deal_feedback") or data.get("sales_feedback"),
        )

    final_check = data.get("final_check", {}) if include_internal else {}
    if final_check:
        add_key_values(document, "最終確認", final_check, GREEN)

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def sample_data() -> dict[str, Any]:
    return {
        "title": "営業後送付メール サンプル",
        "subject": "本日のご面談のお礼",
        "recipient": "〇〇さま",
        "body": [
            "本日はお時間をいただき、ありがとうございました。",
            "[黄色:営業確認]",
            "お話の中で、現場での運用負荷を抑えながら進めたいという点が大事なのだと受け取りました。",
            "[/黄色]",
            "まずはお時間があるときに、下記をご確認いただけると幸いです。",
            "ZOOM URL：[黄色:〇〇〇[/黄色]",
        ],
        "yellow_fields": ["冒頭の確認差し替え欄", "ZOOM URL：〇〇〇"],
        "social_style_variants": {
            "Driver / Driving": "件名から署名まで含む全文メール案を入れます。",
            "Analytical": "件名から署名まで含む全文メール案を入れます。",
            "Amiable": "件名から署名まで含む全文メール案を入れます。",
            "Expressive": "件名から署名まで含む全文メール案を入れます。",
        },
        "deal_feedback": {
            "商談フェーズ": {
                "currentPhase": "不安の特定",
                "currentGoal": "判断材料を整理し、次回質問につなげる",
                "mustHearBeforeProposal": ["作業時間", "予算感", "意思決定者"],
            },
            "次の一手": {
                "nextBestAction": "送信後、資料確認の有無と不明点を確認する。",
                "hearingQuestions": ["一番気になるのは費用面ですか、作業面ですか？"],
                "recommendedAnswer": "金額だけで判断するとズレやすいので、作業時間と目的に合うかを一緒に確認させてください。",
            },
            "ベンチマーク営業再現": {
                "script": "そこは皆さん一番気にされます。まず状況を確認した上で、合うかどうかを一緒に見ていきましょう。",
                "delivery": "急かさず、短く区切って伝える。",
            },
        },
        "final_check": {"顧客送付用本文": "確認済み", "黄色箇所": "確認済み"},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="JSON input file")
    parser.add_argument("--output", type=Path, required=True, help="Output .docx path")
    parser.add_argument("--self-test", action="store_true", help="Use built-in sample data")
    args = parser.parse_args()

    if args.self_test:
        data = sample_data()
    elif args.input:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        parser.error("Use --input or --self-test")

    build_document(data, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
