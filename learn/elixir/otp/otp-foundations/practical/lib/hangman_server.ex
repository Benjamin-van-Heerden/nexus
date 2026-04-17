defmodule Hangman.Server do
  @moduledoc """
  GenServer wrapper (imperative shell) for the Hangman game.

  This module should be a thin wrapper around Hangman.Core.
  All business logic lives in the Core — this just manages the process state.

  Implement:
  - start_link/1 — start the server with a word
  - guess/2 — synchronous call to make a guess
  - display/1 — synchronous call to get display string
  - status/1 — synchronous call to get game status
  """
  use GenServer
  alias Hangman.Core

  # Client API

  @doc "Start the Hangman server with a word"
  @spec start_link(String.t()) :: GenServer.on_start()
  def start_link(word) do
    GenServer.start_link(__MODULE__, word)
  end

  @doc "Make a guess (synchronous call)"
  @spec guess(pid(), String.t()) :: {:ok, String.t()} | {:game_over, atom()}
  def guess(pid, letter) do
    GenServer.call(pid, {:guess, letter})
  end

  @doc "Get the display string"
  @spec display(pid()) :: String.t()
  def display(pid) do
    GenServer.call(pid, :display)
  end

  @doc "Get the game status"
  @spec status(pid()) :: :ongoing | :won | :lost
  def status(pid) do
    GenServer.call(pid, :status)
  end

  # Server Callbacks

  @impl true
  def init(word) do
    {:ok, Core.new(word)}
  end

  @impl true
  def handle_call({:guess, letter}, _from, state) do
    new_state = Core.guess(state, letter)

    tup_res =
      case new_state.status do
        :won -> {:game_over, :won}
        :lost -> {:game_over, :lost}
        :ongoing -> {:ok, Core.display(new_state)}
      end

    {:reply, tup_res, new_state}
  end

  @impl true
  def handle_call(:display, _from, state) do
    {:reply, Core.display(state), state}
  end

  @impl true
  def handle_call(:status, _from, state) do
    {:reply, Core.status(state), state}
  end
end
