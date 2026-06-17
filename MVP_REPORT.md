# Yggdrasil MVP Demo Report

Date: 2026-05-26

## MVP Plan

1. Use context-mode for large-output analysis and session continuity.
2. Use Muninn as the durable memory backend.
3. Keep Yggdrasil as a thin workflow/materialization layer.
4. Validate project isolation before building custom memory logic.
5. Export useful memories to Obsidian-readable Markdown.

## Muninn Setup

- Repo: `./Muninn`
- Server: `http://127.0.0.1:42069`
- Data dir: `./muninn-data-fallback`
- Auth token used for demo: `yggdrasil-demo-token`
- Strict project mode: `MUNINN_PROJECT_SCOPE_STRICT=1`
- Namespace: `yggdrasil-demo`

Health check:

```json
{
  "status": "ok",
  "memory_count": 3,
  "vector_count": 3,
  "bm25_size": 3,
  "backend": "muninn-native"
}
```

## Backend Findings

- Muninn server runs locally and exposes `/health`, `/add`, `/search`, and `/get_all`.
- Project id is passed via `metadata.project`, not as a top-level REST field.
- `scope` is top-level on `/add`; for project memories use `scope="project"`.
- Strict project isolation worked in the REST checks when searches included `filters.project`.
- Search found the saved `debugging_lesson` by symptom terms: `scrollWidth clientWidth chips overflow`.

## Demo Memories

- `test-a`: Hotel Milano mobile hero overflow memory.
- `test-b`: Billing webhook signature mismatch memory.
- `test-a`: `debugging_lesson` for mobile layout overflow.

Key IDs:

- `cf629bf5-b526-4a6a-bb9a-d3aa7656ed13`: test-a overflow memory
- `c56c3d6e-e82b-4899-8f4c-7a89070bbdc6`: test-b webhook memory
- `74c21c9b-0e9c-43e1-aed6-eb3f26ebd12c`: test-a debugging_lesson

Isolation result:

```json
{
  "test_a_contains_b": false,
  "test_b_contains_a": false,
  "lesson_found_by_symptoms": true
}
```

## Known Blockers

- `pip install -e .` missed runtime dependency `aiohttp`; manual install was required.
- Default embedding model tried to download about 548 MB at startup.
- Smaller model still required runtime Hugging Face download and stalled in this environment.
- For demo, `fastembed` was removed so Muninn used fallback embeddings. This validates REST, storage, BM25, and isolation, but not dense-vector quality.

## Obsidian Materialization

- Script: `./scripts/materialize_muninn_memory.py`
- Thin CLI facade: `./scripts/ygg.py`
- Input example: `./debugging_lesson_record.json`
- Output note: `./vault/04-learnings/test-a-debugging-lesson-74c21c9b.md`

## Ygg CLI Smoke Test

The second MVP slice added `scripts/ygg.py`, a small stdlib-only facade over Muninn REST.

Validated commands:

- `ygg.py health`
- `ygg.py bootstrap --project test-a --query "mobile overflow chips"`
- `ygg.py remember --project test-a --type debugging_lesson --json-file examples/layout-overflow-debugging-lesson.json`
- `ygg.py search --project test-a --query "chip bounding rect exceeds viewport next time 390 768 1200"`
- `ygg.py materialize --id b02daf01-bdab-4896-991d-54fc0546f4b1 --project test-a --output-dir vault/04-learnings`

Additional output note:

- `./vault/04-learnings/test-a-debugging-lesson-b02daf01.md`

Guardrail check:

- The CLI refused to save a fake `sk-...` API key pattern.

New caveat:

- In fallback mode without `fastembed`, semantic dedupe is weak; saving the same lesson shape again created a duplicate. Treat this as a quality gate for the next slice with a pre-cached embedding model.

## Reproducible Demo Gate

The third MVP slice added a repeatable launcher and quality gate:

- Launcher: `./scripts/run_muninn_demo.sh fallback`
- Dense-mode launcher: `./scripts/run_muninn_demo.sh dense-small`
- Gate: `./scripts/ygg_quality_gate.py`
- Repro docs: `./docs/reproducible-demo.md`

Latest quality gate:

- Report: `./reports/quality-gate-1779821211.json`
- Status: pass
- Checks:
  - health ok
  - bootstrap finds test-a lesson
  - test-a does not leak test-b
  - test-b does not leak test-a
  - secret guard blocks fake `sk-...`
  - materialized note has required YAML frontmatter

