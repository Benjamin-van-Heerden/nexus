defmodule SupervisorStrategyLabTest do
  use ExUnit.Case, async: true

  describe "kv_store_child_spec/2" do
    test "builds a named KVStore child spec with the requested restart policy" do
      spec = SupervisorStrategyLab.kv_store_child_spec(:cache, :transient)

      assert spec.id == :cache
      assert spec.restart == :transient
      assert spec.start == {KVStore, :start_link, [[name: :cache]]}
    end

    test "defaults to permanent restart" do
      spec = SupervisorStrategyLab.kv_store_child_spec(:primary)

      assert spec.id == :primary
      assert spec.restart == :permanent
    end
  end

  describe "restart_after_exit?/2" do
    test "permanent children always restart" do
      assert SupervisorStrategyLab.restart_after_exit?(:permanent, :normal)
      assert SupervisorStrategyLab.restart_after_exit?(:permanent, :shutdown)
      assert SupervisorStrategyLab.restart_after_exit?(:permanent, :boom)
    end

    test "temporary children never restart" do
      refute SupervisorStrategyLab.restart_after_exit?(:temporary, :normal)
      refute SupervisorStrategyLab.restart_after_exit?(:temporary, :shutdown)
      refute SupervisorStrategyLab.restart_after_exit?(:temporary, :boom)
    end

    test "transient children restart only after abnormal exits" do
      refute SupervisorStrategyLab.restart_after_exit?(:transient, :normal)
      refute SupervisorStrategyLab.restart_after_exit?(:transient, :shutdown)
      refute SupervisorStrategyLab.restart_after_exit?(:transient, {:shutdown, :done})

      assert SupervisorStrategyLab.restart_after_exit?(:transient, :boom)
      assert SupervisorStrategyLab.restart_after_exit?(:transient, {:badmatch, :value})
    end
  end

  describe "restart_scope/3" do
    setup do
      %{children: [:database, :cache, :web]}
    end

    test "one_for_one restarts only the crashed child", %{children: children} do
      assert SupervisorStrategyLab.restart_scope(:one_for_one, children, :cache) == [:cache]
    end

    test "one_for_all restarts every child", %{children: children} do
      assert SupervisorStrategyLab.restart_scope(:one_for_all, children, :cache) == children
    end

    test "rest_for_one restarts the crashed child and later children", %{children: children} do
      assert SupervisorStrategyLab.restart_scope(:rest_for_one, children, :database) == [
               :database,
               :cache,
               :web
             ]

      assert SupervisorStrategyLab.restart_scope(:rest_for_one, children, :cache) == [:cache, :web]
      assert SupervisorStrategyLab.restart_scope(:rest_for_one, children, :web) == [:web]
    end
  end

  describe "choose_strategy/1" do
    test "matches strategy to dependency shape" do
      assert SupervisorStrategyLab.choose_strategy(:independent_workers) == :one_for_one
      assert SupervisorStrategyLab.choose_strategy(:all_share_in_memory_state) == :one_for_all
      assert SupervisorStrategyLab.choose_strategy(:dependency_chain) == :rest_for_one
    end
  end
end
