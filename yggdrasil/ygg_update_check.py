#!/usr/bin/env python3
"""Cached 'a newer version is available' check — like context-mode's update nudge.

Split so nothing ever blocks on the network at call time:
- The long-lived engine periodically calls ``refresh_cache()`` (one PyPI request)
  and writes ``~/.yggdrasil/update-check.json``.
- The CLI and the MCP facade call ``notice()`` which only READS that cache and
  compares to the installed version — instant, offline-safe.

Pure stdlib; works both as a package module and as a flat-deployed script.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from pathlib import Path

PKG = "yggdrasil-memory"
TTL = float(os.environ.get("YGG_UPDATE_CHECK_TTL", "43200"))  # 12h
_CACHE = Path(os.environ.get("YGG_HOME", str(Path.home() / ".yggdrasil"))) / "update-check.json"


def _vtuple(v: str) -> tuple:
    return tuple(int("".join(c for c in p if c.isdigit()) or 0) for p in str(v).split("."))


def installed_version() -> str | None:
    """The version of the running code — works in the package and flat-deploy."""
    try:
        from yggdrasil import __version__  # package context
        return __version__
    except ImportError:
        pass
    try:  # flat deploy: read the __init__.py sitting next to this file
        txt = (Path(__file__).resolve().parent / "__init__.py").read_text()
        m = re.search(r'__version__\s*=\s*"([^"]+)"', txt)
        return m.group(1) if m else None
    except OSError:
        return None


def _fetch_latest() -> str | None:
    # Cache-bust PyPI's CDN (it can briefly serve the previous version right after
    # a publish) with a unique query + no-cache headers.
    url = f"https://pypi.org/pypi/{PKG}/json?_={int(time.time())}"
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r)["info"]["version"]
    except Exception:  # noqa: BLE001 — best effort, never raise into the engine loop
        return None


def refresh_cache() -> None:
    """Fetch the latest published version and cache it. Called by the engine."""
    latest = _fetch_latest()
    if not latest:
        return
    try:
        _CACHE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE.write_text(json.dumps({"checked_at": time.time(), "latest": latest}))
    except OSError:
        pass


def notice(installed: str | None = None) -> str:
    """A one-line upgrade nudge if the cached latest > installed, else ''. No network."""
    installed = installed or installed_version()
    if not installed:
        return ""
    try:
        latest = json.loads(_CACHE.read_text()).get("latest")
    except (OSError, ValueError):
        return ""
    if latest and _vtuple(latest) > _vtuple(installed):
        return f"⬆ Yggdrasil {latest} is available (you have {installed}). Upgrade:  ygg update"
    return ""
