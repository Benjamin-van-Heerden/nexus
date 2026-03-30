# Design Concepts: When Not to OTP, and Backpressure

## When Not to OTP

Not everything needs a process. Common over-OTP patterns:

- **Don't GenServer for pure computation** — if there's no state to manage and no concurrency need, a plain module with functions is better.
- **Don't GenServer for configuration** — use Application config or module attributes.
- **Don't GenServer as a cache without reason** — ETS tables are often simpler and faster for read-heavy shared state.
- **Don't GenServer for sequential pipelines** — if there's no parallelism benefit, a pipeline of function calls is clearer.

### The test: does this need a process?

A process is warranted when you need:
1. **Mutable state** that multiple callers access
2. **Concurrency** — work that should happen in parallel
3. **Fault isolation** — failure in this component shouldn't take down others
4. **Lifecycle management** — something needs to start, stop, and restart

If none apply, use plain functions.

## Backpressure

GenServer mailboxes are unbounded. If producers send messages faster than the server can process them, the mailbox grows without limit until the system runs out of memory.

### Solutions

- **Use `call` instead of `cast`** — synchronous calls naturally throttle the caller. The caller blocks until the server responds.
- **Bounded queues** — limit mailbox size externally (e.g., a separate process that rejects overflow).
- **GenStage / Flow** — Elixir's demand-driven processing pipeline. Consumers tell producers how many events they can handle.
- **Load shedding** — drop messages when overwhelmed rather than queueing indefinitely.

### The rule of thumb

Default to `handle_call`. Only use `handle_cast` when:
- The caller genuinely doesn't need a response
- You have another backpressure mechanism in place
- The operation is truly fire-and-forget (logging, metrics)

## What to Practice

- Identify scenarios where a GenServer is and isn't appropriate
- Build a system that demonstrates mailbox overflow with cast
- Refactor it to use call for backpressure
- Experiment with process message queues using `Process.info(pid, :message_queue_len)`
