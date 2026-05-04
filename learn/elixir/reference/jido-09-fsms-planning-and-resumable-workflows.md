# Jido 09: FSMs, Planning, and Resumable Workflows

## Goal

Model workflows with explicit valid transitions, then extend the idea into task planning and resume behaviour.

## FSM concepts

Finite-state-machine strategies are useful when the workflow has explicit states and guarded transitions. Good candidates include:

- Approval workflows.
- Payment processing.
- Long-running jobs.
- Any process where valid next steps depend on current state.

Jido's FSM tutorial uses `RunInstruction` directives internally. Under runtime operation, `AgentServer` processes those directives.

## Planning concepts

Task planning turns a goal into a list of tasks, stores those tasks in memory, executes one task at a time, and resumes until completion. A deterministic version should come before an AI-backed planner.

## Build target

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

## Exercises

1. Implement deterministic planning.
2. Execute pending tasks one at a time.
3. Resume until all tasks are complete.
4. Preserve enough state to explain what happened after interruption.

## Checkpoint questions

- What makes a workflow resumable?
- Which transitions should be illegal?
- Where should failed task details live?
