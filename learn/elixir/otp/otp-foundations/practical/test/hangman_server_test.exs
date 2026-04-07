defmodule Hangman.ServerTest do
  use ExUnit.Case
  alias Hangman.Server

  describe "start_link/1" do
    test "starts server with word" do
      assert {:ok, pid} = Server.start_link("elixir")
      assert Process.alive?(pid)
    end
  end

  describe "guess/2" do
    test "returns display after correct guess" do
      {:ok, pid} = Server.start_link("hi")
      assert {:ok, "h _"} = Server.guess(pid, "h")
    end

    test "returns display after wrong guess" do
      {:ok, pid} = Server.start_link("hi")
      assert {:ok, "_ _"} = Server.guess(pid, "z")
    end

    test "returns :game_over when game is won" do
      {:ok, pid} = Server.start_link("a")
      assert {:game_over, :won} = Server.guess(pid, "a")
    end

    test "returns :game_over when game is lost" do
      {:ok, pid} = Server.start_link("xyz")
      
      # Use up all lives
      for letter <- ["a", "b", "c", "d", "e", "f", "g"] do
        Server.guess(pid, letter)
      end
      
      assert Server.status(pid) == :lost
    end
  end

  describe "display/1" do
    test "returns current display" do
      {:ok, pid} = Server.start_link("apple")
      Server.guess(pid, "p")
      assert Server.display(pid) == "_ p p _ _"
    end
  end

  describe "status/1" do
    test "tracks game status" do
      {:ok, pid} = Server.start_link("hi")
      assert Server.status(pid) == :ongoing
      
      Server.guess(pid, "h")
      assert Server.status(pid) == :ongoing
      
      {:game_over, :won} = Server.guess(pid, "i")
      assert Server.status(pid) == :won
    end
  end

  test "full game flow" do
    {:ok, pid} = Server.start_link("elixir")
    
    # Make some guesses
    {:ok, "e _ _ _ _ _"} = Server.guess(pid, "e")
    {:ok, "e _ _ _ _ _"} = Server.guess(pid, "z")  # wrong
    {:ok, "e _ i _ i _"} = Server.guess(pid, "i")
    
    # Check status is still ongoing
    assert Server.status(pid) == :ongoing
    
    # Finish the game
    Server.guess(pid, "l")
    Server.guess(pid, "x")
    
    {:game_over, :won} = Server.guess(pid, "r")
    assert Server.display(pid) == "e l i x i r"
  end
end
