defmodule KVStore do
  @moduledoc """
  A simple key-value store implemented as a GenServer.
  
  This is the worker that will be supervised. It stores data in memory
  and can crash in specific ways to demonstrate supervisor restart behavior.
  """
  
  use GenServer
  
  # Client API
  
  def start_link(opts) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, opts, name: name)
  end
  
  @doc """
  Stores a key-value pair.
  """
  def put(pid_or_name \\ __MODULE__, key, value) do
    GenServer.call(pid_or_name, {:put, key, value})
  end
  
  @doc """
  Retrieves a value by key.
  """
  def get(pid_or_name \\ __MODULE__, key) do
    GenServer.call(pid_or_name, {:get, key})
  end
  
  @doc """
  Deletes a key.
  """
  def delete(pid_or_name \\ __MODULE__, key) do
    GenServer.call(pid_or_name, {:delete, key})
  end
  
  @doc """
  Intentionally crashes the process (for testing supervisor restarts).
  """
  def crash(pid_or_name \\ __MODULE__) do
    GenServer.cast(pid_or_name, :crash)
  end
  
  @doc """
  Gets all keys in the store.
  """
  def keys(pid_or_name \\ __MODULE__) do
    GenServer.call(pid_or_name, :keys)
  end
  
  # Server Callbacks
  
  @impl true
  def init(opts) do
    # If :crash_on_init is set, crash immediately to test supervisor restart
    if Keyword.get(opts, :crash_on_init, false) do
      raise "Simulated init crash"
    end
    
    {:ok, %{}}
  end
  
  @impl true
  def handle_call({:put, key, value}, _from, state) do
    new_state = Map.put(state, key, value)
    {:reply, :ok, new_state}
  end
  
  @impl true
  def handle_call({:get, key}, _from, state) do
    {:reply, Map.get(state, key), state}
  end
  
  @impl true
  def handle_call({:delete, key}, _from, state) do
    {:reply, :ok, Map.delete(state, key)}
  end
  
  @impl true
  def handle_call(:keys, _from, state) do
    {:reply, Map.keys(state), state}
  end
  
  @impl true
  def handle_cast(:crash, state) do
    raise "Intentional crash requested"
    {:noreply, state}
  end
end