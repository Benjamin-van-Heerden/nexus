# Jido Agent Framework

## What are we learning?

Jido as a BEAM-native agent framework for building deterministic, testable agent systems in Elixir. The course covers Jido agents, actions, signals, directives, supervised runtime execution, plugins, workflows, memory, AI agents, tool use, and production readiness.

## Why are we learning this?

Jido is interesting because it maps agent systems onto familiar Elixir/OTP ideas without reducing the problem to an LLM wrapper. Agents are schema-backed data, actions are validated transitions, signals are typed event envelopes, directives describe effects, and `Jido.AgentServer` supplies the OTP runtime boundary when lifecycle and concurrency are needed.

## How will we learn?

Work through the Jido stack from deterministic core primitives to runtime orchestration and only then to AI-backed agents. Each module is a Nexus phase with a reference-backed goal. Daily sessions should usually pair a theoretical reading with a practical exercise and tests.

The course should preserve this order:

1. Understand Jido's OTP mapping.
2. Build immutable agents and pure actions.
3. Compose workflows with action chains.
4. Add signals, directives, and runtime supervision.
5. Package reusable capabilities as plugins.
6. Build orchestration, planning, memory, RAG, and AI/tool workflows.
7. Finish with a supervised research-and-execution capstone.

## Phases

1. `module-01-setup-and-mental-model` — Setup, smoke test, and Jido's OTP mapping
2. `module-02-agents-as-immutable-data` — `Jido.Agent` as schema-backed state
3. `module-03-actions-as-validated-state-transitions` — `Jido.Action` and validation
4. `module-04-workflows-with-action-chains` — Composing actions into workflows
5. `module-05-signals-and-routing` — CloudEvents-style signals and routes
6. `module-06-directives-and-side-effect-boundaries` — Effects as data
7. `module-07-agentserver-and-supervised-runtime` — Runtime execution under OTP
8. `module-08-plugins-and-reusable-capabilities` — Shared state, actions, hooks, and routes
9. `module-09-fsms-planning-and-resumable-workflows` — Explicit state machines and task planning
10. `module-10-parent-child-sensors-and-orchestration` — Multi-agent coordination
11. `module-11-ai-agents-tools-chat-and-reasoning` — LLM agents after deterministic foundations
12. `module-12-memory-rag-production-readiness` — Memory, threads, RAG, persistence, testing, debugging
13. `capstone-research-execution-system` — Supervised research-and-execution agent system

## Resources

- Jido: https://jido.run/
- Jido docs: https://jido.run/docs
- Jido concepts: https://jido.run/docs/concepts
- Jido learn tutorials: https://jido.run/docs/learn
- Source course brief: `.mem/docs/jido_course.md`
