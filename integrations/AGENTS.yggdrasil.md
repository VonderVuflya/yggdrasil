# Yggdrasil Memory Protocol

Before non-trivial work:

1. Identify the active project id.
2. Search durable memory before asking the user to repeat context.
3. Use context-mode for large files, logs, and command output.
4. Treat the repository as source of truth when memory conflicts with code.

After meaningful work:

1. Save reusable lessons, decisions, failed approaches, and workflows.
2. Prefer `debugging_lesson` for bugfix learnings.
3. Include symptoms, failed approaches, working solution, recognition signals, evidence, and next-time guidance.

Safety:

- Do not save secrets, tokens, passwords, private keys, raw `.env`, or sensitive logs.
- Project memory must be project-scoped.
- Global memory is only for stable cross-project preferences and universal rules.

Demo commands:

```bash
scripts/ygg.py bootstrap --project PROJECT --query "task summary"
scripts/ygg.py remember --project PROJECT --type debugging_lesson --json-file lesson.json
scripts/ygg.py search --project PROJECT --query "symptom terms"
scripts/ygg.py materialize --id MEMORY_ID --project PROJECT
```
