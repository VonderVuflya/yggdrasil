# Yggdrasil MVP CLI

`scripts/ygg.py` is a thin facade over Muninn REST. It exists so agents do not need to remember Muninn's exact payload shape.

## Environment

```bash
export YGG_MUNINN_URL="http://127.0.0.1:42069"
export YGG_MUNINN_TOKEN="..."
export YGG_NAMESPACE="yggdrasil-demo"
export YGG_USER_ID="global_user"
```

## Commands

Health:

```bash
scripts/ygg.py health
```

Save a project-scoped memory:

```bash
scripts/ygg.py remember \
  --project test-a \
  --type debugging_lesson \
  --json-file examples/layout-overflow-debugging-lesson.json
```

Search before non-trivial work:

```bash
scripts/ygg.py bootstrap --project test-a --query "mobile layout overflow"
```

Search directly:

```bash
scripts/ygg.py search --project test-a --query "scrollWidth clientWidth chips"
```

Materialize a memory to Obsidian Markdown:

```bash
scripts/ygg.py materialize \
  --id MEMORY_ID \
  --project test-a \
  --output-dir vault/04-learnings
```

## Guardrails

- Project memories require `--project`.
- `project` is written into `metadata.project`.
- `scope` is always sent to Muninn and mirrored into metadata.
- The CLI refuses common secret patterns before writeback.
- By default, writeback sets `muninn_skip_extraction=true` for deterministic agent-authored memories.
