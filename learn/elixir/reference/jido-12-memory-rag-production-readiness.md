# Jido 12: Memory, RAG, and Production Readiness

## Goal

Understand memory, threads, RAG, persistence, testing, debugging, and production readiness.

## Memory layers

Jido provides complementary memory layers:

1. Structured memory in named spaces.
2. Thread logs as append-only interaction history.
3. Retrieval stores for recall over text documents.

Use structured memory for current facts and task state. Use thread logs for messages, tool calls, system events, and audit history. Use retrieval for grounding against larger document sets.

## Persistence and checkpointing

Plugin checkpoint strategies include:

- `:keep`
- `:drop`
- `{:externalize, key, pointer}`

Make memory and thread persistence explicit. Do not accidentally serialize transient or sensitive runtime state.

## Testing strategy

Test in layers:

1. Action unit tests.
2. Agent transition tests.
3. Signal routing tests.
4. Directive tests.
5. AI boundary tests without live providers.

## Production checklist

- Actions have schemas.
- Side effects are directives or isolated workers.
- Agents have clear IDs.
- Signal type naming is consistent.
- Runtime supervision is explicit.
- Error directives are handled.
- AI calls have timeouts, budgets, and model/provider configuration.
- Memory/persistence policy is explicit.
- Observability is wired before launch.

## Checkpoint questions

- Which memory should be durable?
- What belongs in a thread log?
- How can an AI test be useful without live model calls?
