# Word Ladder Project: CLI and Dynamic Supervisor

## Part 3: Command Line UI

Build a simple CLI that lets a user play from IEx or the terminal:

```elixir
defmodule WordLadder.CLI do
  def play do
    {:ok, pid} = WordLadder.Server.start_link(dictionary: "words.txt")
    IO.puts(WordLadder.Server.display(pid))
    loop(pid)
  end

  defp loop(pid) do
    word = IO.gets("Your move: ") |> String.trim()
    case WordLadder.Server.guess(pid, word) do
      {:ok, display} ->
        IO.puts(display)
        if WordLadder.Server.won?(pid), do: IO.puts("You win!"), else: loop(pid)
      {:error, reason} ->
        IO.puts("Invalid: #{reason}")
        loop(pid)
    end
  end
end
```

## Part 4: Dynamic Supervisor for Multiplayer

Make the game multiplayer — multiple simultaneous games, each managed by a named process under a DynamicSupervisor.

### Structure

1. **DynamicSupervisor** — starts game servers on demand
2. **Registry** — maps game IDs to PIDs so players can join by name
3. **Game API** — `create_game(id)`, `join_game(id)`, `guess(id, word)`

```elixir
defmodule WordLadder.GameSupervisor do
  use DynamicSupervisor

  def start_link(_), do: DynamicSupervisor.start_link(__MODULE__, :ok, name: __MODULE__)
  def init(:ok), do: DynamicSupervisor.init(strategy: :one_for_one)

  def create_game(game_id) do
    DynamicSupervisor.start_child(__MODULE__, {WordLadder.Server, id: game_id})
  end
end
```

### What This Exercises

- Everything from the course: functional core, GenServer, supervision, dynamic supervisor, registry
- Process lifecycle: games start, players interact, games end and clean up
- Named processes: find a game by ID, not by PID

## What to Build

1. CLI module for single-player interaction
2. DynamicSupervisor for starting game processes
3. Registry for named game lookup
4. Multiplayer support: create, join, and play multiple games from IEx
