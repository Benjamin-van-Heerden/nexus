defmodule Hangman.Core do
  @moduledoc """
  Functional core for a Hangman game.

  Implement this module using the CRC pattern:
  - Construct: new/1 — create initial game state
  - Reduce: guess/2 — process a letter guess
  - Convert: display/1, status/1, won?/1, lost?/1 — query state

  The game state should track:
  - The secret word
  - Letters guessed so far
  - Remaining lives (start with 7)

  Rules:
  - Correct guesses don't cost a life
  - Repeated guesses don't cost a life (just ignored)
  - Wrong guesses decrement lives
  - Game ends when word is guessed (won) or lives reach 0 (lost)
  """

  @doc "Construct a new game with the given word"
  @spec new(String.t()) :: map()
  def new(word) do
    %{status: :ongoing, word: word |> String.downcase() |> String.to_charlist(), correct_letters: MapSet.new(), lives: 7}
  end

  @doc "Reduce: process a guess, return updated game state"
  @spec guess(map(), String.t()) :: map()
  def guess(game, letter) do
    letter = String.downcase(letter) |> String.to_charlist() |> Enum.at(0)
    case letter in game.word do
      true -> case won?(%{game | correct_letters: MapSet.put(game.correct_letters, letter)}) do
        true -> %{game | status: :won,  correct_letters: MapSet.put(game.correct_letters, letter)}
        false -> %{game | correct_letters: MapSet.put(game.correct_letters, letter)}
      end

      false -> case lost?(game) do
          true -> %{game | status: :lost, lives: 0 }
          false -> %{game | lives: game.lives - 1}
        end
    end
  end

  @doc "Convert: return display string (e.g., '_ p p _ e' for 'apple' with 'p' guessed)"
  @spec display(map()) :: String.t()
  def display(game) do
    for letter <- game.word do
      case MapSet.member?(game.correct_letters, letter) do
        true -> "#{<<letter::utf8>>} "
        false -> "_ "
      end
    end |> Enum.join() |> String.trim()
  end

  @doc "Convert: return :ongoing, :won, or :lost"
  @spec status(map()) :: :ongoing | :won | :lost
  def status(game) do
    game.status
  end

  @doc "Convert: check if game is won"
  @spec won?(map()) :: boolean()
  def won?(game) do
    game.word |> MapSet.new() |> MapSet.equal?(game.correct_letters)
  end

  @doc "Convert: check if game is lost"
  @spec lost?(map()) :: boolean()
  def lost?(game) do
     game.lives - 1 <= 0
  end

  @doc "Convert: get remaining lives"
  @spec lives(map()) :: integer()
  def lives(game) do
    game.lives
  end
end
