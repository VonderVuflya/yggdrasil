# Prompt For Next Session: Yggdrasil MVP Continuation

Ты продолжаешь работу над MVP системы долговременной самообучающейся памяти для AI-агентов. Рабочее название верхнего workflow layer: **Yggdrasil**.

## Goal

Построить тонкий workflow/governance слой поверх готового memory backend, чтобы Codex GUI, Codex CLI, Claude Code, Hermes, Cursor/VS Code и будущие MCP-compatible агенты использовали одну общую durable память без постоянных ручных напоминаний.

Главный сценарий:

1. Агент решает проблему.
2. После решения сохраняется reusable lesson:
   - problem;
   - symptoms;
   - failed approaches;
   - working solution;
   - recognition signals;
   - commands/files/evidence;
   - next_time guidance.
3. В новой сессии или похожей задаче агент сам находит lesson и не решает проблему с нуля.
4. Память изолирована по проектам.
5. Память экспортируется в Obsidian-readable Markdown.

## Architecture Decision

Не писать memory engine с нуля.

Use:

- **context-mode**: экономия токенов, sandboxed large-output processing, session continuity.
- **Muninn**: durable local-first memory backend, REST/MCP/Python SDK, project/global scopes, SQLite + Qdrant + KuzuDB.
- **Yggdrasil**: workflow layer: agent protocol, Obsidian materialization, exact duplicate guard, review queue, review actions, future docs drift/skill promotion loops.

Current verdict:

- Muninn is good enough as backend for the MVP.
- Yggdrasil wrapper is required for:
  - consistent `metadata.project`;
  - consistent `scope`;
  - exact duplicate guard via `content_hash`;
  - secret guard;
  - review/governance workflow;
  - Obsidian materialization.
- Do not fork Muninn yet.
- Do not build a custom memory engine yet.

## Project/Demo Location

Work under:

```text
/Users/vuflya/Documents/Codex/2026-05-25/obsidian-codex-twitter-obsidian-hermes-agents/yggdrasil-demo
```

Important files:

```text
MVP_REPORT.md
AI_MEMORY_INDEX.txt
NEXT_SESSION_PROMPT.md

scripts/ygg.py
scripts/ygg_mcp_server.py
scripts/run_muninn_demo.sh
scripts/ygg_quality_gate.py
scripts/ygg_dense_gate.py
scripts/ygg_review_queue.py
scripts/ygg_review_actions.py
scripts/materialize_muninn_memory.py

docs/agent-protocol.md
docs/ygg-cli.md
docs/reproducible-demo.md
docs/mcp-facade.md
docs/memory-review-queue.md
docs/review-actions.md

integrations/AGENTS.yggdrasil.md
integrations/CLAUDE.yggdrasil.md
integrations/mcp.yggdrasil.example.json

vault/04-learnings/
vault/99-review/
reports/
```

Muninn repo is cloned at:

```text
yggdrasil-demo/Muninn
```

Python venv:

```text
yggdrasil-demo/.venv
```

Installed dependencies:

```bash
.venv/bin/pip install -e Muninn
.venv/bin/pip install aiohttp
.venv/bin/pip install fastembed==0.8.0
```

## Important Runtime Notes

Muninn default setup had issues:

- `aiohttp` was missing from runtime deps, had to install manually.
- Default embedding model tried to download about 548 MB.
- Smaller model `BAAI/bge-small-en-v1.5` required about 67 MB download.
- Interrupted model download corrupted FastEmbed cache once; fixed by deleting:

```text
/var/folders/wm/f5p9ljjj67jcg2v5l8wt652c0000gn/T/fastembed_cache/models--qdrant--bge-small-en-v1.5-onnx-q
```

Dense model now works:

```text
fastembed/BAAI/bge-small-en-v1.5
dimensions: 384
```

Use launchers, not ad hoc env commands:

```bash
cd /Users/vuflya/Documents/Codex/2026-05-25/obsidian-codex-twitter-obsidian-hermes-agents/yggdrasil-demo

scripts/run_muninn_demo.sh fallback
scripts/run_muninn_demo.sh dense-small
```

Both modes use local demo data dirs:

```text
muninn-data-fallback
muninn-data-dense-small
```

Server:

```text
http://127.0.0.1:42069
token: yggdrasil-demo-token
```

Always stop the server after checks.

## What Has Been Completed

### 1. Muninn Backend Validation

Validated:

- `/health`
- `/add`
- `/search`
- `/get_all`
- project scopes:
  - `test-a`
  - `test-b`
- `MUNINN_PROJECT_SCOPE_STRICT=1`
- project isolation held.

Saved example `debugging_lesson` in `test-a`.

Search by symptoms found lesson:

```text
scrollWidth clientWidth chips overflow
```

### 2. Obsidian Materialization

Created:

