# Jido Foundations: Signals, Directives, and Supervised Runtime

## Goal

Move from pure data transitions to runtime execution: signals for typed events, directives for side effects, and `AgentServer` for supervised process-backed agents.

## Signals

Signals are Jido's universal message format and follow a CloudEvents-style shape with fields such as:

- `specversion`
- `id`
- `source`
- `type`
- `subject`
- `time`
- `datacontenttype`
- `dataschema`
- `data`

Signal types use dot notation:

```text
order.payment.processed.success
user.profile.updated
system.metrics.collected
```

Routes map signal types to actions:

```elixir
def signal_routes(_ctx) do
  [
    {"order.confirmed", Course.HandleOrderConfirmed},
    {"order.*.failed", Course.HandleOrderFailure},
    {"audit.**", Course.HandleAuditEvent}
  ]
end
```

## Directives

Directives are data structures that describe effects. The runtime executes them after `cmd/2` completes.

Core directive types include:

- `Emit`
- `Schedule`
- `Cron` and `CronCancel`
- `SpawnAgent`
- `StopChild`
- `Spawn`
- `RunInstruction`
- `Stop`
- `Error`

This keeps actions deterministic and testable. Tests can assert directive structs without depending on dispatch, timers, child processes, or external systems.

## AgentServer

`AgentServer` is a GenServer that wraps an agent struct. It owns:

- Signal routing.
- Directive execution.
- Agent lifecycle.
- Directive queue draining.
- Parent-child tracking.
- Registry lookup.

Signal flow:

1. Signal arrives by call or cast.
2. Router maps the signal type to an action or instruction.
3. `AgentServer` calls `Agent.cmd/2`.
4. Updated agent is stored in server state.
5. Returned directives are enqueued.
6. The directive queue drains in order.

## Exercises

1. Add signal routes to `Course.OrderAgent`.
2. Create `Course.HandleOrderConfirmed`.
3. Extend `ConfirmOrder` to emit an `order.confirmed` signal through a directive.
4. Write tests that assert directive structs.
5. Compare direct `cmd/2` execution with `AgentServer.call/2`.
6. Send one synchronous signal and one asynchronous signal.
7. Inspect runtime state with `AgentServer.status/1` and `AgentServer.state/1`.

## Checkpoint Questions

- Why use a typed signal envelope instead of raw process messages?
- Why should side effects be directives instead of hidden action code?
- What changes when an agent becomes process-backed?
- Why keep pure tests after adding runtime tests?
