# OTP Basics and Elixir Behaviours

## What is OTP?

OTP (Open Telecom Platform) is Erlang/Elixir's framework for building concurrent, fault-tolerant, distributed applications. It provides:

- **Behaviours** — contracts that define how a module should behave (GenServer, Supervisor, Application, etc.)
- **Supervision trees** — hierarchical process structures that restart failed processes
- **Applications** — self-contained units of functionality that can be started and stopped

OTP is not a library you import — it's an architecture you follow. The patterns are the point.

## Elixir Behaviours

A behaviour is a contract: a module declares `@callback` functions, and any module that `use`s it must implement them.

```elixir
defmodule MyBehaviour do
  @callback init(args :: term()) :: {:ok, state :: term()}
  @callback handle(event :: term(), state :: term()) :: {:ok, new_state :: term()}
end
```

GenServer is the most important behaviour. It separates the concurrent concerns (message passing, process lifecycle) from your business logic (the callbacks you implement).

## The OTP Mental Model

Think of OTP processes as independent actors:
- Each has its own state
- They communicate only via messages
- If one crashes, others can detect and respond
- The system is designed to recover, not prevent failure

## What to Practice

- Implement a module that uses the GenServer behaviour
- Understand the callback contract: `init/1`, `handle_call/3`, `handle_cast/2`, `handle_info/2`
- Understand why OTP separates the "server" (GenServer) from your "module" (your callbacks)
