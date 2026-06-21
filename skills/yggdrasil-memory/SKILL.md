---
name: yggdrasil-memory
description: Durable, cross-session, cross-project memory for the user's work via Yggdrasil. Use at the START of any non-trivial task to recall prior decisions, solutions, and lessons (ygg_recall / ygg_bootstrap), and AFTER solving something reusable to save it (ygg_remember). Trigger when the user says "have we done this before", "what do we know about X", "remember this", "save this decision/lesson", when starting work in a project that may have history, or when a problem resembles past work. Works with the Yggdrasil MCP tools (ygg_*) or the `ygg` CLI.
license: Elastic-2.0
metadata:
  project: yggdrasil
  homepage: https://github.com/VonderVuflya/yggdrasil
---

# Yggdrasil memory

Yggdrasil is the user's **durable memory** across sessions, tools, and projects.
Treat it as long-term memory you must consult and curate — not as a scratchpad.

## When to use

- **Before** starting non-trivial work → recall what's already known so you
  reuse prior decisions/solutions instead of re-deriving them.
- **When** the user asks "have we done this before", "what do we know about X",
  "what did we decide about Y".
- **After** you solve something reusable (a fix, a decision, a gotcha, a
  convention) → save it so the next session/agent benefits.
- **When** the user says "remember this" / "save this".

## Tools

Prefer the MCP tools if present, otherwise shell out to the `ygg` CLI (same
behavior):

| Goal | MCP tool | CLI |
|---|---|---|
| Find prior work across ALL projects | `ygg_recall` | `ygg recall --query "..."` |
| Find memory scoped to one project | `ygg_bootstrap` / `ygg_search` | `ygg bootstrap --project P --query "..."` |
| Save a reusable memory | `ygg_remember` | `ygg remember --project P --type T --content "..."` |
| Check the engine is up | `ygg_health` | `ygg health` |

## Workflow

### 1. Recall first (read)
At the start of a task, query before acting:
- Cross-project: `ygg_recall(query: "<the problem in a few words>", limit: 5)`.
- Project-scoped (when you know the project): `ygg_bootstrap(project: "<name>",
  query: "<topic>")`.

Skim the hits, note their **provenance** (source / confidence / how often used /
📌 pinned), and **reuse** what applies. If something contradicts the current
situation, say so rather than blindly trusting it — memories are point-in-time.

### 2. Remember after (write)
When you produce something worth keeping, save **one fact per memory**:
`ygg_remember(project: "<name>", type: "<decision|lesson|convention|fix|...>",
content: "<the durable fact, self-contained>")`.

Good candidates: a decision and its rationale, a non-obvious fix, a project
convention, a gotcha that cost time. Skip: things derivable from the code, git
history, or that only matter to this one conversation.

## Conventions

- **Scope by project.** Always pass a real `project` name for saves and
  project-scoped reads; use `ygg_recall` (no project) only for cross-project
  lookups.
- **One fact per memory.** Keep `content` self-contained and specific. Convert
  relative dates ("yesterday") to absolute.
- **Never store secrets.** No tokens, API keys, passwords. The engine refuses
  common secret patterns, but don't rely on that — don't try.
- **Don't dump.** Recall the few relevant memories and act; don't paste the
  whole store into the chat.

## If the tools aren't available

The engine may be down or the MCP/CLI not installed. Check with `ygg health`
(or `ygg_health`). If it's unreachable, tell the user to run `ygg start` /
`ygg doctor`, and continue without memory rather than blocking.
