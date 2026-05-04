# Jido Course for an Experienced Elixir Developer

A practical course for learning Jido as a BEAM-native agent framework, not merely an LLM wrapper.

Sources reviewed: Jido home page, documentation landing page, Getting Started, Concepts, Learn tutorials, Guides, and Reference pages at <https://jido.run/> and <https://jido.run/docs>. The site version shown in the docs footer was Jido 2.1.0.

---

## 0. Course orientation

### What Jido is

Jido is an open-source Elixir framework for building production-grade agents on the BEAM. The core idea is very Elixir-native: agents are deterministic, schema-backed data structures; OTP processes are provided by the runtime layer; side effects are described as data and executed separately.

Jido’s ecosystem is split into packages:

- `jido`: core agents, actions, signals, directives, runtime.
- `jido_action`: standalone action framework.
- `jido_signal`: CloudEvents-based signal system.
- `jido_ai`: LLM-powered agents, tool use, reasoning strategies.
- `req_llm`: provider-agnostic LLM HTTP client.
- `llmdb`: model metadata database.
- Additional integrations include browser tooling, observability, messaging, and Ash integration.

### The most important mental model

Jido separates concerns that ordinary GenServers often combine:

| Ordinary OTP habit | Jido equivalent | Why it matters |
|---|---|---|
| GenServer state | `Jido.Agent` struct | State is plain data, schema-validated, serializable, testable. |
| `handle_call/3` logic | `Jido.Action` modules | Actions are pure, validated units of work. |
| Side effects inside callbacks | `Jido.Agent.Directive` structs | Effects are returned as data and executed later by runtime. |
| `send/2` and ad-hoc messages | `Jido.Signal` | Typed CloudEvents-style envelope with routing. |
| Process supervision | `Jido.AgentServer` and supervisors | Runtime wraps agents in OTP when you need lifecycle and concurrency. |

The core invariant: `cmd/2` returns `{updated_agent, directives}`. The returned agent is already complete. Directives do not mutate state; they describe outbound effects for the runtime.

### Prerequisites

You should already be comfortable with:

- Elixir 1.18+ and OTP 27+.
- Mix projects and supervision trees.
- GenServer and DynamicSupervisor mental models.
- Pattern matching, structs, behaviours, callbacks.
- Basic testing with ExUnit.

You do not need Phoenix for the core course, though Phoenix LiveView is a natural UI layer for agent systems.

---

## Course structure

The course has 12 modules. Each module has a goal, concepts, build task, checks, and extension exercises.

1. Setup and Jido’s OTP mapping.
2. Agents as immutable data.
3. Actions as validated state transitions.
4. Workflows with action chains.
5. Signals and routing.
6. Directives and runtime side effects.
7. AgentServer and supervised runtime.
8. Plugins and reusable capabilities.
9. FSMs, task planning, and resumable workflows.
10. Parent-child hierarchies, sensors, and orchestration.
11. AI agents, tools, chat, and reasoning strategies.
12. Memory, threads, RAG, persistence, testing, debugging, and production readiness.

Capstone: build a supervised research-and-execution agent system with tool use, memory, signal routing, and testable pure core logic.

---

# Module 1 — Setup and the Jido mental model

## Goal

Install Jido, verify the runtime, and understand how Jido maps to OTP patterns you already know.

## Install

For a normal Mix project:

```elixir
defp deps do
  [
    {:jido, "~> 2.1"},
    {:jido_ai, "~> 2.0"},
    {:req_llm, "~> 1.7"}
  ]
end
```

Then:

```bash
mix deps.get
mix compile
```

For non-AI modules, `:jido` alone is enough. Add `:jido_ai` and `:req_llm` when you start using LLM features.

Runtime secrets belong in `config/runtime.exs`:

```elixir
import Config

config :req_llm,
  openai_api_key: System.get_env("OPENAI_API_KEY")
```

## Smoke test

