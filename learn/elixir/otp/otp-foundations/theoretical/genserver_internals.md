# GenServer Internals and OTP Behaviours

## What is a Behaviour?

In Elixir, a **behaviour** is a contract. It defines a set of callbacks that a module must implement. The compiler can't enforce this contract (Elixir is dynamically typed), but the behaviour module provides default implementations and the `@impl` attribute gives us compile-time warnings if we miss a callback.

```elixir
defmodule MyServer do
  use GenServer  # Imports the behaviour and default callbacks
  
  @impl true     # Tells compiler: "I'm intentionally implementing a callback"
  def init(state) do
    {:ok, state}
  end
end
```

## The GenServer Loop

At its core, a GenServer is just a process running a loop:

```
loop(state) do
  receive message
  -> handle message
  -> update state  
  -> loop(new_state)
end
```

The `GenServer` behaviour abstracts this pattern. When you `use GenServer`, you get:
- Process spawning (`start_link/3`)
- Message reception and routing
- State management
- System message handling (debug, tracing, etc.)

## Message Types: Call vs Cast

### `handle_call/3` — Synchronous

```elixir
def handle_call(:get_balance, _from, state) do
  {:reply, state.balance, state}
end
```

- **Blocking**: Caller waits for response
- **Reliable**: Caller knows if request succeeded or failed
- **Use for**: Values you need immediately, critical operations, anything where failure matters
- **Returns**: `{:reply, response, new_state}` or `{:noreply, new_state}` (reply later)

The `_from` argument contains `{pid, ref}` — you can use this to reply asynchronously later with `GenServer.reply/2`.

### `handle_cast/2` — Asynchronous

```elixir
def handle_cast({:log_event, event}, state) do
  new_state = [event | state.events]
  {:noreply, new_state}
end
```

- **Non-blocking**: Caller sends and forgets
- **Fire-and-forget**: No confirmation of success
- **Use for**: Logging, metrics, side effects where you don't need confirmation
- **Returns**: `{:noreply, new_state}` only

**Why "use sparingly"?** The docs warn about casts because:
1. If the GenServer crashes, casts are lost (no backpressure)
2. No feedback means harder to debug
3. Can overwhelm a slow GenServer's mailbox

## The Process Mailbox

Every process has a mailbox — a queue of messages. GenServer manages this queue:

1. Messages arrive (from `call`, `cast`, or raw `send`)
2. GenServer extracts OTP-internal messages (system messages)
3. User messages go to your callbacks
4. Unrecognized messages trigger `handle_info/2`

```elixir
# Raw process message (not call/cast)
def handle_info(:timeout, state) do
  {:noreply, state}
end
```

## When to Use What?

| Pattern | Use When | Example |
|---------|----------|---------|
| `Agent` | Simple get/update state | Caching, counters |
| `GenServer.call` | You need the result now | Database query, validation |
| `GenServer.cast` | Side effect, don't need confirmation | Logging, analytics |
| `Task` | One-off async work | HTTP request, file I/O |
| Raw `spawn` | You know what you're doing | Rarely — use Task instead |

## The @impl Attribute

Always use `@impl true` before callbacks. It:
1. Documents intent ("this is a behaviour callback")
2. Enables compiler warnings if callback signature is wrong
3. Makes refactoring safer

```elixir
@impl true
def init(_) do  # Compiler warns if this doesn't match GenServer.init/1
  {:ok, %State{}}
end
```

## Key Takeaways

1. **Behaviours are contracts** — they define expected callbacks
2. **Call = sync, Cast = async** — choose based on whether you need confirmation
3. **State flows through returns** — each callback returns `{:reply, resp, state}` or `{:noreply, state}`
4. **GenServer is a loop abstraction** — understand the mailbox and message handling
5. **Use @impl true** — it catches bugs and documents intent
