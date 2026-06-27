# Yggdrasil MCP Facade

`yggdrasil/ygg_mcp_server.py` is a minimal stdio MCP facade over `yggdrasil/ygg.py`.

It is a thin guardrail layer over Yggdrasil's own engine, exposing the workflow guardrails as tools:

- mandatory project-scoped search;
- normalized `metadata.project`;
- normalized `scope`;
- secret guard through `ygg.py`;
- Obsidian materialization.

## Tools

- `ygg_health`
- `ygg_bootstrap`
- `ygg_search`
- `ygg_recall` (cross-project)
- `ygg_remember`
- `ygg_materialize`

## Example Config

See `integrations/mcp.yggdrasil.example.json`.

## Local Smoke Test

The server accepts newline-delimited JSON-RPC over stdio:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n' | yggdrasil/ygg_mcp_server.py
```

For real agent use, start the engine first:

```bash
python3 yggdrasil/ygg_memory_server.py --reset --db /tmp/ygg.sqlite
```
