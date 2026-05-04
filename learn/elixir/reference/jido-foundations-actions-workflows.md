# Jido Foundations: Actions and Deterministic Workflows

## Goal

Learn to model work as validated actions and compose those actions into deterministic workflows.

## Actions

An action uses `Jido.Action`. It declares metadata and schemas, then implements `run/2`.

Valid return shapes:

```elixir
{:ok, result}
{:ok, result, directives}
{:error, reason}
```

Actions should be pure. They should not send emails, call APIs, write files, or mutate process state inline. Return directives for effects instead.

## Build: Counter Actions

Add `Course.Increment`:

```elixir
defmodule Course.Increment do
  use Jido.Action,
    name: "increment",
    description: "Increment the counter",
    schema: Zoi.object(%{
      by: Zoi.integer() |> Zoi.default(1)
    })

  @impl true
  def run(params, context) do
    current = Map.get(context.state, :count, 0)
    {:ok, %{count: current + params.by, status: :active}}
  end
end
```

Run it through `Course.CounterAgent.cmd/2` and verify:

- The original agent remains unchanged.
- The updated agent has the new count.
- Invalid params leave state unchanged and produce the expected error path.

## Workflows

`cmd/2` accepts one instruction or a list of instructions. Each action output is merged into agent state before the next action runs, so later actions can read previous results from `context.state`.

Instruction forms include:

```elixir
MyAction
{MyAction, %{param: "value"}}
[MyAction, {OtherAction, %{x: 1}}]
Jido.Instruction.new!(%{action: MyAction, params: %{}, context: %{}, opts: []})
```

## Build: Order Workflow

Create `Course.OrderAgent` with state for:

- `order_id`
- `validated`
- `discount`
- `total`
- `status`

Create actions:

- `ValidateOrder`
- `ApplyDiscount`
- `CalculateTotal`
- `ConfirmOrder`

Run a chain where validation enables a discount and total calculation.

## Exercises

1. Add `Course.Decrement`.
2. Add an output schema to `Course.Increment`.
3. Test success and validation failure.
4. Build the order workflow.
5. Add a deliberate validation failure in the second action and observe whether later actions run.
6. Test each action in isolation and the workflow end-to-end.

## Checkpoint Questions

- Where should validation happen?
- How do chained actions communicate?
- What should a workflow test assert beyond the final value?
- Which parts of a workflow should remain deterministic?
