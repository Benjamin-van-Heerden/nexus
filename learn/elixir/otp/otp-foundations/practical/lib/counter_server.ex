defmodule CounterServer do
  @moduledoc """
  A simple GenServer-based counter.

  This exercise practices the fundamental GenServer callbacks:
  - init/1: Initialize the server's state
  - handle_call/3: Handle synchronous requests (get current value)
  - handle_cast/2: Handle asynchronous updates (increment/decrement)

  The counter should support:
  - Starting with an optional initial value (default 0)
  - Getting the current value (synchronous)
  - Incrementing the value (asynchronous)
  - Decrementing the value (asynchronous)
  - Resetting to a specific value (synchronous with reply)
  """

  use GenServer

  # --- Public API ---

  @doc """
  Starts the counter GenServer with an optional initial value.
  Returns {:ok, pid} on success.
  """
  def start_link(initial_value \\ 0) do
    GenServer.start_link(__MODULE__, initial_value)
  end

  @doc """
  Gets the current counter value.
  Returns the integer value.
  """
  def get_value(pid) do
    GenServer.call(pid, :get_value)
  end

  @doc """
  Increments the counter by 1 (asynchronous).
  Returns :ok immediately.
  """
  def increment(pid) do
    GenServer.cast(pid, :increment)
  end

  @doc """
  Decrements the counter by 1 (asynchronous).
  Returns :ok immediately.
  """
  def decrement(pid) do
    GenServer.cast(pid, :decrement)
  end

  @doc """
  Resets the counter to a specific value (synchronous).
  Returns :ok on success.
  """
  def reset(pid, new_value) do
    GenServer.call(pid, {:reset, new_value})
  end

  # --- Callbacks ---

  @impl true
  def init(initial_value) do
    {:ok, initial_value}
  end

  @impl true
  def handle_call(:get_value, _from, state) do
    {:reply, state, state}
  end

  @impl true
  def handle_call({:reset, new_value}, _from, _state) do
    {:reply, :ok, new_value}
  end

  @impl true
  def handle_cast(:increment, state) do
    {:noreply, state + 1}
  end

  @impl true
  def handle_cast(:decrement, state) do
    {:noreply, state - 1}
  end
end