```text
scripts/materialize_muninn_memory.py
vault/04-learnings/test-a-debugging-lesson-74c21c9b.md
vault/04-learnings/test-a-debugging-lesson-b02daf01.md
```

Required frontmatter:

```yaml
id:
type:
project:
scope:
confidence:
created_at:
source:
```

### 3. Thin CLI Facade

Created:

```text
scripts/ygg.py
```

Commands:

```bash
scripts/ygg.py health
scripts/ygg.py bootstrap --project PROJECT --query "..."
scripts/ygg.py search --project PROJECT --query "..."
scripts/ygg.py remember --project PROJECT --type debugging_lesson --json-file lesson.json
scripts/ygg.py materialize --id MEMORY_ID --project PROJECT
```

Guardrails:

- project required for project-scoped memory;
- normalizes `metadata.project`;
- always sends `scope`;
- refuses common secret patterns;
- exact duplicate preflight using `content_hash`;
- deterministic agent writeback defaults to `muninn_skip_extraction=true`.

### 4. Quality Gate

Created:

```text
scripts/ygg_quality_gate.py
```

Latest report:

```text
reports/quality-gate-1779822944.json
```

Status: pass.

Checks:

- health;
- bootstrap finds test-a lesson;
- test-a does not leak test-b;
- test-b does not leak test-a;
- secret guard blocks fake `sk-...`;
- materialized note has required YAML frontmatter;
- MCP facade works.

### 5. MCP Facade

Created:

```text
scripts/ygg_mcp_server.py
integrations/mcp.yggdrasil.example.json
docs/mcp-facade.md
```

MCP tools:

```text
ygg_health
ygg_bootstrap
ygg_search
ygg_remember
ygg_materialize
```

Validated:

- JSON-RPC `initialize`;
- `tools/list`;
- `tools/call ygg_bootstrap`;
- secret guard returns `isError=true`.

### 6. Dense Retrieval Gate

Created:

```text
scripts/ygg_dense_gate.py
```

Latest report:

```text
reports/dense-gate-1779823651.json
```

Status: pass.

Checks:

```json
{
  "health_ok": true,
  "paraphrase_finds_dense_a": true,
  "dense_a_no_dense_b_leak": true,
  "dense_b_no_dense_a_leak": true,
  "backend_duplicate_not_added": false,
  "ygg_duplicate_guard": true
}
```

Important finding:

- Dense retrieval works.
- Project isolation holds.
- Muninn backend still added exact duplicates.
- Ygg wrapper exact duplicate guard works and is required.

### 7. Memory Review Queue

Created:

```text
scripts/ygg_review_queue.py
docs/memory-review-queue.md
```

Latest report:

```text
reports/review-queue-1779823862.json
vault/99-review/memory-review-queue.md
```

Status:

```json
{
  "status": "review_needed",
  "memory_count": 7,
  "issue_count": 4
}
```

Issues found:

- exact duplicate in `dense-a`;
- exact duplicate in `dense-b`;
- near duplicate in `dense-a`;
- near duplicate in `dense-b`.

Important fix:

- Initial stale detector falsely flagged phrase “stale signing secret”.
- Detector now only flags explicit memory-status phrases or `metadata.status`.

### 8. Review Actions

Created:

```text
scripts/ygg_review_actions.py
docs/review-actions.md
reports/review-actions-1780001070.json
vault/99-review/memory-review-actions.md
reports/review-action-audit.jsonl
```

Generated proposed actions from latest review queue:

```json
{
  "action_count": 8,
  "source_review_report": "reports/review-queue-1779823862.json"
}
```

Action types:

- `keep`
- `archive`
- `merge_proposal`
- `verify_or_archive`

Audit smoke:

- Recorded `merge-proposal-3` as `needs-info`.
- No Muninn backend mutation performed.

## Current State

We now have:

- Muninn backend validated.
- CLI facade.
- MCP facade.
- Obsidian materialization.
- Fallback and dense modes.
- Quality gates.
- Dense retrieval check.
- Exact duplicate guard in Ygg wrapper.
- Review queue.
- Review action proposals.
- Audit log.

The system is now a real MVP demo, not only a research note.

## Next Step

Implement explicit, safe `--apply` workflow for **approved archive actions**.

Why:

- Review queue finds duplicates.
- Review actions propose `archive`.
- Audit log can record approvals.
- But no backend mutation exists yet.

Goal for next session:

1. Add `apply` command to `scripts/ygg_review_actions.py`.
2. Only apply actions that have an `approve` decision in `reports/review-action-audit.jsonl`.
3. Only support `archive` initially.
4. Do not delete records physically.
5. Archive by calling Muninn `/update` and setting metadata/status fields, e.g.:

