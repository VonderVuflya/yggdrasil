# Yggdrasil Backend Boundary

Yggdrasil is a workflow/governance layer. The durable memory engine sits behind
a small, explicit, testable contract.

- **Default engine:** Yggdrasil's own `yggdrasil/ygg_memory_server.py` (stdlib
  SQLite + FTS5, zero heavy dependencies). Shipped, no external service.
- **Optional engine:** an external Muninn instance (Apache-2.0, third party).
  Reached through the same REST client; selected via `YGG_MUNINN_URL`.

The point of the boundary is that nothing in the workflow layer is
engine-specific: the same gates pass against either engine.

## Contract

The engine must support (`MemoryBackend` protocol in `yggdrasil/ygg_core.py`):

- `health`
- `add`
- `search`
- `get_all`
- `update_memory`
- `archive_memory`

`archive_memory` is non-destructive. It must preserve the memory record and set both:

- top-level `archived=true`, when the backend supports it;
- `metadata.status=archived`.

Archive metadata must also include:

- `archived_by`
- `archived_at`
- `archive_reason`
- `canonical_memory_id`
- `review_action_id`

## Adapter

The engine-agnostic REST client and the `MemoryBackend` protocol live in:

```text
yggdrasil/ygg_core.py        # MemoryBackend protocol + RestMemoryBackend (alias: MuninnBackend)
yggdrasil/ygg_memory_server.py  # the default engine implementing the contract
```

Review queue, review actions, and the gates use the client instead of building
raw REST requests directly. The default engine satisfies the full contract,
including `metadata_patch` / `archived` on `PUT /update`.

## Capability Failure

If a configured engine does not accept `metadata_patch` or `archived` through
`PUT /update`, Yggdrasil must fail at the adapter boundary with
`BackendCapabilityError`.

Do not silently fall back to delete, direct SQLite mutation, or partial archive
state.

## Optional Muninn backend

Muninn (`github.com/wjohns989/Muninn`, Apache-2.0) is NOT bundled. To use it as
the engine, point `YGG_MUNINN_URL` at a running instance. Stock Muninn does not
expose the metadata-update contract; it needs a small REST shim so
`UpdateMemoryRequest` accepts optional `metadata_patch` / `archived` and
`server.py` forwards them to `memory.update` (metadata-only update without
re-embedding). Without it, archive/merge/verify actions raise
`BackendCapabilityError` — by design, not a silent fallback. Preserve Muninn's
`NOTICE`/attribution when redistributing.