```elixir
defmodule SmokeAgent do
  use Jido.Agent,
    name: "smoke_agent",
    schema: Zoi.object(%{
      status: Zoi.string() |> Zoi.default("pending")
    })
end

defmodule MarkReady do
  use Jido.Action,
    name: "mark_ready",
    schema: Zoi.object(%{})

  @impl true
  def run(_params, _context), do: {:ok, %{status: "ready"}}
end

agent = SmokeAgent.new()
{updated, directives} = SmokeAgent.cmd(agent, {MarkReady, %{}})
updated.state.status
# => "ready"
directives
# => []
```

## Key lesson

Do not start with an LLM. Start with the core abstraction: an agent is data, an action is a validated transition, and directives are effects-as-data.

## Exercises

1. Create a new supervised Mix project called `jido_course_app`.
2. Add `:jido` only.
3. Reproduce the smoke test in `iex -S mix`.
4. Write one ExUnit test that proves the original agent remains unchanged after `cmd/2`.

---

# Module 2 — Agents as immutable data

## Goal

Understand `Jido.Agent` before touching `Jido.AgentServer`.

## Concepts

A Jido agent is an immutable struct with schema-backed state and a command interface. It is not a GenServer. It has no mailbox. You can create it, pass it to `cmd/2`, get back a new struct, and test the whole transition synchronously.

Use Jido agents when you need:

- Multi-step workflows where each step depends on accumulated state.
- State shape validation over time.
- A clear boundary between decision logic and effects.
- Optional runtime supervision later.

## Build: `CounterAgent`

```elixir
defmodule Course.CounterAgent do
  use Jido.Agent,
    name: "counter_agent",
    description: "Tracks a simple counter",
    schema: Zoi.object(%{
      count: Zoi.integer() |> Zoi.default(0),
      status: Zoi.atom() |> Zoi.default(:idle)
    })
end
```

## What you should inspect

```elixir
agent = Course.CounterAgent.new()
agent.state
Course.CounterAgent.validate(agent, %{})
```

## Checkpoint questions

- What fields are in the agent struct besides `state`?
- What does `new/1` accept?
- What happens if initial state violates the schema?
- Why is this easier to test than a GenServer callback?

---

# Module 3 — Actions as validated state transitions

## Goal

Define actions that validate params, read context, and return state updates.

## Concepts

An action is a module using `Jido.Action`. It declares compile-time metadata and input/output schemas. The required callback is `run/2`:

```elixir
@impl true
def run(params, context) do
  {:ok, result_map}
end
```

Valid return shapes:

```elixir
{:ok, result}
{:ok, result, directives}
{:error, reason}
```

Actions are designed to be pure. They should not send emails, call APIs, write files, or mutate process state directly. Return directives for that.

## Build: increment action

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

Run it:

```elixir
agent = Course.CounterAgent.new()
{agent2, directives} = Course.CounterAgent.cmd(agent, {Course.Increment, %{by: 3}})
agent.state.count
# => 0
agent2.state.count
# => 3
directives
# => []
```

## Validation path

```elixir
{error_agent, error_directives} =
  Course.CounterAgent.cmd(agent, {Course.Increment, %{by: "not an integer"}})
```

Expected behaviour: the state remains unchanged and the directive list contains an error directive.

## Exercises

1. Add `Course.Decrement`.
2. Add an output schema to `Course.Increment`.
3. Write tests for success and validation failure.
4. Refactor an existing GenServer callback from one of your own projects into an action-shaped function.

---

# Module 4 — Workflows with action chains

## Goal

Compose multiple actions into one command and let state accumulate between steps.

## Concepts

`cmd/2` accepts a single instruction or a list of instructions. Each action’s output is merged into agent state before the next action runs. Later actions read previous results from `context.state`.

Instruction formats include:

