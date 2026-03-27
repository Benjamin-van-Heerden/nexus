---
title: relative-paths-and-resolve
created_at: '2026-03-27T14:40:52.440680'
updated_at: '2026-03-27T14:46:34.236171'
---
All paths stored in nexus TOML files and references must be relative to the project root. Never store absolute paths. The CLI provides 'nexus resolve-path <relative-path>' which resolves any relative path to an absolute path on the current machine. Agents should use this command to discover actual file locations. Anywhere a path is printed by the nexus app it must be resolved to an absolute path, for which functionality is provided in src/utils/path_resolution.py. This ensures nexus works identically across different machines.