# Jido 08: Plugins and Reusable Capabilities

## Goal

Package shared actions, state, routes, and lifecycle hooks into reusable plugins.

## Concepts

Plugins reduce duplication when multiple agents share a capability. A plugin can provide:

- Actions.
- A state slice under `state_key`.
- Signal routes.
- Signal interception through `handle_signal/2`.
- Lifecycle hooks such as `mount/2`, `child_spec/1`, `transform_result/3`, checkpoint, and restore.
- Schedules.

Default plugin ideas include thread, identity, and memory capabilities.

## Build target

Build a notes plugin:

- `AddNote`
- `ClearNotes`
- `ListNotes`
- `NotesPlugin` with `state_key: :notes`
- Routes for `notes.add`, `notes.clear`, and `notes.list`

Use the plugin in two agents, one default and one configured for work notes.

## Exercises

1. Add `ListNotes`.
2. Add a plugin config schema.
3. Add a signal route for `notes.list`.
4. Decide which plugin state should be kept, dropped, or externalized during checkpoint.

## Checkpoint questions

- When is a plugin better than a shared module?
- What belongs in plugin state?
- How should plugin state be namespaced?
