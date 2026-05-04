# Jido 07: AgentServer and Supervised Runtime

## Goal

Move from pure data execution to supervised runtime execution.

## Concepts

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

## Runtime shapes

For scripts and Livebook, use `Jido.start()` and `Jido.default_instance()`.

For Mix applications, define a runtime module:

```elixir
defmodule CourseApp.Jido do
  use Jido, otp_app: :course_app
end
```

Then supervise it and start agents against that runtime.

## Exercises

1. Compare direct `cmd/2` execution with `AgentServer.call/2`.
2. Use `AgentServer.status/1` and `AgentServer.state/1`.
3. Send one synchronous signal and one asynchronous signal.
4. Test the runtime path without relying on external services.

## Checkpoint questions

- What changes when an agent becomes process-backed?
- What state lives in the agent versus the server?
- Why keep pure tests even after adding runtime tests?
