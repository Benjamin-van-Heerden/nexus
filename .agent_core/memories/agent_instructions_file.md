---
title: agent-instructions-file
created_at: '2026-03-27T15:55:51.655078'
updated_at: '2026-03-27T15:55:51.655078'
---
Agent-facing instructions (commands, guidelines, workflow) for the nexus learn system live in src/commands/learn/agent_instructions.md. This file is read and appended to the onboard output. When commands change or new functionality is added, update this file as the central source of truth rather than hardcoding instructions in Python code. This pattern should be followed for any future app (e.g. self-improvement) — each app gets its own agent_instructions.md.