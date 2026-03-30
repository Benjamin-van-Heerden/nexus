# OTP Core Abstractions, Links, and Monitors

## OTP Core Abstractions

OTP provides several process abstractions beyond GenServer:

- **GenServer** — stateful server process (request-response and fire-and-forget)
- **Supervisor** — monitors child processes and restarts them on failure
- **DynamicSupervisor** — supervisor for processes created at runtime
- **Task** — one-off async computation
- **Agent** — simple state wrapper (GenServer without the ceremony)
- **Registry** — process name registry for dynamic lookup

Each abstracts away the raw process primitives (spawn, send, receive) and gives you a structured contract.

## Links

`Process.link/1` or `spawn_link` creates a bidirectional link between two processes. If either dies, the other receives an exit signal.

- Default behaviour: linked process also dies (cascading failure)
- With `Process.flag(:trap_exit, true)`: exit signal becomes a message `{:EXIT, pid, reason}` in `handle_info`

Links are the foundation of supervision — a supervisor links to its children so it knows when they crash.

## Monitors

`Process.monitor/1` creates a unidirectional watch. If the monitored process dies, the monitoring process receives `{:DOWN, ref, :process, pid, reason}`.

- Monitor does NOT kill the monitoring process
- One-directional: monitored process doesn't know it's being watched
- Returns a reference for selective demonitoring

## Links vs Monitors

| | Links | Monitors |
|---|---|---|
| Direction | Bidirectional | Unidirectional |
| Default on death | Linked process also dies | Message received |
| Use case | Supervision, co-dependent processes | Observing, notifications |

## What to Practice

- Link two processes and observe cascading failure
- Trap exits and handle `{:EXIT, pid, reason}` in handle_info
- Monitor a process and handle `{:DOWN, ...}` messages
- Understand when to use links vs monitors
