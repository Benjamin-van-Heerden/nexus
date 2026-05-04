# Jido 06: Directives and Side-Effect Boundaries

## Goal

Return side-effect descriptions from actions without performing effects inline.

## Concepts

Directives are data structures that describe effects. The runtime executes them after `cmd/2` completes.

Core directive types include:

- `Emit`
- `Schedule`
- `Cron` and `CronCancel`
- `SpawnAgent`
- `StopChild`
- `Spawn`
- `RunInstruction`
- `Stop`
- `Error`

This keeps actions deterministic and testable. Tests can assert the directive struct without depending on real dispatch, timers, child processes, or external systems.

## Build target

Extend order confirmation:

- `ConfirmOrder` sets `status: :confirmed`.
- It creates an `order.confirmed` signal with `order_id` and `total`.
- It returns an `Emit` directive instead of dispatching inline.

## Exercises

1. Return a list of directives: emit a signal and schedule a timeout check.
2. Write tests that assert directive structs.
3. Create a custom directive struct.
4. Sketch its `DirectiveExec` protocol implementation.

## Checkpoint questions

- Why are directives not just callbacks?
- Which effects should remain outside actions?
- What does the runtime need to execute a directive safely?
