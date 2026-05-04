# Jido Advanced: AI Agents, Memory, RAG, and Production Readiness

## Goal

Add LLM behaviour after the deterministic core is clear, then make the system testable and production-ready.

## AI Agents and Tools

`Jido.AI.Agent` adds LLM calls, tools, chat, and reasoning strategies on top of the same runtime ideas. Do not use the AI layer to hide unclear deterministic logic.

Every `Jido.Action` can double as an LLM tool. Its schema can become JSON Schema, and `jido_ai` can adapt actions into tool definitions. The important design point is that the LLM request does not execute tools inline; tool execution routes back through Jido's action/directive path.

Build:

- A no-tool greeter agent.
- A support or weather agent with tool actions.
- A two-turn chat agent.
- A hybrid mode that changes request options for quick versus deep turns.

Keep live provider calls optional and isolated from core tests.

## Memory Layers

Jido provides complementary memory layers:

1. Structured memory in named spaces.
2. Thread logs as append-only interaction history.
3. Retrieval stores for recall over text documents.

Use structured memory for current facts and task state. Use thread logs for messages, tool calls, system events, and audit history. Use retrieval for grounding against larger document sets.

## Persistence and Checkpointing

Plugin checkpoint strategies include:

- `:keep`
- `:drop`
- `{:externalize, key, pointer}`

Make memory and thread persistence explicit. Do not accidentally serialize transient or sensitive runtime state.

## Testing and Production Checklist

Test in layers:

1. Action unit tests.
2. Agent transition tests.
3. Signal routing tests.
4. Directive tests.
5. AI boundary tests without live providers.

Before production:

- Actions have schemas.
- Side effects are directives or isolated workers.
- Agents have clear IDs.
- Signal type naming is consistent.
- Runtime supervision is explicit.
- Error directives are handled.
- AI calls have timeouts, budgets, and model/provider configuration.
- Memory/persistence policy is explicit.
- Observability is wired before launch.

## Exercises

1. Build a no-tool greeter.
2. Build a tool-calling agent whose tools are deterministic actions.
3. Build a two-turn chat agent.
4. Add hybrid quick/deep request modes.
5. Add structured memory and a thread log.
6. Add a simple retrieval store or retrieval adapter.
7. Write tests that avoid live LLM calls.

## Checkpoint Questions

- Why should tools be deterministic actions?
- Which memory should be durable?
- What belongs in a thread log?
- How can an AI test be useful without live model calls?
