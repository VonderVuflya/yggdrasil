# Yggdrasil

A thin, agent-agnostic **memory + governance layer** so coding agents (Claude
Code, Codex, and any MCP host) share one durable, inspectable project memory —
backed by its own lightweight engine and materialized into an Obsidian vault.

> Status: **alpha / working prototype.** The happy path and the full review
> governance loop are covered by passing gates (see below). Not production
> hardened. Honest about what works — every claim here is backed by a gate you
> can run.

## What's here

- **Own memory engine** — `scripts/ygg_memory_server.py`: a stdlib-only HTTP
  server over SQLite + FTS5. Zero heavy dependencies. The default backend.
- **Agent facade** — `scripts/ygg.py` (CLI) + `scripts/ygg_mcp_server.py` (MCP
  stdio). Secret-refusal guard and content-hash dedupe live here.
- **Governance loop** — `scripts/ygg_review_queue.py` →
  `scripts/ygg_review_actions.py`: surfaces duplicate / stale / conflicting
  memories and applies **non-destructive** actions (`archive`,
  `merge_proposal`, `verify_or_archive`) only after explicit approval.
- **Obsidian** — memories materialize to Markdown notes (a readable view).

## Quick start

```bash
# start engine, seed fixtures, run every gate, tear down — one command:
scripts/run_gates.sh

# or run the engine yourself:
python3 scripts/ygg_memory_server.py --reset --db /tmp/ygg.sqlite
```

Cross-agent shared memory over MCP (writer + reader are separate sessions):

```bash
python3 scripts/ygg_cross_agent_demo.py
```

See `docs/reproducible-demo.md` for the full flow and `docs/backend-boundary.md`
for the engine contract.

## Gates (the test suite that backs the status claims)

| Gate | Proves |
| --- | --- |
| `ygg_quality_gate.py` | health, bootstrap, project isolation, secret guard, Obsidian materialize, MCP facade |
| `ygg_dense_gate.py` | paraphrase retrieval (FTS5), isolation, wrapper dedupe guard |
| `ygg_review_apply_gate.py` | exact-duplicate detection → approved archive → follow-up queue ignores it |
| `ygg_governance_gate.py` | near-duplicate `merge_proposal` + stale `verify_or_archive`, non-destructive |

All four pass on the bundled engine (`scripts/run_gates.sh`).

## Backend strategy

The workflow layer talks to a small REST contract (`MemoryBackend` in
`scripts/ygg_core.py`), so the engine is swappable:

- **Default:** the bundled own engine. No external service, no model downloads.
- **Optional:** an external **Muninn** instance
  (`github.com/wjohns989/Muninn`, Apache-2.0, third party — NOT bundled).
  Point `YGG_MUNINN_URL`/`YGG_MUNINN_TOKEN` at it. It needs a small
  metadata-update shim; see `docs/backend-boundary.md`. Preserve its
  `NOTICE`/attribution if you redistribute.

The "couple of genuinely useful" things an external engine adds (reranking,
temporal validity) are tracked in `../ROADMAP.md` as native features to build
under our own contract rather than depend on a third-party runtime.

## Migrating existing memory

Claude Code accumulates per-project memory under
`~/.claude/projects/<sanitized>/memory/`. Import it into Yggdrasil (drives the
real `ygg.py remember` path — secret guard + dedupe — then materializes notes):

```bash
python3 scripts/ygg_import_claude_memory.py \
  --source-dir ~/.claude/projects/<sanitized>/memory \
  --project <name> --materialize
```

Dogfooded on real projects: existing Claude-memory lessons import cleanly and
are retrievable by symptom (e.g. "service won't start after an image upgrade" →
the matching environment-corruption lesson ranks first).

## Known limitations

- Retrieval is lexical: FTS5/BM25 relevance blended with an importance +
  recency boost. Good enough for v1; dense/embedding ranking is a roadmap item,
  not shipped.
- The importer stores each source note's full Markdown (including its original
  frontmatter) as the memory body, so materialized notes have nested
  frontmatter and an empty `confidence`. Cosmetic; strip-on-import is a polish
  item.

The engine has unit tests (`tests/test_ygg_memory_server.py`, run via
`python3 -m unittest`) in addition to the integration gates.
