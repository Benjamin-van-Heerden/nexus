# Dynamic Supervisors and Registries

## Dynamic Supervisors

Regular supervisors start children at boot with a fixed list. DynamicSupervisor starts children on demand at runtime.

```elixir
defmodule MyApp.GameSupervisor do
  use DynamicSupervisor

  def start_link(init_arg) do
    DynamicSupervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  def init(_init_arg) do
    DynamicSupervisor.init(strategy: :one_for_one)
  end

  def start_game(game_id) do
    DynamicSupervisor.start_child(__MODULE__, {GameServer, game_id})
  end
end
```

Use cases: chat rooms, game sessions, user connections — anything where the number of processes is determined at runtime.

## Registries

A Registry maps names to PIDs, allowing you to look up processes by a meaningful key rather than a PID.

```elixir
# In your application supervisor's children:
{Registry, keys: :unique, name: MyApp.GameRegistry}

# In your GenServer:
def start_link(game_id) do
  GenServer.start_link(__MODULE__, game_id, name: via_tuple(game_id))
end

defp via_tuple(game_id) do
  {:via, Registry, {MyApp.GameRegistry, game_id}}
end

# Looking up:
def get_game(game_id) do
  GenServer.call(via_tuple(game_id), :get_state)
end
```

### Registry keys
- `:unique` — one process per key (most common)
- `:duplicate` — multiple processes per key (pub/sub pattern)

## The Power of a Name

Named processes are the glue in OTP systems. With a registry:
- Clients don't need to track PIDs
- Processes can be restarted and re-registered transparently
- The supervisor + registry + dynamic supervisor pattern gives you a self-healing pool of named workers

## What to Practice

- Build a DynamicSupervisor that starts workers on demand
- Add a Registry for named lookup
- Start multiple game/session processes and interact with them by name
- Crash a named process and verify it restarts with the same name