```elixir
MyAction
{MyAction, %{param: "value"}}
[MyAction, {OtherAction, %{x: 1}}]
Jido.Instruction.new!(%{action: MyAction, params: %{}, context: %{}, opts: []})
```

## Build: order workflow

Agent:

```elixir
defmodule Course.OrderAgent do
  use Jido.Agent,
    name: "order_agent",
    schema: Zoi.object(%{
      order_id: Zoi.string() |> Zoi.default(""),
      validated: Zoi.boolean() |> Zoi.default(false),
      discount: Zoi.float() |> Zoi.default(0.0),
      total: Zoi.float() |> Zoi.default(0.0),
      status: Zoi.atom() |> Zoi.default(:pending)
    })
end
```

Actions:

```elixir
defmodule Course.ValidateOrder do
  use Jido.Action,
    name: "validate_order",
    schema: Zoi.object(%{order_id: Zoi.string()})

  @impl true
  def run(params, _context) do
    {:ok, %{order_id: params.order_id, validated: true}}
  end
end

defmodule Course.ApplyDiscount do
  use Jido.Action,
    name: "apply_discount",
    schema: Zoi.object(%{})

  @impl true
  def run(_params, context) do
    discount = if context.state.validated, do: 0.10, else: 0.0
    {:ok, %{discount: discount}}
  end
end

defmodule Course.CalculateTotal do
  use Jido.Action,
    name: "calculate_total",
    schema: Zoi.object(%{})

  @impl true
  def run(_params, context) do
    base = 100.0
    {:ok, %{total: base * (1.0 - context.state.discount)}}
  end
end
```

Execute:

```elixir
agent = Course.OrderAgent.new()

{agent, directives} =
  Course.OrderAgent.cmd(agent, [
    {Course.ValidateOrder, %{order_id: "ord_99"}},
    Course.ApplyDiscount,
    Course.CalculateTotal
  ])
```

## Exercises

1. Add `Course.ConfirmOrder` that sets `status: :confirmed`.
2. Add a deliberate validation failure in the second action. Observe whether the third action runs.
3. Test each action in isolation and test the workflow end-to-end.

---

# Module 5 — Signals and routing

## Goal

Use signals as typed event envelopes and route them to actions.

## Concepts

Signals are Jido’s universal message format. They implement the CloudEvents model with fields such as:

- `specversion`
- `id`
- `source`
- `type`
- `subject`
- `time`
- `datacontenttype`
- `dataschema`
- `data`

Signal types use dot notation, for example:

```text
order.payment.processed.success
user.profile.updated
system.metrics.collected
```

Signals are created with:

```elixir
signal =
  Jido.Signal.new!(
    "order.confirmed",
    %{order_id: "ord_99"},
    source: "/orders"
  )
```

## Routing

A running `AgentServer` maps signal types to actions through routes. Routes may come from:

1. Strategy routes.
2. Agent routes.
3. Plugin routes.

Routes support exact and wildcard patterns such as:

```elixir
def signal_routes(_ctx) do
  [
    {"order.confirmed", Course.HandleOrderConfirmed},
    {"order.*.failed", Course.HandleOrderFailure},
    {"audit.**", Course.HandleAuditEvent}
  ]
end
```

## Exercise

Add signal routes to `Course.OrderAgent` and create a `Course.HandleOrderConfirmed` action. Start the agent under `AgentServer`, send a signal, and inspect updated state.

---

# Module 6 — Directives and side-effect boundaries

## Goal

Learn to return side-effect descriptions from actions without performing effects inline.

## Concepts

Directives are structs that describe effects. The runtime executes them after `cmd/2` completes.

Core directive types include:

- `Emit`: dispatch a signal.
- `Schedule`: send a delayed message/signal.
- `Cron` and `CronCancel`: recurring agent-local scheduled execution.
- `SpawnAgent`: start a child agent and track it by tag.
- `StopChild`: stop a tracked child.
- `Spawn`: start a generic BEAM child process.
- `RunInstruction`: execute another instruction later.
- `Stop`: terminate the agent process.
- `Error`: wrap a typed error.