```json
{
  "metadata.status": "archived",
  "metadata.archived_by": "ygg_review_actions",
  "metadata.archived_at": "...",
  "metadata.archive_reason": "...",
  "metadata.canonical_memory_id": "..."
}
```

Check Muninn update API shape before implementing. Existing server has:

```text
PUT /update
```

and `server.py` endpoint calls:

```python
memory.update(req.memory_id, req.data)
```

Need inspect `UpdateMemoryRequest` / `memory.update` / SQLite update behavior before applying.

6. Add dry-run default:

```bash
scripts/ygg_review_actions.py apply --actions-report REPORT --dry-run
```

7. Require explicit:

```bash
scripts/ygg_review_actions.py apply --actions-report REPORT --execute
```

8. Append every attempted mutation to audit log.
9. Add quality check:
   - approve one known `archive-*` action;
   - dry-run shows it;
   - execute archives it;
   - review queue no longer includes archived memory, or scanner clearly ignores `metadata.status=archived`.

10. Update:

```text
MVP_REPORT.md
AI_MEMORY_INDEX.txt
docs/review-actions.md
```

## Suggested First Commands In Next Session

Use context-mode for large outputs.

```bash
cd /Users/vuflya/Documents/Codex/2026-05-25/obsidian-codex-twitter-obsidian-hermes-agents/yggdrasil-demo
```

Inspect update API:

```bash
rg -n "class UpdateMemoryRequest|def update|/update" Muninn/server.py Muninn/muninn
```

Start dense backend if needed:

```bash
scripts/run_muninn_demo.sh dense-small
```

Current review artifacts:

```bash
scripts/ygg_review_queue.py --user-id dense-user
scripts/ygg_review_actions.py propose --review-report reports/review-queue-1779823862.json
```

## Important Constraints

- Do not write to home directory for MVP.
- Do not build custom memory engine.
- Do not fork Muninn yet.
- Do not delete memories automatically.
- Do not save secrets.
- If memory conflicts with repo reality, repo wins.
- Use context-mode for large outputs.
- Use `rdrr "{url}"` instead of WebFetch for web pages.

## One-Sentence Brief For The Next Agent

Continue Yggdrasil MVP by adding a safe audited `apply` flow for approved review actions, starting with non-destructive archive of duplicate Muninn memories, while preserving the thin-wrapper architecture over Muninn and keeping all demo artifacts under `yggdrasil-demo`.

## 2026-05-29 Continuation Update

The approved archive apply flow is now implemented and tested.

Added:

- `scripts/ygg_review_actions.py apply`
- `scripts/ygg_review_apply_gate.py`
- Muninn demo REST shim for `/update` with `metadata_patch` and `archived`
- metadata-only `memory.update()` defaults for `chain_links_created` and `entity_names`
- archived-memory filtering in `scripts/ygg_review_queue.py`

Latest passing reports:

- `reports/review-apply-gate-1780083335.json`
- `reports/quality-gate-1780083385.json`
- `reports/dense-gate-1780083812.json`

Dogfood result:

- Saved real reusable lesson via `scripts/ygg.py remember`: `daa4b9e6-81db-4cbb-8d1c-8f5de2d468cf`
- Bootstrap found it by symptoms.
- Materialized note: `vault/04-learnings/yggdrasil-demo-debugging-lesson-daa4b9e6.md`
- Duplicate re-save returned `YGG_DUPLICATE_SKIP`.

Current next step:

1. Decide whether to upstream the Muninn REST `metadata_patch` / `archived` support or keep it as a demo shim.
2. Add reviewed `merge_proposal` and `verify_or_archive` execution flows.
3. Dogfood the MCP facade from actual Codex/Hermes/Cursor-style integration instructions.

## 2026-05-29 Architecture Hardening Update

User explicitly chose architecture maturity over MVP shortcuts.

Added:

- `scripts/ygg_core.py`
- `docs/backend-boundary.md`
- `tests/test_ygg_core.py`

Changed:

- `scripts/ygg_review_queue.py`, `scripts/ygg_review_actions.py`, and `scripts/ygg_review_apply_gate.py` now use `MuninnBackend` instead of local raw REST helpers.
- `scripts/ygg.py` duplicate guard ignores archived records.
- `MuninnBackend.archive_memory()` is the explicit non-destructive mutation path.
- Missing backend metadata-update support raises `BackendCapabilityError`.

Latest passing checks after refactor:

- Unit tests: 4 passed.
- `reports/review-apply-gate-1780086160.json`
- `reports/quality-gate-1780086256.json`
- `reports/dense-gate-1780086979.json`

Next architectural step:

1. Upstream or vendor-pin Muninn `/update` metadata patch support.
2. Move remaining CLI/MCP/gate direct REST calls onto `scripts/ygg_core.py`.
3. Add reviewed `merge_proposal` and `verify_or_archive` execution flows.
