---
title: relative-paths-and-resolve
created_at: '2026-03-27T14:40:52.440680'
updated_at: '2026-04-10T16:19:16.703110'
---
All paths stored in nexus TOML files use the ./ prefix, relative to the project root (e.g. ./learn/jax/reference/doc.md). This is the single, universal convention — no field-specific base directories. The CLI resolves these to absolute paths for display using src/utils/path_resolution.py. The to_stored_path() function converts any path to the ./ convention, and resolve()/resolve_str() convert stored paths to absolute paths. nexus resolve-path command is available for agents. CRITICAL: any time a path is displayed to an agent (in onboard output, refresh output, task listings, or instructions), it MUST be an absolute path. Agents run from their own workspace directories and cannot resolve relative paths. Never show ./ prefixed paths in agent-facing output.