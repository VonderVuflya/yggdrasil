#!/usr/bin/env python3
"""Claude Code SessionStart hook: inject relevant Yggdrasil memory for the project.

Reads the hook payload on stdin, derives the project from the working directory
(git toplevel basename), queries the running Yggdrasil engine, and emits the top
matching memories as `additionalContext` so the agent starts with prior lessons
already in context — the retrieval half of the self-learning loop.

Fail-safe by design: any error (engine down, no token, no memory) prints nothing
and exits 0, so it can never break or slow a session noticeably.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path


URL = os.environ.get("YGG_MUNINN_URL", "http://127.0.0.1:42069").rstrip("/")
NAMESPACE = os.environ.get("YGG_NAMESPACE", "yggdrasil-dogfood")
USER_ID = os.environ.get("YGG_USER_ID", "dogfood-user")
LIMIT = int(os.environ.get("YGG_BOOTSTRAP_LIMIT", "5"))


def token() -> str:
    tok = os.environ.get("YGG_MUNINN_TOKEN")
    if tok:
        return tok
    try:
        return (Path.home() / ".yggdrasil" / "token").read_text().strip()
    except OSError:
        return "yggdrasil-demo-token"


def project_for(cwd: str) -> str:
    try:
        top = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=3)
        if top.returncode == 0 and top.stdout.strip():
            return Path(top.stdout.strip()).name
    except (OSError, subprocess.SubprocessError):
        pass
    return Path(cwd).name


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        payload = {}
    cwd = payload.get("cwd") or os.getcwd()
    project = project_for(cwd)

    body = json.dumps({
        "query": f"{project} decision lesson gotcha workflow command",
        "user_id": USER_ID,
        "limit": LIMIT,
        "rerank": False,
        "filters": {"project": project, "scope": "project"},
        "namespaces": [NAMESPACE],
    }).encode("utf-8")
    req = urllib.request.Request(URL + "/search", data=body, method="POST",
                                headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read()).get("data", [])
    except Exception:
        return 0  # fail-safe: never break the session

    if not data:
        return 0
    lines = [f"Yggdrasil memory for project `{project}` (prior durable lessons — verify against the repo):"]
    for item in data:
        meta = item.get("metadata") or {}
        preview = " ".join((item.get("memory") or "").split())[:200]
        lines.append(f"- [{meta.get('type', 'memory')}] {preview}")
    context = "\n".join(lines)

    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