## Build: emit confirmation signal

```elixir
defmodule Course.ConfirmOrder do
  use Jido.Action,
    name: "confirm_order",
    schema: Zoi.object(%{})

  alias Jido.Agent.Directive

  @impl true
  def run(_params, context) do
    signal =
      Jido.Signal.new!(
        "order.confirmed",
        %{order_id: context.state.order_id, total: context.state.total},
        source: "/orders"
      )

    {:ok, %{status: :confirmed}, %Directive.Emit{signal: signal}}
  end
end
```

## Exercises

1. Return a list of directives: emit a signal and schedule a timeout check.
2. Write tests that assert the directive struct, not the side effect.
3. Create a custom directive struct and sketch its `DirectiveExec` protocol implementation.

---

# Module 7 — AgentServer and supervised runtime

## Goal

Move from pure data execution to supervised runtime execution.

## Concepts

`AgentServer` is a GenServer that wraps an agent struct. It owns:

- Signal routing.
- Directive execution.
- Agent process lifecycle.
- Directive queue draining.
- Parent-child tracking.
- Registry lookup.

Start directly:

```elixir
{:ok, pid} = Jido.AgentServer.start(agent: Course.OrderAgent)
```

Or linked:

```elixir
{:ok, pid} =
  Jido.AgentServer.start_link(
    agent: Course.OrderAgent,
    id: "order-42",
    initial_state: %{total: 0.0}
  )
```

Signal flow:

1. Signal arrives by `call/3` or `cast/2`.
2. Router maps signal type to action/instruction.
3. AgentServer calls `Agent.cmd/2` in a supervised task.
4. Updated agent is stored in server state.
5. Returned directives are enqueued.
6. Directive queue drains in order.

## Runtime helpers

For scripts and Livebook:

```elixir
{:ok, _} = Jido.start()
runtime = Jido.default_instance()
{:ok, pid} = Jido.start_agent(runtime, Course.OrderAgent, id: "order-demo")
```

For Mix applications, define a runtime module:

```elixir
defmodule CourseApp.Jido do
  use Jido, otp_app: :course_app
end
```

Supervise it:

```elixir
children = [
  {CourseApp.Jido, name: CourseApp.Jido}
]
```

Start agents against it:

```elixir
{:ok, pid} = Jido.start_agent(CourseApp.Jido, Course.OrderAgent, id: "order-1")
```

## Exercises

1. Compare `cmd/2` direct execution with `AgentServer.call/2` execution.
2. Use `AgentServer.status/1` and `AgentServer.state/1` to inspect runtime state.
3. Send one synchronous signal and one asynchronous signal.

---

# Module 8 — Plugins and reusable capabilities

## Goal

Package actions, state, routes, and lifecycle hooks into reusable plugins.

## Concepts

Plugins solve duplication when multiple agents share the same capability. A plugin can provide:

- Actions.
- A state slice under `state_key`.
- Signal routes.
- Signal interception via `handle_signal/2`.
- Lifecycle hooks such as `mount/2`, `child_spec/1`, `transform_result/3`, checkpoint/restore hooks.
- Schedules.

Default plugins include:

- `Jido.Thread.Plugin` under `:__thread__`.
- `Jido.Identity.Plugin` under `:__identity__`.
- `Jido.Memory.Plugin` under `:__memory__`.

## Build: notes plugin

