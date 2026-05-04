defmodule LinkMonitorLabTest do
  use ExUnit.Case, async: false

  describe "monitor_worker/1" do
    test "returns a DOWN message without killing the caller" do
      caller = self()

      assert {:DOWN, ref, :process, worker_pid, :done} = LinkMonitorLab.monitor_worker(:done)
      assert is_reference(ref)
      assert is_pid(worker_pid)
      assert Process.alive?(caller)
    end

    test "preserves abnormal exit reasons" do
      assert {:DOWN, _ref, :process, _worker_pid, {:error, :bad_input}} =
               LinkMonitorLab.monitor_worker({:error, :bad_input})
    end
  end

  describe "linked_worker_crash/1" do
    test "an abnormal linked child exit kills the linked observer" do
      assert {:DOWN, ref, :process, observer_pid, :boom} = LinkMonitorLab.linked_worker_crash(:boom)
      assert is_reference(ref)
      assert is_pid(observer_pid)
      refute Process.alive?(observer_pid)
    end

    test "normal exits do not cascade as failures" do
      # A linked process exiting :normal does not kill its linked peer. The helper
      # should prove this by returning a clean observer result instead of a DOWN
      # caused by :normal.
      assert {:observer_survived, :normal} = LinkMonitorLab.linked_worker_crash(:normal)
    end
  end

  describe "trapped_link_exit/1" do
    test "trap_exit converts linked child crash into an EXIT message" do
      assert {:EXIT, child_pid, :boom} = LinkMonitorLab.trapped_link_exit(:boom)
      assert is_pid(child_pid)
    end

    test "trap_exit preserves structured exit reasons" do
      assert {:EXIT, _child_pid, {:shutdown, :maintenance}} =
               LinkMonitorLab.trapped_link_exit({:shutdown, :maintenance})
    end
  end

  describe "choose_primitive/1" do
    test "uses links for shared fate" do
      assert LinkMonitorLab.choose_primitive(:supervisor_child) == :link
      assert LinkMonitorLab.choose_primitive(:two_halves_of_one_protocol) == :link
    end

    test "uses monitors for observation without shared fate" do
      assert LinkMonitorLab.choose_primitive(:request_timeout_tracker) == :monitor
      assert LinkMonitorLab.choose_primitive(:background_job_notification) == :monitor
    end
  end
end
