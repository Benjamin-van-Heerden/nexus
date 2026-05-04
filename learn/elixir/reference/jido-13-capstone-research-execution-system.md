# Jido 13: Capstone Research-and-Execution System

## Objective

Build a supervised system that accepts a goal, plans work, delegates tasks to specialist agents, uses tools, stores memory, and returns an auditable result.

## Core requirements

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

## AI extension

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

## Stretch goals

- Add a sensor that injects goals from a queue or webhook.
- Add context-aware routing for maintenance mode.
- Add hybrid chat behaviour for quick vs deep turns.
- Add telemetry assertions or log capture in tests.

## Checkpoint questions

- What is the smallest deterministic version of the system?
- Which agents own which state?
- How will the final report be audited?