```elixir
defmodule Course.AddNote do
  use Jido.Action,
    name: "add_note",
    schema: Zoi.object(%{text: Zoi.string()})

  @impl true
  def run(params, context) do
    notes = get_in(context.state, [:notes, :entries]) || []
    note = %{text: params.text, added_at: DateTime.utc_now()}
    {:ok, %{notes: %{entries: [note | notes]}}}
  end
end

defmodule Course.ClearNotes do
  use Jido.Action,
    name: "clear_notes",
    schema: Zoi.object(%{})

  @impl true
  def run(_params, _context), do: {:ok, %{notes: %{entries: []}}}
end

defmodule Course.NotesPlugin do
  use Jido.Plugin,
    name: "notes_plugin",
    state_key: :notes,
    actions: [Course.AddNote, Course.ClearNotes],
    description: "Manages notes",
    schema: Zoi.object(%{
      entries: Zoi.list(Zoi.any()) |> Zoi.default([])
    }),
    signal_patterns: ["notes.*"]

  @impl Jido.Plugin
  def mount(_agent, config) do
    label = Map.get(config, :label, "default")
    {:ok, %{label: label}}
  end

  @impl Jido.Plugin
  def signal_routes(_config) do
    [
      {"notes.add", Course.AddNote},
      {"notes.clear", Course.ClearNotes}
    ]
  end
end
```

Use it:

```elixir
defmodule Course.NotesAgent do
  use Jido.Agent,
    name: "notes_agent",
    plugins: [Course.NotesPlugin]
end

defmodule Course.WorkNotesAgent do
  use Jido.Agent,
    name: "work_notes_agent",
    plugins: [{Course.NotesPlugin, %{label: "work"}}]
end
```

## Exercises

1. Add a `ListNotes` action.
2. Add a plugin config schema.
3. Add a signal route for `notes.list`.
4. Decide what plugin state should be kept, dropped, or externalized during checkpoint.

---

# Module 9 — FSMs, planning, and resumable workflows

## Goal

Model workflows where valid transitions matter, then extend the idea into task planning and resume behaviour.

## FSM concepts

Use a finite-state-machine strategy when the workflow has explicit states and guarded transitions. Good candidates:

- Approval workflows.
- Payment processing.
- Long-running jobs.
- Any process where “what can happen next” depends on current state.

In Jido’s FSM tutorial, the FSM strategy uses `RunInstruction` directives internally. Under normal runtime operation, `AgentServer` processes those directives.

## Planning concepts

Task planning turns a goal into a list of tasks, stores those tasks in memory, executes one task at a time, and resumes until completion. The tutorial’s deterministic version uses `Jido.Memory.Agent` as the task store; AI planning can later plug into the same architecture.

## Exercise: deterministic task planner

Build:

- `Course.TaskAgent`.
- Memory space `:tasks`.
- `PlanGoal` action that creates task maps.
- `ExecuteNextTask` action that marks the next task complete.
- `ResumeUntilComplete` helper that loops through tasks.

Task shape:

```elixir
%{
  id: "task-1",
  title: "Validate inputs",
  status: :pending | :done | :failed,
  result: nil | map()
}
```

## Extension

Replace deterministic planning with an LLM-backed action later, but keep the same task memory and execution loop.

---

# Module 10 — Parent-child hierarchies, sensors, and orchestration

## Goal

Coordinate multiple agents with signal routing and runtime-managed relationships.

## Parent-child concepts

Parent-child hierarchy is application-level coordination, not a replacement for OTP supervision. A parent can emit `SpawnAgent`, track children by tag, and receive child-exit signals. Children can emit signals back to parents.

Typical shape:

```text
Orchestrator
  └── Coordinator
        ├── Worker A
        └── Worker B
```

Use this when a job decomposes into isolated units of execution.

## Sensors

A sensor bridges external events into Jido signals. The docs present a sensor as a GenServer that polls or receives data, builds a `Jido.Signal`, and sends it to an agent with `AgentServer.cast/2`.

Sources might include:

- Timers.
- Webhooks.
- Message queues.
- File watchers.
- External APIs.

## Orchestration

The multi-agent orchestration tutorial coordinates specialized sub-agents with signals and skills. It introduces `Jido.AI.Skill.Spec` and a registry as metadata describing what specialists can do.

## Exercises

