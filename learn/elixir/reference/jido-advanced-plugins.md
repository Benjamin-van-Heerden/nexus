# Jido Advanced: Plugins and Reusable Capabilities

## Goal

Learn when and how to package shared capabilities as plugins instead of duplicating actions and state across agents.

## Concepts

Plugins reduce duplication when multiple agents share a capability. A plugin can provide:

- Actions.
- A state slice under `state_key`.
- Signal routes.
- Signal interception through `handle_signal/2`.
- Lifecycle hooks such as `mount/2`, `child_spec/1`, `transform_result/3`, checkpoint, and restore.
- Schedules.

Good plugin candidates include:

- Notes.
- Identity.
- Thread history.
- Memory spaces.
- Shared audit/event capture.
- Common tool sets.

## Build Target

Build a notes plugin:

- `AddNote`
- `ClearNotes`
- `ListNotes`
- `NotesPlugin` with `state_key: :notes`
- Routes for `notes.add`, `notes.clear`, and `notes.list`

Use the plugin in two agents:

- One default notes agent.
- One configured work-notes agent.

## Exercises

1. Build the notes plugin.
2. Add a plugin config schema.
3. Add signal routes for note operations.
4. Decide which plugin state should be kept, dropped, or externalized during checkpoint.
5. Add tests proving two agents using the same plugin do not accidentally share state.

## Checkpoint Questions

- When is a plugin better than a shared module?
- What belongs in plugin state?
- How should plugin state be namespaced?
- What lifecycle hooks does this plugin actually need?
