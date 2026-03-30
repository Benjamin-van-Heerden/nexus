# GenServer Message Callbacks

## The Callback Contract

GenServer defines the process lifecycle and message handling. You implement callbacks:

### init/1
Called when the process starts. Returns `{:ok, initial_state}` or `{:stop, reason}`.

```elixir
def init(args) do
  {:ok, MyCore.new(args)}
end
```

### handle_call/3 — Synchronous
Client sends a message and waits for a reply. The most common pattern.

```elixir
def handle_call(:get, _from, state) do
  {:reply, MyCore.value(state), state}
end

def handle_call({:update, val}, _from, state) do
  new_state = MyCore.update(state, val)
  {:reply, :ok, new_state}
end
```

### handle_cast/2 — Asynchronous (fire-and-forget)
Client sends a message and doesn't wait. Use sparingly — you lose backpressure.

```elixir
def handle_cast({:log, msg}, state) do
  {:noreply, MyCore.log(state, msg)}
end
```

### handle_info/2 — Everything else
Messages not sent via `call` or `cast` — timers, monitors, raw sends.

```elixir
def handle_info(:tick, state) do
  Process.send_after(self(), :tick, 1000)
  {:noreply, MyCore.tick(state)}
end
```

## The API Layer

Always wrap GenServer calls in a public API:

```elixir
def get(pid), do: GenServer.call(pid, :get)
def update(pid, val), do: GenServer.call(pid, {:update, val})
def log(pid, msg), do: GenServer.cast(pid, {:log, msg})
```

This hides the message format from callers. If you change the internal protocol, the API stays the same.

## What to Practice

- Implement a GenServer with all four callbacks
- Build the API layer
- Connect a functional core to GenServer callbacks (thin boundary pattern)
- Use `handle_info` with `Process.send_after` for periodic work
