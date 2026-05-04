# Jido Capstone: Build and Harden the Research-and-Execution System

## Goal

Implement the capstone system, then harden it with tests, persistence decisions, runtime inspection, and optional AI extensions.

## Core Requirements

Agents:

- `ResearchCoordinatorAgent`
- `PlannerAgent`
- `ResearcherAgent`
- `WriterAgent`

Signals:

- `goal.received`
- `task.created`
- `task.assigned`
- `task.result`
- `report.ready`

Actions:

- `PlanGoal`
- `AssignTask`
- `ExecuteTask`
- `AggregateResults`
- `WriteReport`

State and runtime:

- Memory space `:tasks`.
- Thread log for interaction history.
- Directives for spawning children and emitting task/result signals.
- Supervised runtime with deterministic integration tests.

## AI Extension

Only add this after the deterministic version works:

- `PlannerAgent` may use an LLM to propose tasks.
- `ResearcherAgent` may use tool actions for retrieval or external API calls.
- `WriterAgent` may synthesize the final report.

The deterministic core must work without live LLM calls.

## Tests

- Unit test every action.
- Integration test the coordinator without live LLM calls.
- Test at least one signal route.
- Test at least one emitted directive.
- Test checkpoint/restore for relevant plugin state.

## Hardening

Before considering the capstone complete:

- Inspect runtime state during a multi-step run.
- Confirm failed tasks are visible in state.
- Confirm duplicate or out-of-order signals are handled intentionally.
- Confirm thread log entries explain what happened.
- Confirm persistence/checkpoint strategy is explicit.
- Confirm AI calls, if present, have timeouts and budget boundaries.

## Stretch Goals

- Add a sensor that injects goals from a queue or webhook.
- Add context-aware routing for maintenance mode.
- Add hybrid chat behaviour for quick vs deep turns.
- Add telemetry assertions or log capture in tests.

## Checkpoint Questions

- Does the system still work without live LLM calls?
- Can you explain every emitted directive?
- Can the final report be audited from memory and thread state?
- What would you monitor in production?
