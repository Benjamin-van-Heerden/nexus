defmodule MultiStore.Supervisor do
  @moduledoc """
  Extended supervisor managing multiple KVStore instances.
  
  TODO: Implement this supervisor with:
  
  1. Start THREE separate KVStore workers with different names:
     - :kv_store_a
     - :kv_store_b
     - :kv_store_c
  
  2. Experiment with different restart strategies:
     - Try :one_for_all (one crashes, all restart)
     - Try :rest_for_one (crash store_a, b and c restart)
  
  3. Make store_a :transient (only restart on abnormal exit)
     and the others :permanent
  
  Testing checklist:
  - Start supervisor and verify all 3 stores run
  - Crash store_a with :abnormal exit → should restart
  - Crash store_a with :normal exit → transient, should NOT restart
  - Crash store_b with :one_for_all → all should restart
  """
  
  use Supervisor
  
  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end
  
  @impl true
  def init(_init_arg) do
    children = [
      # TODO: Add three KVStore children with different names
      # Experiment with restart: :permanent | :transient
    ]
    
    # TODO: Try different strategies: :one_for_one, :one_for_all, :rest_for_one
    Supervisor.init(children, strategy: :one_for_one)
  end
end