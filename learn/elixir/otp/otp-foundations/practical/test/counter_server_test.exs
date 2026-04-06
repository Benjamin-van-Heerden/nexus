defmodule CounterServerTest do
  use ExUnit.Case

  alias CounterServer

  describe "start_link/1" do
    test "starts with default value of 0" do
      {:ok, pid} = CounterServer.start_link()
      assert is_pid(pid)
      assert CounterServer.get_value(pid) == 0
    end

    test "starts with a custom initial value" do
      {:ok, pid} = CounterServer.start_link(42)
      assert CounterServer.get_value(pid) == 42
    end
  end

  describe "get_value/1" do
    test "returns the current counter value" do
      {:ok, pid} = CounterServer.start_link(10)
      assert CounterServer.get_value(pid) == 10
    end
  end

  describe "increment/1" do
    test "increases the counter by 1" do
      {:ok, pid} = CounterServer.start_link(0)
      assert :ok = CounterServer.increment(pid)
      assert CounterServer.get_value(pid) == 1
    end

    test "can be called multiple times" do
      {:ok, pid} = CounterServer.start_link(0)
      CounterServer.increment(pid)
      CounterServer.increment(pid)
      CounterServer.increment(pid)
      assert CounterServer.get_value(pid) == 3
    end
  end

  describe "decrement/1" do
    test "decreases the counter by 1" do
      {:ok, pid} = CounterServer.start_link(5)
      assert :ok = CounterServer.decrement(pid)
      assert CounterServer.get_value(pid) == 4
    end

    test "can go negative" do
      {:ok, pid} = CounterServer.start_link(0)
      CounterServer.decrement(pid)
      assert CounterServer.get_value(pid) == -1
    end
  end

  describe "reset/2" do
    test "resets the counter to a new value" do
      {:ok, pid} = CounterServer.start_link(100)
      assert :ok = CounterServer.reset(pid, 0)
      assert CounterServer.get_value(pid) == 0
    end

    test "can reset to any value" do
      {:ok, pid} = CounterServer.start_link(0)
      CounterServer.increment(pid)
      CounterServer.increment(pid)
      assert :ok = CounterServer.reset(pid, 50)
      assert CounterServer.get_value(pid) == 50
    end
  end

  describe "integration" do
    test "handles mixed operations correctly" do
      {:ok, pid} = CounterServer.start_link(10)

      CounterServer.increment(pid)
      CounterServer.increment(pid)
      CounterServer.decrement(pid)
      assert CounterServer.get_value(pid) == 11

      CounterServer.reset(pid, 0)
      CounterServer.increment(pid)
      assert CounterServer.get_value(pid) == 1
    end
  end
end
