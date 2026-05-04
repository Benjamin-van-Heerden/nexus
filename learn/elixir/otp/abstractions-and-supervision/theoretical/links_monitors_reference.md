# Links, Monitors, and Trapped Exits — Reference

Use this as the companion reference for the practical exercise:

`/home/benjamin/Documents/nexus/learn/elixir/otp/abstractions-and-supervision/practical/lib/link_monitor_lab.ex`

The goal is not to memorize syntax. The goal is to build a reliable mental model for what happens when BEAM processes observe, link to, or crash because of each other.

---

## 1. Processes fail independently by default

A plain spawned process is isolated from its parent:

```elixir
pid = spawn(fn -> exit(:boom) end)
```

If that process exits, the caller does not automatically die and does not automatically receive a message. Unless you link or monitor it, the failure is mostly invisible to you.

That isolation is one of the BEAM's core design choices: many small processes can fail without taking down unrelated work.

---

## 2. Monitors: one-way observation

A monitor lets one process observe another process dying:

```elixir
pid = spawn(fn ->
  receive do
    :stop -> exit(:done)
  end
end)

ref = Process.monitor(pid)
send(pid, :stop)

receive do
  {:DOWN, ^ref, :process, ^pid, reason} ->
    reason
end
```

When the monitored process exits, the monitoring process receives:

```elixir
{:DOWN, ref, :process, pid, reason}
```

Important properties:

- Monitoring is **one-way**.
- The monitored process does not know it is being watched.
- The monitoring process does **not** die when the monitored process dies.
- The monitor reference lets you distinguish multiple monitored processes.

Use monitors when you want notification without shared fate.

Good examples:

- A request process watching a worker so it can return an error if the worker crashes.
- A process tracking whether a background job completed or failed.
- A parent process collecting results from temporary workers.

Mental model:

> "Tell me when that process dies, but don't make its death my death."

---

## 3. Links: shared fate

A link connects two processes bidirectionally:

```elixir
child = spawn(fn ->
  receive do
    :stop -> exit(:boom)
  end
end)

Process.link(child)
send(child, :stop)
```

If one linked process exits abnormally, the other receives an exit signal. By default, that exit signal kills the linked process too.

Important properties:

- Links are **bidirectional**.
- Abnormal exits usually cascade.
- Links express shared fate: if one side dies, the other probably should too.
- Links are the foundation of supervision.

Use links when two processes are part of one fault domain.

Good examples:

- A supervisor linked to its children.
- Two tightly coupled protocol processes where one is useless without the other.
- A worker process whose failure should be escalated.

Mental model:

> "If that process crashes, I should know in the strongest possible way — by failing too unless I deliberately handle it."

---

## 4. Normal exits are special

Not every exit is treated as failure.

A linked process exiting with `:normal` usually does not kill its linked peers:

```elixir
spawn_link(fn -> exit(:normal) end)
```

This matters because links are not simply "if either exits, both die." More precisely:

- `:normal` means ordinary completion.
- Abnormal reasons like `:boom`, `:error`, or raised exceptions are failure signals.
- `:kill` is untrappable and becomes `:killed` to observers.

For this exercise, focus on the common distinction:

- `:normal` → no cascade
- abnormal reason → cascade unless exits are trapped

---

## 5. Trapping exits: turning link signals into messages

A process can choose to trap exits:

```elixir
Process.flag(:trap_exit, true)
```

After that, exit signals from linked processes become ordinary messages:

```elixir
{:EXIT, pid, reason}
```

Example:

```elixir
Process.flag(:trap_exit, true)

child = spawn_link(fn ->
  receive do
    :stop -> exit(:boom)
  end
end)

send(child, :stop)

receive do
  {:EXIT, ^child, reason} ->
    reason
end
```

Important properties:

- The process must be linked to receive `{:EXIT, pid, reason}`.
- `trap_exit` changes linked exit signals into mailbox messages.
- This lets a process react to failure without dying immediately.
- Supervisors use this idea internally, though OTP wraps it in higher-level behaviour.

Mental model:

> "I still share a link, but I want a chance to handle the exit signal as data."

---

## 6. How this maps to the practical exercise

The practical asks you to implement four behaviours.

### `monitor_worker/1`

You need to:

1. Spawn a worker process.
2. Monitor it with `Process.monitor/1`.
3. Make it exit with the given reason.
4. Receive and return the `{:DOWN, ref, :process, pid, reason}` message.

Core tools:

```elixir
pid = spawn(fn -> ... end)
ref = Process.monitor(pid)
send(pid, ...)
receive do
  {:DOWN, ^ref, :process, ^pid, reason} -> ...
end
```

### `linked_worker_crash/1`

Be careful: do **not** link the test process/caller directly to a crashing process. If you do, the test process may die.

Instead:

1. Spawn an isolated observer process.
2. Monitor that observer from the caller.
3. Inside the observer, link to a child process.
4. Make the linked child exit.
5. Observe whether the observer dies too.

This demonstrates cascading failure safely.

For abnormal reasons like `:boom`, expect the observer to die and the caller to receive a `{:DOWN, ...}` message for the observer.

For `:normal`, the observer should survive long enough to report that it survived.

### `trapped_link_exit/1`

Inside an isolated observer process:

1. Set `Process.flag(:trap_exit, true)`.
2. Spawn/link a child.
3. Make the child exit.
4. Receive `{:EXIT, child_pid, reason}`.
5. Send that message back to the caller.

This proves that trapping exits converts linked failure signals into normal messages.

### `choose_primitive/1`

Use the mental model:

- Use `:link` for shared fate.
- Use `:monitor` for observation without shared fate.

Suggested answers:

```elixir
:supervisor_child -> :link
:two_halves_of_one_protocol -> :link
:request_timeout_tracker -> :monitor
:background_job_notification -> :monitor
```

---

## 7. Practical checklist

Before calling a function done, ask:

- Did I accidentally link the caller/test process to something that can crash?
- Am I matching monitor refs with `^ref` so I don't consume the wrong message?
- Am I returning the actual message shape the tests expect?
- Do I understand whether this situation is shared fate or observation?

If those answers are clear, you understand the core idea. The syntax can be cleaned up with your coding agent.
