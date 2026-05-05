defmodule SupervisorStrategyLab do
  @moduledoc """
  A small lab for modelling supervisor child specs and restart semantics.

  This exercise is deliberately partly pure. Before you rely on OTP to do the
  restarting, you should be able to predict what it will do.
  """

  @doc """
  Build a child spec for a named KVStore process.

  Requirements:

  - start `KVStore` with the provided `name`
  - set the child spec `id` to the same `name`
  - set the restart policy to `restart`

  Example shape:

      %{
        id: :cache,
        start: {KVStore, :start_link, [[name: :cache]]},
        restart: :permanent
      }
  """
  def kv_store_child_spec(name, restart \\ :permanent) do
    raise "implement me"
  end

  @doc """
  Return whether a child with `restart_policy` should restart after `exit_reason`.

  Rules:

  - `:permanent` always restarts
  - `:temporary` never restarts
  - `:transient` restarts on abnormal exits, but not on:
    - `:normal`
    - `:shutdown`
    - `{:shutdown, term}`
  """
  def restart_after_exit?(restart_policy, exit_reason) do
    raise "implement me"
  end

  @doc """
  Given a supervisor strategy, child order, and crashed child id, return the child
  ids that would be restarted by the strategy.

  This function models the strategy blast radius only. It does not apply the
  crashed child's `:restart` policy.

  Examples with child order `[:database, :cache, :web]`:

      restart_scope(:one_for_one, children, :cache)
      #=> [:cache]

      restart_scope(:one_for_all, children, :cache)
      #=> [:database, :cache, :web]

      restart_scope(:rest_for_one, children, :cache)
      #=> [:cache, :web]
  """
  def restart_scope(strategy, child_order, crashed_child_id) do
    raise "implement me"
  end

  @doc """
  Choose the best supervisor strategy for a relationship between children.

  Return one of:

  - `:one_for_one`
  - `:one_for_all`
  - `:rest_for_one`

  Scenarios used by the tests:

  - `:independent_workers`
  - `:all_share_in_memory_state`
  - `:dependency_chain`
  """
  def choose_strategy(scenario) do
    raise "implement me"
  end
end
