# Yggdrasil × autoresearch

[karpathy/autoresearch](https://github.com/karpathy/autoresearch) is an autonomous
ML-research loop: an agent edits `train.py`, trains for a fixed 5-minute budget,
measures `val_bpb`, keeps or reverts, and repeats — ~100 experiments overnight.

Its one missing piece is **memory**. Each session the agent wakes up cold and
only sees whatever is in the repo's experiment log — it has no durable, searchable
memory of what was already tried across nights, machines, or forks.

**That's exactly Yggdrasil's job.** Plug Yggdrasil in and the loop *compounds*:
the agent recalls past experiments before proposing the next one (so it stops
re-running known-bad ideas) and remembers every result as durable memory.

> This is **not** "the same as autoresearch." autoresearch is the **action/eval
> loop**; Yggdrasil is the **long-term memory** that loop was missing. They compose.

## Setup

1. Install & run Yggdrasil so its MCP tools are available to your agent:
   ```bash
   uvx --from yggdrasil-memory ygg install   # registers ygg_* with Claude Code / Codex
   ```
2. In your `autoresearch` checkout, append our memory block to `program.md`:
   ```bash
   cat path/to/yggdrasil/integrations/autoresearch/program.ygg.md >> program.md
   ```
3. Start your agent in the autoresearch repo as usual and kick off experiments.
   It will now `ygg_recall` before each experiment and `ygg_remember` each result.

## What you get

- **Compounding overnight runs** — night 2 starts from night 1's lessons, not cold.
- **Cross-fork / cross-machine memory** — lessons follow *you*, not the repo.
- **A searchable experiment history** — `ygg recall --query "best val_bpb so far"` any time.

See [`program.ygg.md`](./program.ygg.md) for the exact agent instructions.
