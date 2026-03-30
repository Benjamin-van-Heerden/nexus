# Tasks and Agents

## Tasks

Tasks are for one-off asynchronous work — computation you want to run concurrently and (optionally) collect the result.

### async/await pattern

```elixir
task = Task.async(fn -> expensive_computation() end)
# ... do other work ...
result = Task.await(task)  # blocks until done, default 5s timeout
```

### Fire-and-forget

```elixir
Task.start(fn -> send_email(user) end)
```

### Supervised tasks

```elixir
# In your supervision tree:
{Task.Supervisor, name: MyApp.TaskSupervisor}

# Start supervised tasks:
Task.Supervisor.async_nolink(MyApp.TaskSupervisor, fn -> work() end)
```

`async_nolink` — the task failure won't crash the caller. Essential for tasks triggered by user requests.

### Task patterns
- `Task.async_stream/3` — concurrent map over a collection with controlled concurrency
- `Task.yield/2` — non-blocking check if a task is done
- `Task.shutdown/2` — cancel a running task

## Agents

Agents are the simplest stateful abstraction — a process that holds state and provides get/update.

```elixir
{:ok, pid} = Agent.start_link(fn -> %{} end)
Agent.get(pid, fn state -> state end)
Agent.update(pid, fn state -> Map.put(state, :key, "value") end)
Agent.get_and_update(pid, fn state ->
  {Map.get(state, :key), Map.put(state, :count, 1)}
end)
```

### When to use Agents vs GenServer

- **Agent** — when you just need get/update on simple state, no complex message handling
- **GenServer** — when you need handle_info, multiple message types, or complex lifecycle

Agents are literally GenServers under the hood — they just provide a simpler API for the common case.

## What to Practice

- Use Task.async/await to parallelize multiple computations
- Use Task.async_stream to process a list concurrently
- Build a supervised task that can fail without crashing the caller
- Implement state management with Agent
- Rewrite an Agent as a GenServer and compare the code
