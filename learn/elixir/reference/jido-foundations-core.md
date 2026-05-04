# Jido Foundations: Core Mental Model and Agent Data

## Goal

Build a working mental model of Jido before introducing runtime complexity. By the end of this goal, you should understand what Jido is, how it maps to OTP habits, and why `Jido.Agent` starts as immutable data rather than a process.

## What Jido Is

Jido is an Elixir framework for building production-grade agent systems on the BEAM. The important point is that it is not merely an LLM wrapper. Its core abstractions are deterministic and testable:

- Agents are schema-backed data structures.
- Actions are validated state transitions.
- Signals are typed event envelopes.
- Directives describe effects as data.
- Runtime modules and `Jido.AgentServer` supply OTP lifecycle, concurrency, routing, and directive execution.

Jido's ecosystem includes:

- `jido` for core agents, actions, signals, directives, and runtime.
- `jido_action` for standalone actions.
- `jido_signal` for CloudEvents-style signals.
- `jido_ai` for LLM agents and tool use.
- `req_llm` for provider-agnostic LLM calls.
- `llmdb` for model metadata.

## OTP Mapping

| Ordinary OTP habit | Jido equivalent | Why it matters |
|---|---|---|
| GenServer state | `Jido.Agent` struct | State is plain data, schema-validated, serializable, and testable. |
| `handle_call/3` logic | `Jido.Action` modules | Transitions become named, validated, reusable units. |
| Side effects inside callbacks | `Jido.Agent.Directive` structs | Effects are returned as data and executed by the runtime. |
| `send/2` and ad-hoc messages | `Jido.Signal` | Messages use a typed event envelope. |
| Process lifecycle | `Jido.AgentServer` | Runtime concerns stay separate from core transition logic. |

The core invariant is:

```elixir
cmd(agent, instruction) :: {updated_agent, directives}
```

The returned agent is the complete new state. Directives do not mutate state; they describe outbound effects for the runtime.

## Setup

For the non-AI parts of the course, start with `:jido` only:

```elixir
defp deps do
  [
    {:jido, "~> 2.1"}
  ]
end
```

Add `:jido_ai` and `:req_llm` later, when you reach AI agents and tool-calling:

```elixir
{:jido_ai, "~> 2.0"},
{:req_llm, "~> 1.7"}
```

Runtime secrets belong in `config/runtime.exs`, not in application code.

## Agents as Immutable Data

A Jido agent is not a GenServer. It has no mailbox and no process lifecycle by itself. It is an immutable struct with schema-backed state and a command interface.

Start with a small counter:

```elixir
defmodule Course.CounterAgent do
  use Jido.Agent,
    name: "counter_agent",
    description: "Tracks a simple counter",
    schema: Zoi.object(%{
      count: Zoi.integer() |> Zoi.default(0),
      status: Zoi.atom() |> Zoi.default(:idle)
    })
end
```

Inspect:

```elixir
agent = Course.CounterAgent.new()
agent.state
Course.CounterAgent.validate(agent, %{})
```

## Exercises

1. Create a supervised Mix project called `jido_course_app`.
2. Add `:jido` and compile.
3. Build a `SmokeAgent` with a `status` field and a `MarkReady` action that moves it from `"pending"` to `"ready"`.
4. Build `Course.CounterAgent`.
5. Write tests for default state, valid initial state, invalid initial state, and immutability after `cmd/2`.

## Checkpoint Questions

- Why should this course start without an LLM?
- What does Jido move out of a GenServer callback?
- What fields are present on an agent struct besides `state`?
- Why is this easier to test than a GenServer callback?
