defmodule LinkMonitorLab do
  @moduledoc """
  Small OTP lab for observing links, trapped exits, and monitors.

  Keep this module deliberately close to raw process primitives. The point is to
  see what OTP abstractions are built from before moving deeper into supervisors.
  """

  @doc """
  Spawn a worker, monitor it, stop it with `reason`, and return the DOWN message.

  Expected shape:

      {:DOWN, ref, :process, worker_pid, reason}

  Monitors are one-way: the observer should stay alive and receive a message when
  the monitored process exits.
  """
  def monitor_worker(reason \\ :normal) do
    raise "implement me"
  end

  @doc """
  Demonstrate that a normal link cascades failure.

  This function should NOT link the caller/test process directly. Instead, spawn
  an isolated observer process, monitor that observer, then have the observer use
  `spawn_link/1` or `Process.link/1` to link to a child that exits with `reason`.

  Return the observer's DOWN message:

      {:DOWN, ref, :process, observer_pid, observed_reason}

  For an abnormal child exit such as `:boom`, the linked observer should also die.
  """
  def linked_worker_crash(reason \\ :boom) do
    raise "implement me"
  end

  @doc """
  Demonstrate that `Process.flag(:trap_exit, true)` turns linked exits into messages.

  Spawn an isolated observer process. Inside that process:

  1. enable `Process.flag(:trap_exit, true)`
  2. spawn/link a child
  3. make the child exit with `reason`
  4. receive `{:EXIT, child_pid, reason}`
  5. send that message back to the caller

  Return the trapped EXIT message.
  """
  def trapped_link_exit(reason \\ :boom) do
    raise "implement me"
  end

  @doc """
  Choose the better primitive for the situation.

  Return `:link` when the processes should share fate and crash together.
  Return `:monitor` when one process only needs to observe another process dying.

  Scenarios used by the tests:

  - `:supervisor_child`
  - `:request_timeout_tracker`
  - `:two_halves_of_one_protocol`
  - `:background_job_notification`
  """
  def choose_primitive(scenario) do
    raise "implement me"
  end
end
