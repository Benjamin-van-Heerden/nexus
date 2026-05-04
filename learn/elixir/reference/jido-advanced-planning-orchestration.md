# Jido Advanced: Planning, FSMs, and Orchestration

## Goal

Build systems where valid transitions, resumability, parent-child relationships, and external event injection matter.

## FSMs

Finite-state-machine strategies are useful when the workflow has explicit states and guarded transitions. Good candidates include:

- Approval workflows.
- Payment processing.
- Long-running jobs.
- Any process where valid next steps depend on current state.

Jido's FSM tutorial uses `RunInstruction` directives internally. Under runtime operation, `AgentServer` processes those directives.

## Deterministic Planning

Task planning turns a goal into a list of tasks, stores those tasks in memory, executes one task at a time, and resumes until completion. A deterministic version should come before an AI-backed planner.

Build:

- `Course.TaskAgent`
- Memory space `:tasks`
- `PlanGoal`
- `ExecuteNextTask`
- `ResumeUntilComplete`

Task shape:

```elixir
%{
  id: "task-1",
  title: "Validate inputs",
  status: :pending,
  result: nil
}
```

## Parent-Child Orchestration

Parent-child hierarchy is application-level coordination, not a replacement for OTP supervision. A parent can emit `SpawnAgent`, track children by tag, and receive child-exit signals. Children can emit signals back to the parent.

Typical shape:

```text
Orchestrator
  Coordinator
    Worker A
    Worker B
```

## Sensors

A sensor bridges external events into Jido signals. It can be a GenServer that polls or receives data, builds a `Jido.Signal`, and sends it to an agent with `AgentServer.cast/2`.

Sources include timers, webhooks, queues, file watchers, and external APIs.

## Exercises

1. Implement deterministic planning.
2. Execute pending tasks one at a time and resume until all tasks are complete.
3. Build a `CoordinatorAgent` that spawns two worker agents.
4. Have workers emit `task.result` signals back to the coordinator.
5. Aggregate worker results into `job.result`.
6. Add a `QuoteSensor` or webhook-style injection.
7. Add context-aware routing for `:normal` versus `:maintenance` mode.

## Checkpoint Questions

- What makes a workflow resumable?
- Which transitions should be illegal?
- What is the difference between OTP supervision and application-level orchestration?
- How should sensor failures be isolated?
