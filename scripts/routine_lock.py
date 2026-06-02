#!/usr/bin/env python3
"""
routine_lock.py - Claude Routine duplicate-run guard
====================================================
Use a small JSON file in the configured Google Drive output folder as a shared
lock. This prevents a 30-minute external scheduler from starting a second
Routine while the previous run is still working.

Commands:
  python scripts/routine_lock.py acquire
  python scripts/routine_lock.py release
  python scripts/routine_lock.py status

Environment:
  ROUTINE_LOCK_TTL_MINUTES  Default: 90
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import uuid
from datetime import datetime, timedelta, timezone

from googleapiclient.http import MediaIoBaseUpload
import io

from gdrive_client import GoogleDriveClient


LOCK_NAME = "routine_running.lock.json"
DEFAULT_TTL_MINUTES = 90


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _json_response(**values) -> None:
    print(json.dumps(values, ensure_ascii=False, indent=2))


def _safe_drive_name(name: str) -> str:
    return name.replace("\\", "\\\\").replace("'", "\\'")


def _list_lock_files(gdrive: GoogleDriveClient) -> list[dict]:
    safe = _safe_drive_name(LOCK_NAME)
    q = (
        f"name = '{safe}' and '{gdrive.root_folder_id}' in parents "
        "and trashed = false"
    )
    resp = gdrive.service.files().list(
        q=q,
        fields="files(id, name, createdTime, modifiedTime)",
        orderBy="createdTime",
    ).execute()
    return resp.get("files", [])


def _read_file_json(gdrive: GoogleDriveClient, file_id: str) -> dict:
    try:
        content = gdrive.service.files().get_media(fileId=file_id).execute()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        return json.loads(content)
    except Exception:
        return {}


def _delete_file(gdrive: GoogleDriveClient, file_id: str) -> None:
    gdrive.service.files().delete(fileId=file_id).execute()


def _is_fresh(lock: dict, file_meta: dict, ttl: timedelta) -> bool:
    timestamp = (
        _parse_time(lock.get("acquired_at"))
        or _parse_time(file_meta.get("createdTime"))
        or _parse_time(file_meta.get("modifiedTime"))
    )
    if not timestamp:
        return True
    return _now() - timestamp < ttl


def acquire() -> int:
    ttl_minutes = int(os.getenv("ROUTINE_LOCK_TTL_MINUTES", str(DEFAULT_TTL_MINUTES)))
    ttl = timedelta(minutes=ttl_minutes)
    owner = os.getenv("GITHUB_RUN_ID") or os.getenv("RUN_ID") or str(uuid.uuid4())
    payload = {
        "owner": owner,
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "acquired_at": _now().isoformat(),
        "ttl_minutes": ttl_minutes,
    }

    gdrive = GoogleDriveClient()

    for file_meta in _list_lock_files(gdrive):
        lock = _read_file_json(gdrive, file_meta["id"])
        if _is_fresh(lock, file_meta, ttl):
            _json_response(
                status="locked",
                message="Another Routine run is still active.",
                lock_file_id=file_meta["id"],
                lock=lock,
            )
            return 75
        _delete_file(gdrive, file_meta["id"])

    media = MediaIoBaseUpload(
        io.BytesIO(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")),
        mimetype="application/json",
        resumable=False,
    )
    created = gdrive.service.files().create(
        body={"name": LOCK_NAME, "parents": [gdrive.root_folder_id]},
        media_body=media,
        fields="id, createdTime",
    ).execute()

    # Mitigate near-simultaneous starts: after creating our lock, the oldest
    # lock wins and newer contenders delete their own lock.
    locks = _list_lock_files(gdrive)
    if locks and locks[0]["id"] != created["id"]:
        _delete_file(gdrive, created["id"])
        winner = locks[0]
        _json_response(
            status="locked",
            message="Another Routine run acquired the lock first.",
            lock_file_id=winner["id"],
            lock=_read_file_json(gdrive, winner["id"]),
        )
        return 75

    _json_response(status="acquired", lock_file_id=created["id"], lock=payload)
    return 0


def release() -> int:
    gdrive = GoogleDriveClient()
    deleted = []
    for file_meta in _list_lock_files(gdrive):
        _delete_file(gdrive, file_meta["id"])
        deleted.append(file_meta["id"])
    _json_response(status="released", deleted=deleted)
    return 0


def status() -> int:
    gdrive = GoogleDriveClient()
    locks = [
        {"file": file_meta, "lock": _read_file_json(gdrive, file_meta["id"])}
        for file_meta in _list_lock_files(gdrive)
    ]
    _json_response(status="locked" if locks else "unlocked", locks=locks)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["acquire", "release", "status"])
    args = parser.parse_args()
    if args.command == "acquire":
        return acquire()
    if args.command == "release":
        return release()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
