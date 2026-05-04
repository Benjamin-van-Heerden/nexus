# Jido 11: AI Agents, Tools, Chat, and Reasoning Strategies

## Goal

Add LLM behaviour after understanding the deterministic core runtime.

## Concepts

`Jido.AI.Agent` adds LLM calls, tools, chat, and reasoning strategies on top of the same runtime ideas. Do not use the AI layer to hide unclear deterministic logic.

Every `Jido.Action` can double as an LLM tool. Its schema can become JSON Schema, and `jido_ai` can adapt actions into tool definitions. The important design point is that the LLM request does not execute tools inline; tool execution routes back through Jido's action/directive path.

## Build target

Build:

- A no-tool greeter agent.
- A support or weather agent with tool actions.
- A two-turn chat agent.
- A hybrid mode that changes request options for quick versus deep turns.

Keep live provider calls optional and isolated from core tests.

## Exercises

1. Build a no-tool greeter.
2. Build a weather or support tool-calling agent.
3. Build a two-turn chat agent.
4. Add a hybrid request mode for quick vs deep turns.
5. Inspect runtime snapshots after each turn.

## Checkpoint questions

- Why should tools be deterministic actions?
- Where do provider timeouts and budgets belong?
- When is deeper reasoning justified?
