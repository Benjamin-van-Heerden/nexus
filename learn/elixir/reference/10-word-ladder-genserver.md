# Word Ladder Project: GenServer Boundary and Validation

## Part 2: GenServer Boundary

Wrap the functional core in a GenServer. The server holds the game state; clients interact through the API.

### GenServer Structure

```elixir
defmodule WordLadder.Server do
  use GenServer

  # API
  def start_link(opts), do: GenServer.start_link(__MODULE__, opts)
  def guess(pid, word), do: GenServer.call(pid, {:guess, word})
  def display(pid), do: GenServer.call(pid, :display)
  def state(pid), do: GenServer.call(pid, :state)

  # Callbacks
  def init(opts) do
    {:ok, WordLadder.Core.new(opts[:dictionary])}
  end

  def handle_call({:guess, word}, _from, game) do
    case WordLadder.Core.make_move(game, word) do
      {:ok, new_game} -> {:reply, {:ok, WordLadder.Core.display(new_game)}, new_game}
      {:error, reason} -> {:reply, {:error, reason}, game}
    end
  end
end
```

### Validation Layer

Move validation belongs in the functional core, but error messages flow through the GenServer:

- Word not in dictionary → `{:error, :not_a_word}`
- More than one letter changed → `{:error, :too_many_changes}`
- Same word → `{:error, :no_change}`
- Already won → `{:error, :game_over}`

The GenServer callback is thin — it calls the core and wraps the result.

## What to Build

1. GenServer module wrapping the functional core
2. Clean API layer (start_link, guess, display)
3. Error handling that passes validation results back to the caller
4. Tests that start a real GenServer process and play through a game