1. Build a `CoordinatorAgent` that spawns two worker agents.
2. Workers emit `task.result` signals back to the coordinator.
3. Coordinator aggregates results and emits `job.result`.
4. Add a `QuoteSensor` or webhook-style injection that sends signals to an agent.
5. Add context-aware routing so the same signal routes differently in `:normal` vs `:maintenance` mode.

---

# Module 11 — AI agents, tools, chat, and reasoning strategies

## Goal

Add LLM behaviour after you understand the core runtime.

## First LLM agent

```elixir
defmodule Course.Greeter do
  use Jido.AI.Agent,
    name: "greeter",
    description: "Generates a friendly greeting",
    tools: [],
    model: :fast,
    system_prompt: """
    You are a friendly greeter.
    Generate a short, warm welcome message.
    One or two sentences maximum.
    """
end
```

Start and ask:

```elixir
{:ok, _} = Jido.start()
runtime = Jido.default_instance()
{:ok, pid} = Jido.start_agent(runtime, Course.Greeter, id: "greeter-demo")
Course.Greeter.ask_sync(pid, "Say hello to someone learning Jido.", timeout: 30_000)
```

## Tool-calling with actions

Every `Jido.Action` can double as an LLM tool. Its Zoi schema becomes JSON Schema, and `jido_ai` can adapt actions into tool definitions. The important design detail: the LLM request does not execute tools inline. Tool execution is routed back through Jido’s runtime/directive path.

Build tool actions such as:

- `GetWeather`.
- `LookupCustomer`.
- `CreateTicket`.
- `SearchKnowledgeBase`.

Then attach them:

```elixir
defmodule Course.SupportAgent do
  use Jido.AI.Agent,
    name: "support_agent",
    description: "Support assistant with tools",
    tools: [Course.LookupCustomer, Course.CreateTicket],
    model: "openai:gpt-4o-mini",
    max_iterations: 5,
    system_prompt: """
    You help users resolve support issues. Use tools when facts are needed.
    """
end
```

## Chat agents

A chat agent keeps a multi-turn conversation on one agent process. The basic pattern is:

1. Start one agent process.
2. Send repeated turns to the same pid.
3. Inspect snapshots and thread state.
4. Optionally update system prompt at runtime.
5. Optionally stream partial text while a turn is running.

## Hybrid chat

Hybrid chat changes per-request LLM options rather than defining a separate agent for every mode. Use cheap, quick turns for simple summaries and deeper reasoning turns for complex diagnosis.

## Reasoning strategies

The docs compare:

- Chain-of-thought style reasoning.
- Tree-of-thoughts style exploration.
- Adaptive reasoning.

Course guidance: do not start here. First build deterministic tools and workflows. Then add reasoning strategies where the problem actually benefits from search, comparison, planning, or uncertainty handling.

## Exercises

1. Build a no-tool greeter.
2. Build a weather/tool-calling agent.
3. Build a two-turn chat agent.
4. Add a hybrid request mode for “quick” vs “deep” turns.
5. Inspect the runtime snapshot after each turn.

---

# Module 12 — Memory, threads, RAG, persistence, testing, debugging, and production readiness

## Memory layers

Jido provides three complementary memory layers:

1. Memory Plugin: structured data in named spaces.
2. Thread Plugin: append-only interaction log.
3. Retrieval Store: semantic-ish recall over text documents using token-overlap scoring in the tutorial implementation.

## Structured memory

```elixir
alias Jido.Memory.Agent, as: MemAgent

agent = Course.MemoryAgent.new()
agent = MemAgent.ensure(agent)
agent = MemAgent.ensure_space(agent, :prefs, %{})
agent = MemAgent.put_in_space(agent, :prefs, :theme, "dark")
MemAgent.get_in_space(agent, :prefs, :theme)
# => "dark"
```

List space:

