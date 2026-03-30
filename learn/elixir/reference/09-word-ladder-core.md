# Word Ladder Project: Functional Core

## The Project

Build a word ladder game using OTP. A random 4-letter word is chosen as a base, another as a target. The player changes one letter at a time, forming valid words, to reach the target.

```
mice -> mite -> ... -> cats
```

## Part 1: Functional Core (CRC)

Build the entire game logic as pure functions before touching GenServer.

### Construct

- Load a dictionary of valid 4-letter words
- Choose a random base word and a random target word
- Initialize the state: base, target, current word (starts as base), move history

```elixir
defmodule WordLadder.Core do
  defstruct [:base, :target, :current, :moves, :dictionary]

  def new(dictionary_path) do
    words = load_dictionary(dictionary_path)
    base = Enum.random(words)
    target = Enum.random(words -- [base])
    %__MODULE__{
      base: base,
      target: target,
      current: base,
      moves: [base],
      dictionary: MapSet.new(words)
    }
  end
end
```

### Reduce

- `make_move(game, word)` — validate the move and update state
- Validation: new word must differ by exactly one letter from current, must be a valid dictionary word
- Track move history

### Convert

- `display(game)` — render the ladder: `mice -> mite -> ... -> cats`
- `won?(game)` — check if current == target
- `move_count(game)` — number of moves so far

## What to Build

1. A module with the game struct and CRC functions
2. Validation that enforces the one-letter-change rule
3. Dictionary loading (a text file with one word per line)
4. Tests for all pure functions — no processes needed
