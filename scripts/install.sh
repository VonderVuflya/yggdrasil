#!/usr/bin/env bash
# Yggdrasil installer (macOS): run the memory engine as an always-on background
# service (launchd) and register the MCP facade with Claude Code and Codex, so
# any agent on this machine shares one durable memory — "install once, it just runs".
#
#   scripts/install.sh install [--embed-model all-minilm|paraphrase-multilingual] [--seed-db PATH]
#   scripts/install.sh status | start | stop | restart | logs | token | uninstall
#
# Layout: ~/.yggdrasil/{scripts,data,logs,token}. Token is generated, not hardcoded.
set -uo pipefail

YGG_HOME="${YGG_HOME:-$HOME/.yggdrasil}"
PORT="${YGG_PORT:-42069}"
LABEL="com.yggdrasil.memory"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SRC_SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3)"
URL="http://127.0.0.1:${PORT}"

cmd="${1:-install}"; shift || true
EMBED_MODEL=""; SEED_DB=""
while [ $# -gt 0 ]; do
  case "$1" in
    --embed-model) EMBED_MODEL="${2:-}"; shift 2;;
    --seed-db) SEED_DB="${2:-}"; shift 2;;
    *) shift;;
  esac
done

domain="gui/$(id -u)"

_stop() {
  launchctl bootout "$domain/$LABEL" 2>/dev/null || launchctl unload "$PLIST" 2>/dev/null || true
}

_start() {
  launchctl bootstrap "$domain" "$PLIST" 2>/dev/null || launchctl load -w "$PLIST" 2>/dev/null || true
}

case "$cmd" in
  install)
    echo "==> installing into $YGG_HOME"
    mkdir -p "$YGG_HOME/scripts" "$YGG_HOME/data" "$YGG_HOME/logs"
    cp "$SRC_SCRIPTS"/*.py "$YGG_HOME/scripts/"

    if [ ! -f "$YGG_HOME/token" ]; then
      "$PYTHON" -c "import secrets;print(secrets.token_hex(24))" > "$YGG_HOME/token"
      chmod 600 "$YGG_HOME/token"
      echo "    generated auth token -> $YGG_HOME/token"
    fi
    TOKEN="$(cat "$YGG_HOME/token")"

    if [ -n "$SEED_DB" ] && [ -f "$SEED_DB" ]; then
      cp "$SEED_DB" "$YGG_HOME/data/memory.sqlite"
      echo "    seeded DB from $SEED_DB"
    fi

    # Build engine arguments (conditionally include the embedding model).
    EMBED_PLIST=""
    [ -n "$EMBED_MODEL" ] && EMBED_PLIST="    <string>--embed-model</string>
    <string>${EMBED_MODEL}</string>"

    _stop
    cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON}</string>
    <string>${YGG_HOME}/scripts/ygg_memory_server.py</string>
    <string>--db</string><string>${YGG_HOME}/data/memory.sqlite</string>
    <string>--port</string><string>${PORT}</string>
    <string>--token</string><string>${TOKEN}</string>
${EMBED_PLIST}
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>${YGG_HOME}/logs/engine.log</string>
  <key>StandardErrorPath</key><string>${YGG_HOME}/logs/engine.log</string>
</dict>
</plist>
PLISTEOF
    _start
    sleep 2

    # Register the MCP facade with Claude Code and Codex (best-effort).
    if command -v claude >/dev/null 2>&1; then
      claude mcp remove yggdrasil -s user >/dev/null 2>&1 || true
      claude mcp add yggdrasil -s user -e "YGG_MUNINN_URL=${URL}" -e "YGG_MUNINN_TOKEN=${TOKEN}" \
        -- "$PYTHON" "$YGG_HOME/scripts/ygg_mcp_server.py" >/dev/null 2>&1 \
        && echo "    registered MCP with Claude Code" || echo "    (claude mcp add failed; register manually)"
    fi
    if command -v codex >/dev/null 2>&1; then
      codex mcp remove yggdrasil >/dev/null 2>&1 || true
      codex mcp add yggdrasil --env "YGG_MUNINN_URL=${URL}" --env "YGG_MUNINN_TOKEN=${TOKEN}" \
        -- "$PYTHON" "$YGG_HOME/scripts/ygg_mcp_server.py" >/dev/null 2>&1 \
        && echo "    registered MCP with Codex" || echo "    (codex mcp add failed; register manually)"
    fi

    echo -n "==> health: "
    for _ in $(seq 1 60); do
      if "$PYTHON" -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('${URL}/health',timeout=2) else 1)" 2>/dev/null; then
        "$PYTHON" -c "import urllib.request,json;print(json.load(urllib.request.urlopen('${URL}/health')))"; break
      fi; sleep 0.5
    done
    echo "==> installed. Engine is on ${URL} and will auto-start at login + restart on crash."
    ;;

  status)
    launchctl print "$domain/$LABEL" 2>/dev/null | grep -E "state =|pid =" || echo "not loaded"
    "$PYTHON" -c "import urllib.request,json;print('health:',json.load(urllib.request.urlopen('${URL}/health',timeout=3)))" 2>/dev/null || echo "health: down"
    ;;
  start) _start; echo "started";;
  stop) _stop; echo "stopped";;
  restart) _stop; sleep 1; _start; echo "restarted";;
  logs) tail -n "${LINES:-40}" "$YGG_HOME/logs/engine.log";;
  token) cat "$YGG_HOME/token";;
  uninstall)
    _stop; rm -f "$PLIST"
    command -v claude >/dev/null 2>&1 && claude mcp remove yggdrasil -s user >/dev/null 2>&1 || true
    command -v codex  >/dev/null 2>&1 && codex mcp remove yggdrasil >/dev/null 2>&1 || true
    echo "uninstalled service + MCP registration. Data kept at $YGG_HOME (rm -rf to remove)."
    ;;
  *) echo "usage: install.sh {install|status|start|stop|restart|logs|token|uninstall}"; exit 2;;
esac
