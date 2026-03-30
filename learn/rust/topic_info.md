# Rust

## Background

Benjamin has built a small CLI tool in Rust (topic rotation for the nexus learning system), but is still a novice. He has extensive Python experience and is proficient in functional programming, so concepts like ownership, immutability, and pattern matching should map well — but the borrow checker, lifetimes, and Rust's type system are still unfamiliar territory.

## End Goal

Become proficient in Rust — from language fundamentals through async and into building real systems. This means understanding ownership and borrowing deeply enough that async patterns (futures, pinning, Send/Sync bounds) make intuitive sense, and then applying that knowledge to non-trivial projects.

## Learning Approach

Progressive curriculum:
1. **python-book track** — Rust fundamentals through the lens of a Python developer. Covers types, ownership, traits, error handling, concurrency, and a capstone project.
2. **async-book track** — Deep dive into async Rust: futures, executors, pinning, streams, and production patterns.
3. **bitcoin track** (future) — Build Bitcoin in Rust, based on a dedicated book. A CodeCrafters-style project applying systems-level Rust to a real protocol.
4. **sqlite track** (future) — Build SQLite in Rust, based on the CodeCrafters project. Exercises low-level I/O, parsing, and data structures.

The first two tracks build foundations and async fluency. The latter two are capstone-level projects that put it all together on real systems.

## Reference Material

- `./learn/rust/reference/python-book/` — Rust for Python Developers (17 chapters, foundations through capstone)
- `./learn/rust/reference/async-book/` — Async Rust deep dive (16 chapters, futures through production patterns)
