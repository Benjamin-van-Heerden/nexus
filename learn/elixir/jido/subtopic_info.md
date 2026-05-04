# Jido Agent Framework

## What are we learning?

Jido as a BEAM-native agent framework for building deterministic, testable agent systems in Elixir. The course covers Jido agents, actions, signals, directives, supervised runtime execution, plugins, workflows, memory, AI agents, tool use, and production readiness.

## Why are we learning this?

Jido is interesting because it maps agent systems onto familiar Elixir/OTP ideas without reducing the problem to an LLM wrapper. Agents are schema-backed data, actions are validated transitions, signals are typed event envelopes, directives describe effects, and `Jido.AgentServer` supplies the OTP runtime boundary when lifecycle and concurrency are needed.

## How will we learn?

Work through the Jido stack from deterministic core primitives to runtime orchestration and only then to AI-backed agents. The course has three Nexus phases, each with multiple reference-backed goals. Daily sessions should usually pair a theoretical reading with a practical exercise and tests.

The course should preserve this order:

1. Understand Jido's OTP mapping.
2. Build immutable agents and pure actions.
3. Compose workflows with action chains.
4. Add signals, directives, and runtime supervision.
5. Package reusable capabilities as plugins.
6. Build orchestration, planning, memory, RAG, and AI/tool workflows.
7. Finish with a supervised research-and-execution capstone.

## Phases

1. `foundations` — Setup, mental model, agents, actions, workflows, signals, directives, and `AgentServer`
2. `advanced` — Plugins, FSMs, planning, parent-child orchestration, sensors, AI agents, tools, chat, memory, RAG, testing, and production readiness
3. `capstone` — Supervised research-and-execution agent system

## Goals

### Foundations

1. Core mental model and agent data
2. Actions and deterministic workflows
3. Signals, directives, and supervised runtime

### Advanced

1. Plugins and reusable capabilities
2. Planning, FSMs, and orchestration
3. AI agents, memory, RAG, and production readiness

### Capstone

1. Design the research-and-execution system
2. Build and harden the research-and-execution system

## Resources

- Jido: https://jido.run/
- Jido docs: https://jido.run/docs
- Jido concepts: https://jido.run/docs/concepts
- Jido learn tutorials: https://jido.run/docs/learn
- Source course brief: `.mem/docs/jido_course.md`
