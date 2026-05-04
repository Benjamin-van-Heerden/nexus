# Jido 04: Workflows with Action Chains

## Goal

Compose multiple actions into one command and let state accumulate between steps.

## Concepts

`cmd/2` accepts one instruction or a list of instructions. Each action output is merged into agent state before the next action runs, so later actions can read previous results from `context.state`.

Instruction forms include:

```elixir
MyAction
{MyAction, %{param: "value"}}
[MyAction, {OtherAction, %{x: 1}}]
Jido.Instruction.new!(%{action: MyAction, params: %{}, context: %{}, opts: []})
```

## Build target

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

1. Add `Course.ConfirmOrder` that sets `status: :confirmed`.
2. Add a deliberate validation failure in the second action and observe whether later actions run.
3. Test each action in isolation.
4. Test the workflow end-to-end.

## Checkpoint questions

- Which state does each action own?
- How do chained actions communicate?
- What should a workflow test assert beyond the final value?