```elixir
agent = MemAgent.ensure_space(agent, :notes, [])
agent = MemAgent.append_to_space(agent, :notes, %{id: "n1", text: "Check readings"})
```

## Thread log

```elixir
alias Jido.Thread.Agent, as: ThreadAgent

agent = ThreadAgent.ensure(agent, metadata: %{user_id: "u1"})

agent =
  ThreadAgent.append(agent, %{
    kind: :message,
    payload: %{role: "user", content: "What sensors are online?"}
  })
```

Use thread entries for messages, tool calls, system events, or domain-specific audit records.

## Retrieval-augmented agents

The tutorial retrieval store is ETS-backed and uses token-overlap/Jaccard-style scoring. For production-scale RAG, swap this for a real vector store or search backend.

Pattern:

1. Upsert documents into a namespace.
2. On `on_before_cmd/2`, recall documents for the prompt.
3. Inject retrieved context into the prompt.
4. Let the AI agent answer with grounding from context.

## Checkpoint and restore

Plugin checkpoint strategies:

- `:keep`: include state as-is.
- `:drop`: exclude transient state.
- `{:externalize, key, pointer}`: replace full state with pointer.

Memory defaults to keeping spaces. Thread plugin externalizes thread identity/revision rather than serializing the full log inline.

## Testing strategy

Test in layers:

1. Action unit tests: call `run/2` directly with params/context.
2. Agent transition tests: call `cmd/2` and assert updated state plus directives.
3. Signal routing tests: start `AgentServer`, send signals, inspect state.
4. Directive tests: assert directive structs from pure logic; use fake dispatch adapters when needed.
5. AI tests: avoid relying on live providers for core logic. Mock at the LLM boundary or test tool conversion separately.

## Debugging strategy

Use:

- `AgentServer.status/1` for snapshots.
- `AgentServer.state/1` for server state.
- Debug mode and event buffers where appropriate.
- Telemetry events and structured logging for production observability.
- Explicit inspection of directives and signals.

## Production checklist

Before production:

- All actions have schemas.
- Side effects are directives or isolated workers, not hidden inside actions.
- Agents have clear IDs.
- Signal type naming is consistent.
- Runtime supervision is explicit.
- Directive queue size is understood.
- Error directives are handled or logged.
- Long-running workflows expose completion through state.
- AI calls have timeouts, budgets, and model/provider configuration.
- Tool actions are deterministic and tested without LLMs.
- Memory/persistence policy is explicit.
- Observability is wired before launch.

---

# Capstone project — Supervised research-and-execution agent system

## Objective

Build a system that accepts a goal, plans work, delegates tasks to specialist agents, uses tools, stores memory, and returns an auditable result.

## Requirements

### Core

- `ResearchCoordinatorAgent` supervised under a Jido runtime.
- `PlannerAgent`, `ResearcherAgent`, and `WriterAgent` as children or specialist agents.
- Signals:
  - `goal.received`
  - `task.created`
  - `task.assigned`
  - `task.result`
  - `report.ready`
- Actions:
  - `PlanGoal`
  - `AssignTask`
  - `ExecuteTask`
  - `AggregateResults`
  - `WriteReport`
- Memory space `:tasks`.
- Thread log for interaction history.
- Directives for spawning children and emitting task/result signals.

### AI extension

- `PlannerAgent` may use an LLM to propose tasks.
- `ResearcherAgent` may use tool actions for retrieval or external API calls.
- `WriterAgent` may synthesize final output.

### Tests

- Unit test every action.
- Integration test the coordinator without live LLM calls.
- Test at least one signal route.
- Test at least one directive emitted by an action.
- Test checkpoint/restore for relevant plugin state.

### Stretch goals

- Add a sensor that injects goals from a queue or webhook.
- Add context-aware routing for maintenance mode.
- Add hybrid chat behaviour for quick vs deep turns.
- Add telemetry assertions or log capture in tests.

---

# Suggested study schedule

