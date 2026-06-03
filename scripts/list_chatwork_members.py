#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

import requests


CHATWORK_API = "https://api.chatwork.com/v2"


def main() -> int:
    token = os.getenv("CHATWORK_API_TOKEN", "").strip()
    room_id = os.getenv("CHATWORK_ROOM_ID", "").strip()
    if not token or not room_id:
        print("CHATWORK_API_TOKEN and CHATWORK_ROOM_ID are required.", file=sys.stderr)
        return 1

    response = requests.get(
        f"{CHATWORK_API}/rooms/{room_id}/members",
        headers={"X-ChatWorkToken": token},
        timeout=30,
    )
    if response.status_code != 200:
        print(f"Chatwork API error {response.status_code}: {response.text}", file=sys.stderr)
        return 1

    members = response.json()
    print("account_id\tname")
    for member in members:
        account_id = member.get("account_id", "")
        name = member.get("name", "")
        print(f"{account_id}\t{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
