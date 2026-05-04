# Jido 02: Agents as Immutable Data

## Goal

Understand `Jido.Agent` as a schema-backed data module before using `Jido.AgentServer`.

## Concepts

A Jido agent is not a process. It has no mailbox and no lifecycle by itself. It is an immutable struct with validated state and a command interface. You can create it, pass it to `cmd/2`, get a new struct back, and test transitions synchronously.

Use this when you need:

- Accumulated state across a multi-step workflow.
- Validation over state shape.
- A clear boundary between decision logic and effects.
- Optional runtime supervision later.

## Build target

Create `Course.CounterAgent` with:

- `name: "counter_agent"`
- `description: "Tracks a simple counter"`
- State schema with `count` defaulting to `0`
- State schema with `status` defaulting to `:idle`

Inspect:

```elixir
agent = Course.CounterAgent.new()
agent.state
Course.CounterAgent.validate(agent, %{})
```

## Exercises

1. Create the counter agent.
2. Test its default state.
3. Test valid and invalid initial state.
4. Inspect the fields on the agent struct besides `state`.

## Checkpoint questions

- What does `new/1` accept?
- What happens when initial state violates the schema?
- Why is this easier to test than a GenServer callback?
