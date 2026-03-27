---
title: relative-paths-and-resolve
created_at: '2026-03-27T14:40:52.440680'
updated_at: '2026-03-27T14:40:52.440680'
---
All paths stored in nexus TOML files and references must be relative to the project root or relative to the file they appear in. Never store absolute paths. The CLI provides 'nexus resolve-path <relative-path>' which resolves any relative path to an absolute path on the current machine. Agents should use this command to discover actual file locations and to replace relative paths with absolute paths in output shown to the user. This ensures nexus works identically across different machines.