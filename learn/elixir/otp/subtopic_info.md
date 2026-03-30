# OTP Deep Dive

## What are we learning?

OTP (Open Telecom Platform) — Elixir's framework for building concurrent, fault-tolerant applications. Covers the full stack: behaviours, GenServer, supervision trees, dynamic supervisors, tasks, agents, and design patterns. Culminates in a word ladder game that integrates all the concepts.

## Why are we learning this?

OTP is the reason to use Elixir. Without it, Elixir is just a nice functional language. With it, you get a battle-tested framework for building systems that recover from failures, scale across cores, and manage state cleanly. Understanding OTP deeply is the difference between writing Elixir and thinking in Elixir.

## How will we learn?

Bottom-up through the OTP stack. Start with the primitives (behaviours, GenServer callbacks, CRC pattern), build up through supervision and abstractions, then apply everything in a capstone project. Practical exercises are the core — most concepts only click when you build something with them.

## Phases

1. **otp-foundations** — Behaviours, functional cores, CRC (Construct/Reduce/Convert) pattern, GenServer message callbacks
2. **abstractions-and-supervision** — OTP core abstractions, links and monitors, supervisors, child specs, restart strategies
3. **advanced-patterns** — Dynamic supervisors, registries, design concepts (when not to OTP), backpressure, tasks, agents
4. **capstone** — Word ladder game: functional core, GenServer boundary, validation, CLI, dynamic supervisor for multiplayer

## Resources

- OTP course material in `./learn/elixir/reference/`
- Elixir documentation: https://hexdocs.pm/elixir/
- OTP documentation: https://hexdocs.pm/elixir/otp.html
