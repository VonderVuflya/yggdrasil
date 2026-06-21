# Yggdrasil for Claude Desktop (`.mcpb` extension)

Connect the **Claude Desktop** app to your local Yggdrasil engine, so Claude on
the desktop shares the **same durable memory** as Claude Code and Codex.

This is a thin **MCP** facade (stdio): it does not store anything itself — it
talks to the Yggdrasil engine you already run (default
`http://127.0.0.1:42069`). Zero Python dependencies; it runs on your system
`python3`.

> Why a bundle and not `uvx`? macOS launches GUI apps with a minimal `PATH`, so
> `uvx` / `uv` (in `~/.local/bin`) usually aren't visible to Claude Desktop. The
> bundle ships the (zero-dep) facade and runs it with the system `python3`,
> which is always on the GUI `PATH`.

---

## Prerequisites

1. **Yggdrasil installed and running.**
   ```bash
   uvx --from yggdrasil-memory ygg install   # one-time
   ygg status                                # should report the engine is up
   ```
2. **`python3` available** (macOS ships it via the Command Line Tools; if
   missing: `xcode-select --install`).

## Install (drag-and-drop)

1. Download / locate the bundle: **`packaging/mcpb/yggdrasil-<version>.mcpb`**
   (in this repo).
2. Open **Claude Desktop → Settings → Extensions** (a.k.a. *Add Extension*).
3. **Drag the `.mcpb` file** onto the "Drag .MCPB or .DXT files here to install"
   drop zone (or use *Install from file*).
4. When prompted for configuration:
   - **Engine token** — paste the output of:
     ```bash
     ygg token        # or:  cat ~/.yggdrasil/token
     ```
   - **Engine URL** — leave the default `http://127.0.0.1:42069` for a normal
     local install.
5. Enable the extension. You should now see the `ygg_*` tools available.

## Verify

In a Claude Desktop chat, ask something that needs memory, e.g.
*"Use ygg_recall to find what we know about Yggdrasil."* — Claude should call the
tool and return your stored memories. The tool list should contain:
`ygg_health`, `ygg_bootstrap`, `ygg_search`, `ygg_recall`, `ygg_remember`,
`ygg_materialize`.

---

## Rebuild the bundle (maintainers)

The bundle is just a ZIP of `manifest.json` + the zero-dep payload
(`ygg_mcp_server.py`, `ygg.py`, `ygg_core.py`), staged from the live package so
there's nothing to drift:

```bash
bash packaging/mcpb/build.sh        # -> packaging/mcpb/yggdrasil-<version>.mcpb
```
Bump `version` in `packaging/mcpb/manifest.json` to match the package before
building (the script enforces this).

## Manual fallback (no `.mcpb`)

If your Claude Desktop build can't load extensions, wire the MCP server by hand.
Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "yggdrasil": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/yggdrasil/ygg_mcp_server.py"],
      "env": {
        "YGG_ENGINE_URL": "http://127.0.0.1:42069",
        "YGG_ENGINE_TOKEN": "PASTE_FROM_ygg_token"
      }
    }
  }
}
```
Point `args` at the deployed copy (e.g. `~/.yggdrasil/scripts/ygg_mcp_server.py`)
or the one inside an unzipped bundle. Restart Claude Desktop afterwards.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Tools never appear / server fails to start | Ensure `python3` resolves on a minimal PATH: `/usr/bin/python3 --version`. If missing, `xcode-select --install`. |
| `401` / auth errors in tool output | Token mismatch — re-copy `ygg token` into the extension's settings. |
| `engine not reachable` | The daemon isn't up: `ygg start` (or `ygg status` / `ygg doctor`). |
| Memories differ from Claude Code | The facade defaults to namespace `yggdrasil-demo` / user `demo-user` — the same as Claude Code's MCP. If you customized those for Claude Code, set matching `YGG_NAMESPACE` / `YGG_USER_ID` via the manual-config route. |

See the project root [`README.md`](../../README.md) for the full picture.
