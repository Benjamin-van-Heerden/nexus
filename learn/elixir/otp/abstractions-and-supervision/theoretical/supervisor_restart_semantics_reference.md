# Supervisor Restart Semantics — Reference

Companion reference for:

`/home/benjamin/Documents/nexus/learn/elixir/otp/abstractions-and-supervision/practical/lib/supervisor_strategy_lab.ex`

This session is about predicting what a supervisor will do before you run the code. The practical is intentionally small: model the semantics, then encode child specs clearly.

---

## 1. A supervisor has two separate decisions

When a child exits, OTP answers two questions:

1. **Should this child be restarted?**
   - controlled by the child spec's `:restart` value
2. **Which other children are affected?**
   - controlled by the supervisor's restart `:strategy`

Do not blend these together. The child spec decides whether the failed child is eligible for restart. The supervisor strategy decides the blast radius.

---

## 2. Child `:restart` values

A child spec can include:

```elixir
%{
  id: :cache,
  start: {KVStore, :start_link, [[name: :cache]]},
  restart: :permanent,
  shutdown: 5000,
  type: :worker
}
```

The important field today is `:restart`.

### `:permanent`

Always restart the child when it exits.

Use when the process is expected to exist for the lifetime of the supervisor.

Examples:

- long-running cache
- GenServer holding application state
- worker that should always be available

### `:temporary`

Never restart the child.

Use when the process is allowed to finish or fail without recovery by this supervisor.

Examples:

- fire-and-forget job
- short-lived task
- optional process where retry is handled elsewhere

### `:transient`

Restart only on abnormal exits.

Common non-restart reasons:

```elixir
:normal
:shutdown
{:shutdown, term}
```

Use when normal completion is acceptable, but crashes should be recovered.

Examples:

- worker that may complete successfully
- process that exits `:normal` after finishing its lifecycle
- job runner where success should not relaunch the same job

Mental model:

- `:permanent` → "you should always be here"
- `:temporary` → "you are never my responsibility to restart"
- `:transient` → "I will restart you if you crash, not if you finish"

---

## 3. Supervisor restart strategies

Assume children are started in this order:

```elixir
[:database, :cache, :web]
```

### `:one_for_one`

Only the failed child is restarted.

If `:cache` crashes:

```elixir
[:cache]
```

Use when children are independent.

### `:one_for_all`

All children are terminated and restarted.

If `:cache` crashes:

```elixir
[:database, :cache, :web]
```

Use when children depend on shared state or must be reset together.

### `:rest_for_one`

The failed child and every child started after it are restarted.

If `:cache` crashes:

```elixir
[:cache, :web]
```

If `:database` crashes:

```elixir
[:database, :cache, :web]
```

If `:web` crashes:

```elixir
[:web]
```

Use when children form a dependency chain: later children depend on earlier children.

---

## 4. Child order matters

For `:rest_for_one`, order is design.

Put foundational dependencies first:

```elixir
children = [
  Database,
  Cache,
  WebEndpoint
]
```

If `Database` crashes, everything after it may have stale connections or invalid state, so they restart too.

If `WebEndpoint` crashes, the database and cache do not need to restart.

---

## 5. Max restarts are escalation

Supervisors are not infinite retry machines. They have a restart intensity limit:

```elixir
Supervisor.init(children,
  strategy: :one_for_one,
  max_restarts: 3,
  max_seconds: 5
)
```

If children crash too many times inside the configured time window, the supervisor gives up and exits. That failure can then be escalated to its own supervisor.

Mental model:

> "Restart locally if this looks recoverable. Escalate if the local strategy is not working."

---

## 6. What to focus on in the practical

The practical asks you to encode the rules above as pure functions and child specs.

You should be able to answer:

- Does `:transient` restart after `:normal`? No.
- Does `:transient` restart after `:boom`? Yes.
- In `:rest_for_one`, what restarts when the middle child fails? The middle child and everything after it.
- Why is `:one_for_all` more disruptive? It intentionally restarts the whole sibling group.

If you can predict these without running IEx, you have the useful part of the model.
