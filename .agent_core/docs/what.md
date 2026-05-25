# What Is This Project?

## Purpose

Nexus is a personal system for structured learning and self-improvement. It exists because maintaining consistent progress across multiple learning tracks (programming languages, frameworks) and personal goals (exercise, reading) is hard without accountability and structure. Nexus solves this by combining a CLI tool with a self-documenting file system that an AI agent (OpenClaw, via Telegram) can read and act on autonomously.

The key insight is that between sessions, agents lose all context. The file system — doc.md files, records, state, and config — must fully inform any agent waking up cold about what's happening, what was last worked on, and what to do next.

## Goals

- **Daily learning exercises**: An OpenClaw agent wakes up via cron, reads the current topic and recent activity, and composes a daily exercise (10-20 min most days, up to 2 hours twice a week). Incomplete tasks carry over.
- **Weighted topic rotation**: Learning topics (rust, python, c, elixir, js-ts) rotate weekly based on configurable weights, so higher-priority topics get proportionally more weeks.
- **Self-improvement tracking**: Exercise sessions (4x/week) and reading sessions (5x/week) are tracked via the CLI and reported against goals.
- **Agent-friendly architecture**: Everything the agent needs is on disk. The CLI provides structured commands (`nexus topic`, `nexus record`, `nexus self`) so the agent doesn't need to understand file internals — it just uses the tool.
- **Long-term**: The agent learns to gauge ability over time based on reported task durations and feedback, adjusting difficulty and scope accordingly.

## Target Users / Consumers

Two consumers:

1. **Benjamin** — interacts via Telegram (through OpenClaw) and occasionally directly via the `nexus` CLI. Initiates self-improvement logs directly. Completes learning exercises and reports back.
2. **OpenClaw agent** — wakes up daily via cron to compose exercises, tracks completion, reminds about incomplete tasks. Uses the `nexus` CLI and reads the file system (doc.md, records/) to build context each session.

## Core Value Proposition

A self-documenting file system and CLI that lets a stateless AI agent maintain continuity across sessions to drive daily learning and self-improvement.

## Current State

Early-stage, actively being built. What exists so far:

- **Directory structure**: `learn/` with subdirectories per topic (c, elixir, js-ts, python, python/jax, rust), `self-improvement/` with weekly logs and book tracking
- **CLI foundation**: Typer app scaffolded with `nexus topic` command group (topic selection, reset, history, weights display). Uses `config.toml` for weights/settings and `state.toml` for mutable state.
- **Topic selection algorithm**: Proportional weighted selection with sliding window — ported from a prior Rust implementation, improved to handle weight changes gracefully.

What remains:

- `main.py` entrypoint wiring up the typer app
- `nexus record` command for logging learning sessions
- Self-improvement commands (`nexus self log`, `nexus self status`)
- Populating `doc.md` files with the schema agents need to orient themselves
- OpenClaw skill definition (SKILL.md)
- End-to-end testing
