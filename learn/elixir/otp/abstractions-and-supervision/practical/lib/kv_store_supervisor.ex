defmodule KVStore.Supervisor do
  @moduledoc """
  Supervisor for the KVStore worker.

  TODO: Implement this supervisor with the following requirements:

  1. Use :one_for_one restart strategy
  2. Start a single KVStore child with default options
  3. Make the child :permanent (always restart on crash)

  Then test it:
  - Start the supervisor
  - Verify the KVStore is running
  - Call KVStore.crash() to trigger a restart
  - Observe the supervisor restarts the worker
  """

  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    # TODO: Define children list with KVStore
    # Use :one_for_one strategy

    children = [
      # Add your KVStore child spec here
      KVStore
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
