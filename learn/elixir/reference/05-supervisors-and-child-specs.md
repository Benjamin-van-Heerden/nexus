# Supervisors, Child Specs, and Restart Strategies

## Supervisors

A Supervisor is a process whose only job is to watch other processes and restart them when they fail. This is the "let it crash" philosophy in action — you don't try to handle every error, you let processes fail and restart them in a known-good state.

```elixir
defmodule MyApp.Supervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  def init(_init_arg) do
    children = [
      {MyWorker, arg1},
      {MyOtherWorker, arg2}
    ]
    Supervisor.init(children, strategy: :one_for_one)
  end
end
```

## Child Specs

A child spec tells the supervisor how to start, stop, and restart a child process:

```elixir
%{
  id: MyWorker,
  start: {MyWorker, :start_link, [arg]},
  restart: :permanent,    # :permanent | :temporary | :transient
  shutdown: 5000,         # ms to wait for graceful shutdown
  type: :worker           # :worker | :supervisor
}
```

Most modules define `child_spec/1` automatically when you `use GenServer` — the tuple `{MyWorker, arg}` is shorthand.

### Restart values
- `:permanent` — always restart (default)
- `:temporary` — never restart
- `:transient` — restart only on abnormal exit (not `:normal` or `:shutdown`)

## Restart Strategies

The supervisor's strategy determines what happens when a child crashes:

- **`:one_for_one`** — only restart the failed child. Use when children are independent.
- **`:one_for_all`** — restart ALL children. Use when children are co-dependent.
- **`:rest_for_one`** — restart the failed child and all children started AFTER it. Use when children form a dependency chain.

## Max Restarts

Supervisors have a circuit breaker: `max_restarts` (default 3) in `max_seconds` (default 5). If a child crashes more than this, the supervisor itself shuts down — escalating the failure up the tree.

## What to Practice

- Build a supervisor with multiple children
- Crash a child and observe automatic restart
- Experiment with different restart strategies
- Configure child specs with different restart values
- Trigger max_restarts and observe supervisor shutdown
