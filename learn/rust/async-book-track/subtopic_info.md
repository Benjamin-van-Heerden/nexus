# Async Rust Deep Dive

## What are we learning?

Async Rust from first principles: how futures work under the hood (the Future trait, Poll, Pin), how executors and runtimes are built, Tokio in depth, and production async patterns. This is not a surface-level "how to use async/await" tutorial — it builds a mental model of the machinery underneath.

## Why are we learning this?

Async is where Rust's ownership model gets genuinely hard. Understanding futures as state machines, why Pin exists, and how Send/Sync interact with async code is essential for writing production Rust. This track builds on the foundations from the python-book track (ownership, traits, generics) and applies them to the async domain.

## How will we learn?

Follow the async-book chapter by chapter. The book is structured in three parts that build progressively: first understand the primitives (Future, Poll, Pin), then the ecosystem (executors, Tokio), then production concerns (streams, pitfalls, patterns). Practical exercises are the core — async code needs to be written and debugged to internalize the concepts. The capstone is an async chat server.

## Phases

1. **how-async-works** — Future trait, Poll, Pin/Unpin, state machine desugaring (ch01-ch05)
2. **ecosystem** — Building futures by hand, executors and runtimes, Tokio deep dive, alternative runtimes, async traits (ch06-ch10)
3. **production** — Streams, common pitfalls, production patterns, exercises (ch11-ch14)
4. **capstone** — Async chat server project (ch16)

## Resources

- `./learn/rust/reference/async-book/` — the full book source (markdown chapters)
- Tokio documentation: https://tokio.rs/
- Rust async book (official): https://rust-lang.github.io/async-book/
