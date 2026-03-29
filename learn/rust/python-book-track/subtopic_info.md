# Rust for Python Developers

## What are we learning?

Rust fundamentals through the Microsoft RustTraining python-book curriculum. The book is structured for developers coming from Python — it draws parallels between Python and Rust concepts throughout, making the transition intuitive.

## Why are we learning this?

This is the foundation track for the broader goal of becoming proficient in async Rust. Ownership, borrowing, traits, and error handling need to be solid before tackling futures and pinning. The capstone project (CLI task manager) provides a practical integration point.

## How will we learn?

Follow the book chapter by chapter. Each chapter maps to a goal. Practical exercises are the core — small Rust programs that implement and test the concepts. The reference material lives in `reference/python-book/src/` at the topic level. Exercises live in each phase's `practical/` directory as cargo projects with an `examples/` directory for dated exercise files.

## Phases

1. **foundations** — Types, variables, control flow, data structures, enums, pattern matching (ch01-ch06)
2. **core-concepts** — Ownership, borrowing, modules, error handling, traits, generics, closures, iterators (ch07-ch12)
3. **advanced-topics** — Concurrency, unsafe Rust, FFI, migration patterns, best practices (ch13-ch16)
4. **capstone** — CLI Task Manager project (ch17)

## Resources

- `reference/python-book/` — the full book source (markdown chapters)
