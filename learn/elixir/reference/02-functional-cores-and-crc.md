# Functional Cores and the CRC Pattern

## Functional Core, Imperative Shell

The key OTP design pattern: keep your business logic in pure functions (the functional core), and confine side effects to the GenServer boundary (the imperative shell).

Your GenServer callbacks should be thin — they receive messages, call pure functions, and return new state. The pure functions are easy to test, easy to reason about, and don't depend on OTP at all.

## CRC: Construct, Reduce, Convert

A pattern for structuring the functional core:

1. **Construct** — Build the initial data structure. A function that takes arguments and returns the starting state.
2. **Reduce** — Transform the state. Pure functions that take state + input and return new state. This is where the logic lives.
3. **Convert** — Extract information from the state. Functions that query or format the state for output.

```elixir
# Construct
def new(word), do: %{word: word, guesses: [], lives: 7}

# Reduce
def guess(game, letter) do
  %{game | guesses: [letter | game.guesses]}
  |> update_lives(letter)
end

# Convert
def display(game), do: "#{mask(game.word, game.guesses)} (#{game.lives} lives)"
```

## Why CRC Matters

- Pure functions are trivially testable
- The GenServer becomes a thin wrapper: `handle_call(:guess, _, state) -> {:reply, result, new_state}`
- You can develop and test the entire game/domain logic without starting any processes
- When bugs happen, they're in the pure logic (easy to reproduce) not in the process machinery

## What to Practice

- Build a functional core for a simple domain (counter, game, calculator)
- Structure it as Construct/Reduce/Convert
- Write tests for the core without using GenServer at all
