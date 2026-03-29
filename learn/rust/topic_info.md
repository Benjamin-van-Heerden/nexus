# Rust

## Background

Benjamin has built a small CLI tool in Rust (topic rotation for the nexus learning system), but is still a novice. He has extensive Python experience and is proficient in functional programming, so concepts like ownership, immutability, and pattern matching should map well — but the borrow checker, lifetimes, and Rust's type system are still unfamiliar territory.

## End Goal

Become proficient in async Rust — from language fundamentals through to writing production-quality async code. This means understanding ownership and borrowing deeply enough that async patterns (futures, pinning, Send/Sync bounds) make intuitive sense rather than being fought against.

## Learning Approach

Two-track curriculum using Microsoft's RustTraining material:
1. **python-book track** — Rust fundamentals through the lens of a Python developer. Covers types, ownership, traits, error handling, concurrency, and a capstone project.
2. **async-book track** (planned) — Deep dive into async Rust: futures, executors, pinning, streams, and production patterns.

The python-book track comes first to build solid foundations. The async track builds on top once ownership, traits, and concurrency basics are solid.

## Reference Material

- `reference/python-book/` — Rust for Python Developers (17 chapters, foundations through capstone)
- `reference/async-book/` — Async Rust deep dive (16 chapters, futures through production patterns)
