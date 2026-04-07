defmodule Hangman.CoreTest do
  use ExUnit.Case
  alias Hangman.Core

  describe "new/1" do
    test "creates game with word and 7 lives" do
      game = Core.new("elixir")
      assert Core.lives(game) == 7
    end
  end

  describe "guess/2" do
    test "correct guess adds letter to guesses" do
      game = Core.new("elixir")
           |> Core.guess("e")

      assert Core.lives(game) == 7  # correct guess doesn't cost life
    end

    test "wrong guess decrements lives" do
      game = Core.new("elixir")
           |> Core.guess("z")

      assert Core.lives(game) == 6
    end

    test "repeated correct guess is ignored" do
      game = Core.new("elixir")
           |> Core.guess("e")
           |> Core.guess("e")

      assert Core.lives(game) == 7
    end

  end

  describe "display/1" do
    test "shows underscores for unguessed letters" do
      game = Core.new("hi")
      assert Core.display(game) == "_ _"
    end

    test "reveals guessed letters" do
      game = Core.new("apple")
           |> Core.guess("p")

      assert Core.display(game) == "_ p p _ _"
    end

    test "reveals all letters when all guessed" do
      game = Core.new("hi")
           |> Core.guess("h")
           |> Core.guess("i")

      assert Core.display(game) == "h i"
    end
  end

  describe "status/1" do
    test "returns :ongoing for new game" do
      assert Core.status(Core.new("word")) == :ongoing
    end

    test "returns :won when all letters guessed" do
      game = Core.new("hi")
           |> Core.guess("h")
           |> Core.guess("i")

      assert Core.status(game) == :won
    end

    test "returns :lost when lives reach 0" do
      game = Core.new("hi")
           |> Core.guess("a")  # 6 lives
           |> Core.guess("b")  # 5
           |> Core.guess("c")  # 4
           |> Core.guess("d")  # 3
           |> Core.guess("e")  # 2
           |> Core.guess("f")  # 1
           |> Core.guess("g")  # 0

      assert Core.status(game) == :lost
    end
  end

  describe "won?/1 and lost?/1" do
    test "won? returns true when game won" do
      game = Core.new("a") |> Core.guess("a")
      assert Core.won?(game)
      refute Core.lost?(game)
    end

    test "lost? returns true when game lost" do
      game = Core.new("xyz")
           |> Core.guess("a")
           |> Core.guess("b")
           |> Core.guess("c")
           |> Core.guess("d")
           |> Core.guess("e")
           |> Core.guess("f")
           |> Core.guess("g")

      assert Core.lost?(game)
      refute Core.won?(game)
    end
  end
end
