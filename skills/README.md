# Yggdrasil skills

[Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills)
that teach a Claude agent *how to use* Yggdrasil's memory. A skill is knowledge
(a `SKILL.md`), not a connection — it complements the MCP tools/CLI, it does not
replace them. Pair it with the engine (CLI / MCP / the
[Claude Desktop `.mcpb`](../packaging/mcpb/README.md)).

## `yggdrasil-memory`

The core workflow skill: recall durable memory **before** non-trivial work,
save reusable decisions/lessons **after**. Source: `yggdrasil-memory/SKILL.md`.

### Use it in Claude Desktop (upload)

1. **Settings → Capabilities/Skills → Add skill → Create skill → Upload a skill.**
2. Upload **`skills/yggdrasil-memory.zip`** (rebuild with the command below if
   you edited the skill).
3. Enable it. It pairs with the Yggdrasil MCP tools (install the
   [`.mcpb` extension](../packaging/mcpb/README.md) so the agent has tools to
   call).

### Use it in Claude Code

Drop the folder into a skills directory Claude Code reads (e.g.
`~/.claude/skills/yggdrasil-memory/`), or reference it from your project.

### Rebuild the upload zip

```bash
cd skills && zip -r -X yggdrasil-memory.zip yggdrasil-memory
```
