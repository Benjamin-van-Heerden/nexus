# Jido 05: Signals and Routing

## Goal

Use signals as typed event envelopes and route them to actions.

## Concepts

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

## Routing

A running `AgentServer` maps signal types to actions through routes. Routes may come from strategy routes, agent routes, or plugin routes. Routes support exact and wildcard patterns:

```elixir
def signal_routes(_ctx) do
  [
    {"order.confirmed", Course.HandleOrderConfirmed},
    {"order.*.failed", Course.HandleOrderFailure},
    {"audit.**", Course.HandleAuditEvent}
  ]
end
```

## Exercises

1. Add signal routes to `Course.OrderAgent`.
2. Create `Course.HandleOrderConfirmed`.
3. Start the agent under `AgentServer`.
4. Send a signal and inspect updated state.

## Checkpoint questions

- Why use a typed signal envelope instead of raw process messages?
- What should go in the signal type versus signal data?
- When is a wildcard route appropriate?
