# Supervisors and OTP Abstractions

## Reading Assignment: Understanding OTP Supervision Trees

### Core Concepts

**Supervisors** are processes that monitor other processes and restart them when they crash. They implement the "let it crash" philosophy — instead of defensive coding, you accept failures and restart clean.

### Why Supervision Matters

In OTP, you don't just start processes and hope. You build a **supervision tree**:
```
Application
└── Supervisor (main)
    ├── Worker (GenServer A)
    ├── Worker (GenServer B)
    └── Supervisor (sub)
        ├── Worker (GenServer C)
        └── Worker (GenServer D)
```

### Restart Strategies

| Strategy | Behavior |
|----------|----------|
| `:one_for_one` | If a child crashes, only that child is restarted (default) |
| `:one_for_all` | If one child crashes, ALL children are restarted |
| `:rest_for_one` | If child N crashes, children N+1 and onwards are restarted |

### Child Specifications

When starting a supervisor, you define child specs:

```elixir
children = [
  {MyWorker, arg},           # Shorthand: module, initial arg
  %{                          # Full child spec
    id: MyWorker,
    start: {MyWorker, :start_link, [arg]},
    restart: :permanent,      # :permanent | :temporary | :transient
    type: :worker             # :worker | :supervisor
  }
]

Supervisor.start_link(children, strategy: :one_for_one)
```

### Restart Values

- `:permanent` — Always restart (default for workers)
- `:temporary` — Never restart (use for optional workers)
- `:transient` — Restart only if abnormal exit (use for tasks that should complete)

### When to Nest Supervisors

- **Flat:** Simple applications with independent workers
- **Nested:** When you have groups of related processes that should restart together
- **Dynamic:** Use `DynamicSupervisor` when children are created at runtime

### Key Takeaways

1. Supervisors are your safety net — they make your application self-healing
2. Choose restart strategy based on process relationships
3. Use `:permanent` for essential services, `:transient` for tasks
4. DynamicSupervisors are for runtime-created processes (e.g., connection handlers)

---

**Completion:** Read through this material and note any questions or concepts you'd like to explore further.