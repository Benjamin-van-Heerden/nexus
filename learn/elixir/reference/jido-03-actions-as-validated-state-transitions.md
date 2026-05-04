# Jido 03: Actions as Validated State Transitions

## Goal

Define actions that validate params, read context, and return state updates.

## Concepts

An action uses `Jido.Action`. It declares metadata and schemas, then implements `run/2`.

Valid return shapes:

```elixir
{:ok, result}
{:ok, result, directives}
{:error, reason}
```

Actions should be pure. They should not send emails, call APIs, write files, or mutate process state inline. Return directives for effects.

## Build target

Add `Course.Increment`:

- Schema has `by` as an integer defaulting to `1`.
- Reads current count from `context.state`.
- Returns `%{count: current + params.by, status: :active}`.

Run it through `Course.CounterAgent.cmd/2` and verify:

- Original agent count remains `0`.
- Updated agent count changes.
- Directives are empty for this pure action.

## Exercises

1. Add `Course.Decrement`.
2. Add an output schema to `Course.Increment`.
3. Write tests for success and validation failure.
4. Refactor one GenServer callback-shaped operation into an action-shaped function.

## Checkpoint questions

- Where should validation happen?
- What should happen when params fail validation?
- Why should actions avoid hidden effects?
