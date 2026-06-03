#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys


REQUIRED_MODULES = [
    "requests",
    "google.auth",
    "googleapiclient",
    "google_auth_oauthlib",
    "httplib2",
]


def module_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


def main() -> int:
    missing = [name for name in REQUIRED_MODULES if not module_exists(name)]
    print("missing=" + ",".join(missing))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
