# Yggdrasil MVP Agent Protocol

## Startup

1. Read `AI_MEMORY_INDEX.txt`.
2. Determine the active project before doing non-trivial work.
3. Search Muninn before asking the user to repeat context.
4. Use context-mode for large outputs, logs, broad scans, and session continuity.

## Retrieval

- Search project-scoped memories with `metadata.project` and `scope="project"`.
- Include global memories only when looking for stable user preferences or universal rules.
- Prefer memories with evidence, commands, files, commits, or reproducible signals.
- If memory and repo reality disagree, trust the repo and save a correction/stale-memory note.

## Writeback

After bugfixes, decisions, or repeated workflows, save reusable knowledge rather than just outcome summaries.

Required `debugging_lesson` fields:
- problem
- symptoms
- failed_approaches
- working_solution
- recognition_signals
- commands/files/evidence
- next_time

## Boundaries

- Do not save secrets, credentials, tokens, private keys, raw `.env`, or sensitive logs.
- Do not save noisy one-off facts unless they are likely to help future agents.
- Do not cross project boundaries. Project memory requires explicit project id.
- Do not build a custom memory engine until Muninn is proven insufficient.

## Session Close

For meaningful work, close with:
- what changed
- reusable lessons
- failed paths to avoid
- decisions made
- docs that may be stale
- follow-ups