## Week 1 — Core primitives

- Day 1: Setup, smoke test, OTP mapping.
- Day 2: Agents and schemas.
- Day 3: Actions and validation.
- Day 4: Workflows and action chains.
- Day 5: Signals and directives.
- Day 6: AgentServer runtime.
- Day 7: Review and tests.

## Week 2 — Composition and runtime patterns

- Day 1: Plugins.
- Day 2: FSMs.
- Day 3: Task planning and memory.
- Day 4: Parent-child hierarchy.
- Day 5: Sensors.
- Day 6: Multi-agent orchestration.
- Day 7: Review and refactor.

## Week 3 — AI layer and production readiness

- Day 1: First LLM agent.
- Day 2: Tool-calling actions.
- Day 3: Chat and hybrid chat.
- Day 4: Reasoning strategies.
- Day 5: Memory, threads, RAG.
- Day 6: Persistence, testing, debugging.
- Day 7: Capstone integration.

---

# Reference map

Use this reading order alongside the course:

1. Home: <https://jido.run/>
2. Docs: <https://jido.run/docs>
3. Getting Started: <https://jido.run/docs/getting-started>
4. I know Elixir: <https://jido.run/docs/getting-started/elixir-developers>
5. Installation: <https://jido.run/docs/getting-started/installation>
6. First Agent: <https://jido.run/docs/getting-started/first-agent>
7. First LLM Agent: <https://jido.run/docs/getting-started/first-llm-agent>
8. Concepts: <https://jido.run/docs/concepts>
9. Actions: <https://jido.run/docs/concepts/actions>
10. Signals: <https://jido.run/docs/concepts/signals>
11. Agents: <https://jido.run/docs/concepts/agents>
12. Directives: <https://jido.run/docs/concepts/directives>
13. Agent Runtime: <https://jido.run/docs/concepts/agent-runtime>
14. Plugins: <https://jido.run/docs/concepts/plugins>
15. Learn: <https://jido.run/docs/learn>
16. First Workflow: <https://jido.run/docs/learn/first-workflow>
17. Plugins Tutorial: <https://jido.run/docs/learn/plugins-and-composable-agents>
18. FSM Tutorial: <https://jido.run/docs/learn/state-machines-with-fsm>
19. Parent-child Hierarchies: <https://jido.run/docs/learn/parent-child-agent-hierarchies>
20. Sensors: <https://jido.run/docs/learn/sensors-and-real-time-events>
21. AI Agent with Tools: <https://jido.run/docs/learn/ai-agent-with-tools>
22. Reasoning Strategies: <https://jido.run/docs/learn/reasoning-strategies-compared>
23. Task Planning: <https://jido.run/docs/learn/task-planning-and-execution>
24. Memory and RAG: <https://jido.run/docs/learn/memory-and-retrieval-augmented-agents>
25. Multi-agent Orchestration: <https://jido.run/docs/learn/multi-agent-orchestration>
26. AI Chat Agent: <https://jido.run/docs/learn/ai-chat-agent>
27. Hybrid Chat Agent: <https://jido.run/docs/learn/hybrid-chat-agent>
28. Guides: <https://jido.run/docs/guides>
29. Reference: <https://jido.run/docs/reference>

---

# Personal learning notes

Because you are already an Elixir developer, the fastest route is not “learn agents from scratch.” It is:

1. Treat `Jido.Agent` as a schema-backed state module.
2. Treat `Jido.Action` as a pure command handler with validation.
3. Treat `Jido.Signal` as a typed message envelope.
4. Treat `Jido.Agent.Directive` as effects-as-data.
5. Treat `Jido.AgentServer` as the OTP runtime that processes signals and directives.
6. Only then treat `Jido.AI.Agent` as a higher-level agent that adds LLM calls, tools, and reasoning strategies.

That ordering keeps the library understandable and prevents the AI layer from obscuring the underlying architecture.
