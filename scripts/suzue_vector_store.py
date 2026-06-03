#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests


DEFAULT_SOURCE_DIR = Path(r"C:\Users\r_abe\OneDrive\Desktop\鈴江商談")
DEFAULT_OUTPUT_DIR = Path("knowledge/rag/generated/suzue_vector_store_upload")
DEFAULT_STATE_PATH = Path("knowledge/rag/suzue_vector_store_state.json")
OPENAI_API_BASE = "https://api.openai.com/v1"


def decode_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp932", "shift_jis"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def safe_name(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:140] or "transcript"


def customer_from_filename(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"^2nd\.|^２回目", "", stem)
    stem = stem.replace("【物販システム アクセス】", "")
    stem = stem.replace("ウェビナー個別面談", "")
    stem = stem.replace("ウェビナー", "")
    stem = stem.replace("_transcribe", "").replace("_all", "")
    stem = re.sub(r"\(\d+\)", "", stem)
    stem = stem.replace("さま", "").replace("様", "")
    return re.sub(r"\s+", " ", stem).strip() or Path(name).stem


def normalize_transcript(text: str) -> str:
    rows: list[str] = []
    parsed_rows = 0
    for row in csv.reader(text.splitlines()):
        if len(row) >= 3:
            parsed_rows += 1
            timestamp = row[0].strip()
            speaker = row[1].strip() or "不明"
            body = ",".join(row[2:]).strip()
            if body:
                rows.append(f"[{timestamp}] {speaker}: {body}")
        elif row:
            line = ",".join(row).strip()
            if line:
                rows.append(line)
    if parsed_rows:
        return "\n".join(rows)
    return text.strip()


def topic_tags(text: str) -> list[str]:
    rules = {
        "価格不安": ["価格", "費用", "高い", "金額", "月額", "総額", "予算"],
        "回収期間": ["回収", "利益", "黒字", "売上", "収益", "年収"],
        "作業時間": ["作業時間", "1日", "時間", "週", "副業", "本業"],
        "審査与信": ["審査", "カード", "信販", "ローン", "与信", "リボ", "債務"],
        "家族相談": ["家族", "奥さん", "旦那", "妻", "夫", "相談"],
        "プラン比較": ["ミニマム", "ベーシック", "スタンダード", "プラン"],
        "不安解消": ["不安", "心配", "懸念", "迷", "怖"],
        "次アクション": ["資料", "フォーム", "メール", "電話", "LINE", "連絡", "次回"],
        "クロージング": ["やる", "始め", "契約", "申し込み", "検討結果"],
    }
    tags = [tag for tag, keywords in rules.items() if any(keyword in text for keyword in keywords)]
    return tags[:8]