Post-run note:

- The first fallback launcher run surfaced a vector warning because existing demo data used 384-dimensional vectors while fallback defaults were 768-dimensional. `run_muninn_demo.sh fallback` now pins `MUNINN_EMBEDDING_MODEL=BAAI/bge-small-en-v1.5` and `MUNINN_EMBEDDING_DIMS=384` to match the demo store.

## Agent Integration Pack

The fourth MVP slice added installable agent-facing integration artifacts:

- MCP facade: `./scripts/ygg_mcp_server.py`
- MCP docs: `./docs/mcp-facade.md`
- MCP config example: `./integrations/mcp.yggdrasil.example.json`
- Codex instructions template: `./integrations/AGENTS.yggdrasil.md`
- Claude instructions template: `./integrations/CLAUDE.yggdrasil.md`

MCP facade tools:

- `ygg_health`
- `ygg_bootstrap`
- `ygg_search`
- `ygg_remember`
- `ygg_materialize`

Latest quality gate with MCP facade:

- Report: `./reports/quality-gate-1779822944.json`
- Status: pass
- Added check: `mcp_facade_ok=true`

## Dense-Small Gate

The fifth MVP slice validated dense retrieval with a small local FastEmbed model:

- Model: `BAAI/bge-small-en-v1.5`
- Dimensions: `384`
- Pre-cache required one Hugging Face download of about 67 MB.
- Launcher: `./scripts/run_muninn_demo.sh dense-small`
- Gate: `./scripts/ygg_dense_gate.py`
- Latest report: `./reports/dense-gate-1779823651.json`
- Status: pass

Validated:

- Muninn loaded `fastembed/BAAI/bge-small-en-v1.5`.
- Paraphrase query found the relevant `dense-a` mobile-overflow lesson.
- Project isolation held for `dense-a` and `dense-b`.
- Ygg wrapper exact duplicate guard worked via `content_hash`.

Important backend observation:

- Muninn backend still added an exact duplicate as a new memory in this test. The Ygg wrapper guard is currently required for exact duplicate safety.

## Memory Review Queue

The sixth MVP slice added a governance review queue:

- Scanner: `./scripts/ygg_review_queue.py`
- Docs: `./docs/memory-review-queue.md`
- Latest JSON report: `./reports/review-queue-1779823862.json`
- Latest Markdown queue: `./vault/99-review/memory-review-queue.md`

Latest dense-user scan:

- status: `review_needed`
- memory_count: 7
- issue_count: 4
- issue kinds:
  - exact duplicate in `dense-a`
  - exact duplicate in `dense-b`
  - near duplicate in `dense-a`
  - near duplicate in `dense-b`

Implementation note:

- The first stale/conflict marker pass falsely flagged the phrase "stale signing secret" as stale memory. The scanner now only treats explicit memory-status phrases or metadata status as stale/conflict markers.

## Review Actions

The seventh MVP slice added explicit review action proposals:

- Action generator: `./scripts/ygg_review_actions.py`
- Docs: `./docs/review-actions.md`
- Latest action bundle: `./reports/review-actions-1780001070.json`
- Latest Markdown action view: `./vault/99-review/memory-review-actions.md`
- Audit log: `./reports/review-action-audit.jsonl`

Latest proposal run:

- source review report: `./reports/review-queue-1779823862.json`
- action_count: 8
- actions:
  - `keep` canonical exact duplicate records
  - `archive` exact duplicates after user approval
  - `merge_proposal` near-duplicate groups

Audit smoke:

- Recorded `merge-proposal-3` as `needs-info` with actor `codex-demo`.
- No Muninn backend mutation was performed.

## Approved Archive Apply Flow

The eighth MVP slice added an explicit, safe apply workflow for approved archive actions:

- `scripts/ygg_review_actions.py apply --actions-report REPORT --dry-run`
- `scripts/ygg_review_actions.py apply --actions-report REPORT --execute`

Behavior:

- dry-run is the default unless `--execute` is passed;
- only the latest `approve` decision in `reports/review-action-audit.jsonl` is eligible;
- only `archive` actions are supported;
- memories are not deleted;
- archive is recorded through Muninn `/update` using `metadata_patch` plus top-level `archived=true`;
- every dry-run, applied, failed, missing, or already-archived attempt is appended to the audit log;
- `scripts/ygg_review_queue.py` ignores archived memories via either `metadata.status=archived` or top-level `archived=true`.

