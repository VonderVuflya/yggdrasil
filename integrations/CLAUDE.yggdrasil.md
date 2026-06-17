# Yggdrasil Memory Protocol

Use the project memory tools before asking the user to repeat prior decisions or debugging context.

Session start:

- Determine project id.
- Run memory bootstrap for non-trivial tasks.
- Keep retrieved memory compact and evidence-oriented.

During work:

- Search memory when you see familiar symptoms.
- Use context-mode for large outputs.
- If memory contradicts repository reality, repository wins.

Session close:

- Save reusable debugging lessons, decisions, failed approaches, workflows, and docs drift.
- Do not save secrets.
- Materialize important lessons to the Obsidian vault when useful.

Required debugging lesson shape:

```yaml
type: debugging_lesson
project: PROJECT
problem: ""
symptoms: []
failed_approaches: []
working_solution: []
recognition_signals: []
evidence: []
next_time: []
```
