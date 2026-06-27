## Memory (Yggdrasil)

You have a durable, cross-session memory through the Yggdrasil MCP tools
(`ygg_recall`, `ygg_remember`, `ygg_search`). Past experiments — across nights,
machines, and forks — are recorded there. Use it so progress **compounds**
instead of starting cold each session, and so you never re-run a known-bad idea.

**Project key:** use `autoresearch-nanochat` as the `project` for every memory.

### Before proposing the next experiment
1. `ygg_recall` with a query describing the change you're considering — e.g.
   `"muon learning-rate schedule val_bpb"`, `"DEPTH vs width tradeoff"`,
   `"WINDOW_PATTERN SSSL vs L"`.
2. `ygg_recall "best val_bpb so far and what produced it"` to anchor on the
   current frontier.
3. Skip what memory shows already hurt; build on what helped.

### After each experiment (a `train.py` run finishes)
Call `ygg_remember` with `project=autoresearch-nanochat`,
`type=experiment_result`, and content in this exact shape:

```
hypothesis: <what you changed and why>
change:     <concrete knobs/diff: DEPTH 8->10, lr 0.02->0.03, WINDOW_PATTERN SSSL->L, ...>
result:     val_bpb <before> -> <after>  (Δ <delta>), 5-min budget
decision:   KEEP | REVERT
lesson:     <generalizable takeaway, e.g. "deeper helps until DEPTH>10, where the 5-min budget can't converge">
```

### Every ~10 experiments
`ygg_recall "what directions are working / not working for val_bpb"`, then write
a short `type=research_lesson` memory summarizing the trend, so the next session
starts informed.

> This block does not change the training task — it only gives you a memory so
> progress compounds. Delete it to run vanilla autoresearch.