def prepare_files(source_dir: Path, output_dir: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not source_dir.exists():
        raise FileNotFoundError(f"source directory not found: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    files = sorted(path for path in source_dir.glob("*.txt") if path.is_file())
    if limit:
        files = files[:limit]

    for index, source_path in enumerate(files, start=1):
        raw = source_path.read_bytes()
        decoded = decode_text(raw)
        normalized = normalize_transcript(decoded)
        customer = customer_from_filename(source_path.name)
        tags = topic_tags(normalized)
        out_name = f"{index:03d}_{safe_name(customer)}.md"
        out_path = output_dir / out_name
        header = [
            "---",
            "source: suzue_benchmark_sales_transcript",
            f"source_file: {source_path.name}",
            f"customer: {customer}",
            "salesperson: Masato Suzue",
            f"topic_tags: {', '.join(tags) if tags else '未分類'}",
            "---",
            "",
            f"# 鈴江商談: {customer}",
            "",
            "このファイルはOpenAI Vector Store投入用にUTF-8正規化した文字起こしです。",
            "顧客送付用メール本文には原文を直接出さず、社内確認用のトップ営業指導・勝ち筋・返答案の根拠としてだけ使います。",
            "",
        ]
        out_path.write_text("\n".join(header) + normalized + "\n", encoding="utf-8")
        manifest.append(
            {
                "source_file": str(source_path),
                "upload_file": str(out_path),
                "customer": customer,
                "topic_tags": tags,
                "bytes": out_path.stat().st_size,
            }
        )

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return key


def request_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {api_key()}"
    response = requests.request(method, f"{OPENAI_API_BASE}{path}", headers=headers, timeout=120, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text}")
    if not response.text:
        return {}
    return response.json()


def create_vector_store(name: str) -> str:
    result = request_json("POST", "/vector_stores", json={"name": name})
    vector_store_id = result.get("id")
    if not vector_store_id:
        raise RuntimeError(f"vector store id missing: {result}")
    return vector_store_id


def upload_file(path: Path) -> str:
    with path.open("rb") as handle:
        result = request_json(
            "POST",
            "/files",
            data={"purpose": "assistants"},
            files={"file": (path.name, handle, "text/markdown")},
        )
    file_id = result.get("id")
    if not file_id:
        raise RuntimeError(f"file id missing: {result}")
    return file_id


def attach_file(vector_store_id: str, file_id: str, attributes: dict[str, Any]) -> str:
    payload = {
        "file_id": file_id,
        "attributes": attributes,
        "chunking_strategy": {
            "type": "static",
            "static": {
                "max_chunk_size_tokens": 1000,
                "chunk_overlap_tokens": 200,
            },
        },
    }
    result = request_json("POST", f"/vector_stores/{vector_store_id}/files", json=payload)
    return result.get("id") or file_id


def poll_vector_store(vector_store_id: str, timeout_seconds: int = 900) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last: dict[str, Any] = {}
    while time.time() < deadline:
        last = request_json("GET", f"/vector_stores/{vector_store_id}")
        counts = last.get("file_counts", {})
        in_progress = counts.get("in_progress", 0)
        failed = counts.get("failed", 0)
        status = last.get("status")
        if status == "completed" and in_progress == 0:
            return last
        if failed:
            return last
        time.sleep(5)
    raise TimeoutError(f"vector store processing timed out: {last}")


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        raise FileNotFoundError(f"state file not found: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def upload_corpus(output_dir: Path, state_path: Path, name: str, limit: int | None = None) -> dict[str, Any]:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found. Run prepare first: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if limit:
        manifest = manifest[:limit]

    vector_store_id = create_vector_store(name)
    uploaded: list[dict[str, Any]] = []
    for index, item in enumerate(manifest, start=1):
        upload_path = Path(item["upload_file"])
        print(f"[{index}/{len(manifest)}] upload {upload_path.name}", file=sys.stderr)
        file_id = upload_file(upload_path)
        attributes = {
            "source": "suzue_benchmark_sales_transcript",
            "customer": item.get("customer", "")[:256],
            "salesperson": "Masato Suzue",
            "topic_tags": ",".join(item.get("topic_tags", []))[:256],
            "source_file": Path(item.get("source_file", "")).name[:256],
        }
        vector_store_file_id = attach_file(vector_store_id, file_id, attributes)
        uploaded.append({**item, "file_id": file_id, "vector_store_file_id": vector_store_file_id})

    status = poll_vector_store(vector_store_id)
    state = {
        "vector_store_id": vector_store_id,
        "name": name,
        "created_at": int(time.time()),
        "source_dir": str(DEFAULT_SOURCE_DIR),
        "upload_dir": str(output_dir),
        "files": uploaded,
        "status": status,
    }
    save_state(state_path, state)
    return state


def search(vector_store_id: str, query: str, max_results: int) -> dict[str, Any]:
    payload = {"query": query, "max_num_results": max_results}
    return request_json("POST", f"/vector_stores/{vector_store_id}/search", json=payload)


def print_search_results(result: dict[str, Any]) -> None:
    data = result.get("data", result.get("results", []))
    for index, item in enumerate(data, start=1):
        score = item.get("score", "")
        filename = item.get("filename") or item.get("file_id") or ""
        print(f"\n## result {index} score={score} file={filename}")
        content = item.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "")
                    if text:
                        print(text[:1800])
                elif block:
                    print(str(block)[:1800])
        elif content:
            print(str(content)[:1800])
        else:
            print(json.dumps(item, ensure_ascii=False, indent=2)[:1800])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and query the Suzue benchmark OpenAI Vector Store.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="Normalize source txt files into UTF-8 markdown files for upload.")
    prepare.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    prepare.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    prepare.add_argument("--limit", type=int)

    upload = sub.add_parser("upload", help="Create a vector store and upload prepared files.")
    upload.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    upload.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    upload.add_argument("--name", default="Suzue benchmark sales transcripts")
    upload.add_argument("--limit", type=int)

    search_parser = sub.add_parser("search", help="Search the Suzue vector store.")
    search_parser.add_argument("query")
    search_parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    search_parser.add_argument("--vector-store-id")
    search_parser.add_argument("--max-results", type=int, default=8)

    status = sub.add_parser("status", help="Show vector store status.")
    status.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    status.add_argument("--vector-store-id")

    args = parser.parse_args()

    if args.command == "prepare":
        manifest = prepare_files(args.source_dir, args.output_dir, args.limit)
        print(json.dumps({"prepared": len(manifest), "output_dir": str(args.output_dir)}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "upload":
        state = upload_corpus(args.output_dir, args.state_path, args.name, args.limit)
        print(json.dumps({"vector_store_id": state["vector_store_id"], "files": len(state["files"])}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "search":
        vector_store_id = args.vector_store_id or load_state(args.state_path)["vector_store_id"]
        result = search(vector_store_id, args.query, args.max_results)
        print_search_results(result)
        return 0

    if args.command == "status":
        vector_store_id = args.vector_store_id or load_state(args.state_path)["vector_store_id"]
        result = request_json("GET", f"/vector_stores/{vector_store_id}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
