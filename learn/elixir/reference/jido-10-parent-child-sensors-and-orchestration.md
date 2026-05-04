# Jido 10: Parent-Child Hierarchies, Sensors, and Orchestration

## Goal

Coordinate multiple agents with signal routing and runtime-managed relationships.

## Parent-child concepts

Parent-child hierarchy is application-level coordination, not a replacement for OTP supervision. A parent can emit `SpawnAgent`, track children by tag, and receive child-exit signals. Children can emit signals back to the parent.

Typical shape:

```text
Orchestrator
  Coordinator
    Worker A
    Worker B
```

Use this when a job decomposes into isolated units of execution.

## Sensors

A sensor bridges external events into Jido signals. It can be a GenServer that polls or receives data, builds a `Jido.Signal`, and sends it to an agent with `AgentServer.cast/2`.

Sources include timers, webhooks, queues, file watchers, and external APIs.

## Exercises

1. Build a `CoordinatorAgent` that spawns two worker agents.
2. Workers emit `task.result` signals back to the coordinator.
3. Coordinator aggregates results and emits `job.result`.
4. Add a `QuoteSensor` or webhook-style injection.
5. Add context-aware routing for `:normal` versus `:maintenance` mode.

## Checkpoint questions

- What is the difference between OTP supervision and application-level orchestration?
- What should a child agent know about its parent?
- How should sensor failures be isolated?
