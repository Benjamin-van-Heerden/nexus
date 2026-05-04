# Elixir

## Background

Benjamin has functional programming experience and some exposure to Elixir syntax, but hasn't built anything substantial with OTP or the BEAM ecosystem. The goal is to go deep on Elixir's concurrency and fault-tolerance primitives rather than surface-level web development.

## End Goal

Build real systems using OTP patterns — GenServers, supervision trees, dynamic supervisors, and the "let it crash" philosophy. Understand when and why to reach for OTP abstractions, and when not to.

## Learning Approach

Tracks:
1. **otp track** — Deep dive into OTP: behaviours, GenServer, supervision, dynamic supervisors, tasks/agents, and a capstone word ladder project.
2. **jido track** — Learn Jido as a BEAM-native agent framework: agents as data, actions, signals, directives, supervised runtimes, plugins, memory, AI tools, and orchestration.
3. **redis track** (future) — Build Redis in Elixir, based on a CodeCrafters project. Applies OTP patterns to a real networked system.

The OTP track comes first to build fluency with the concurrency model. The Jido track builds on that OTP foundation to model production agent systems. The redis track applies OTP patterns to a networked system.

## Reference Material

- `./learn/elixir/reference/` — OTP and Jido course material organized by topic