Implementation note:

- Muninn's core `memory.update()` already supported metadata patching, but the REST `UpdateMemoryRequest` exposed only `data`. The local demo shim now forwards `metadata_patch` and `archived` to the existing core update path.
- Metadata-only updates also needed `chain_links_created=0` and `entity_names=[]` defaults in `memory.update()`.

Smoke result:

- Approved `archive-1-42285633` for duplicate `42285633-d153-4fb3-83e8-0aaea0185f75`.
- Dry-run previewed the metadata patch.
- Execute returned `success=true`.
- Follow-up review queue report: `./reports/review-queue-1780002098.json`.
- Active memory count dropped from 7 to 6 because archived memory is now ignored.

Repeatable gate:

- Script: `./scripts/ygg_review_apply_gate.py`
- Behavior: creates an isolated duplicate pair, runs queue/propose/approve/dry-run/execute, checks persisted archive metadata, and checks that the next review queue ignores the archived duplicate.
- Latest report: `./reports/review-apply-gate-1780083335.json`
- Status: pass

## End-to-End Tool Trial

The tool was exercised as an agent-facing workflow, not only as individual gates:

- Quality gate: `./reports/quality-gate-1780083385.json`, status pass.
- Dense gate: `./reports/dense-gate-1780083812.json`, status pass.
- Real lesson saved through `scripts/ygg.py remember`: `daa4b9e6-81db-4cbb-8d1c-8f5de2d468cf`.
- `scripts/ygg.py bootstrap` found the lesson by metadata-only update symptoms.
- `scripts/ygg.py materialize` wrote `./vault/04-learnings/yggdrasil-demo-debugging-lesson-daa4b9e6.md`.
- Re-saving the same lesson returned `YGG_DUPLICATE_SKIP`.

Dense-gate observation remains unchanged:

- `backend_duplicate_not_added=false`, so Muninn still accepts exact duplicates directly.
- `ygg_duplicate_guard=true`, so the Ygg wrapper guard is still required.

## Backend Boundary Hardening

The ninth MVP slice removed an architectural half-measure in the review/apply tooling:

- Shared backend adapter: `./scripts/ygg_core.py`
- Contract docs: `./docs/backend-boundary.md`
- Unit tests: `./tests/test_ygg_core.py`

The review queue, review actions, and review apply gate now use `MuninnBackend` instead of constructing raw REST calls locally.

Architectural rule:

- Yggdrasil workflow code depends on a backend contract, not on scattered `urllib` calls.
- `archive_memory` is an explicit non-destructive backend operation.
- If the configured backend does not expose `metadata_patch` / `archived` through `/update`, Yggdrasil raises `BackendCapabilityError` at the adapter boundary.
- Ygg duplicate detection ignores archived records, so an archived stale duplicate does not block a new replacement memory.

Verification after hardening:

- Unit tests: `python -m unittest discover -s tests -p 'test_*.py'`, pass.
- Review apply gate: `./reports/review-apply-gate-1780086160.json`, status pass.
- Quality gate: `./reports/quality-gate-1780086256.json`, status pass.
- Dense gate: `./reports/dense-gate-1780086979.json`, status pass.

## Recommendation

Use Muninn as-is for the next MVP slice, with a thin Yggdrasil wrapper that:

- normalizes `project` into `metadata.project`;
- always sends `scope`;
- enforces `MUNINN_PROJECT_SCOPE_STRICT=1`;
- stores reusable lesson schemas;
- materializes selected records to Obsidian Markdown;
- refuses secrets;
- records evidence and repo references.
- performs exact duplicate preflight using `content_hash`.
- surfaces duplicate/stale/conflict candidates through a review queue rather than auto-deleting memories.
- turns review queue items into proposed actions and audit log entries before any backend mutation.
- applies approved archive actions through an explicit audited non-destructive flow.
- verifies approved archive application through a repeatable gate.
- routes Yggdrasil backend access through an explicit adapter contract.

Do not fork yet. Do not build a custom memory engine yet.

Next technical step: upstream or vendor-pin the Muninn REST metadata-patch support, then move remaining CLI/MCP codepaths onto the backend adapter and add reviewed merge/verify flows.
