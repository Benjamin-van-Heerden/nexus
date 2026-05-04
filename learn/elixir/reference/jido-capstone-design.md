# Jido Capstone: Design the Research-and-Execution System

## Goal

Design the supervised research-and-execution system before implementing it. The design should make ownership, state, signals, actions, memory, runtime supervision, and test boundaries explicit.

## Objective

Build a supervised system that accepts a goal, plans work, delegates tasks to specialist agents, uses tools, stores memory, and returns an auditable result.

## Core Agents

- `ResearchCoordinatorAgent`
- `PlannerAgent`
- `ResearcherAgent`
- `WriterAgent`

## Core Signals

- `goal.received`
- `task.created`
- `task.assigned`
- `task.result`
- `report.ready`

## Core Actions

- `PlanGoal`
- `AssignTask`
- `ExecuteTask`
- `AggregateResults`
- `WriteReport`

## Design Decisions To Make

Before building, decide:

1. Which agent owns the task list?
2. Which agent owns final report state?
3. Which signals are synchronous versus asynchronous?
4. Which directives are emitted by each action?
5. Which state is plugin-backed memory?
6. Which thread events are recorded?
7. Which tests prove the system without live LLM calls?
8. Where an AI extension can be inserted later without changing the deterministic core.

## Design Deliverables

Create a design document or module notes covering:

- Agent responsibilities.
- State schemas.
- Signal names and payload shapes.
- Action inputs and outputs.
- Directive flow.
- Memory spaces.
- Thread log events.
- Supervision/runtime shape.
- Test plan.

## Checkpoint Questions

- What is the smallest deterministic version of the system?
- Which agents own which state?
- How will the final report be audited?
- What can fail independently?
