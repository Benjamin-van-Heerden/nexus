# Jido 01: Setup and Mental Model

## Goal

Install Jido, run a smoke test, and understand how Jido maps onto OTP concepts you already know.

## Core model

Jido separates concerns that a plain GenServer often bundles together:

| OTP habit | Jido equivalent |
|---|---|
| GenServer state | `Jido.Agent` struct |
| Callback logic | `Jido.Action` modules |
| Side effects in callbacks | `Jido.Agent.Directive` structs |
| Ad-hoc messages | `Jido.Signal` envelopes |
| Supervision/runtime | `Jido.AgentServer` and supervisors |

The important invariant is that `cmd/2` returns `{updated_agent, directives}`. The returned agent is the complete new state. Directives do not mutate state directly; they describe effects for the runtime to execute later.

## Install

For non-AI modules, start with `:jido` only:

```elixir
defp deps do
  [
    {:jido, "~> 2.1"}
  ]
end
```

Add `:jido_ai` and `:req_llm` only when the course reaches AI agents:

```elixir
{:jido_ai, "~> 2.0"},
{:req_llm, "~> 1.7"}
```

Runtime secrets belong in `config/runtime.exs`, not application code.

## Smoke test target

Build a tiny agent and action:

- `SmokeAgent` has a schema-backed `status` field defaulting to `"pending"`.
- `MarkReady` returns `%{status: "ready"}`.
- Calling `SmokeAgent.cmd(agent, {MarkReady, %{}})` returns a new agent whose status is `"ready"` and no directives.

## Exercises

1. Create a supervised Mix project called `jido_course_app`.
2. Add `:jido` and compile.
3. Reproduce the smoke test in `iex -S mix`.
4. Write one ExUnit test proving the original agent remains unchanged after `cmd/2`.

## Checkpoint questions

- Why should the first module avoid LLMs?
- What does Jido move out of a GenServer callback?
- What is the difference between updated state and directives?
