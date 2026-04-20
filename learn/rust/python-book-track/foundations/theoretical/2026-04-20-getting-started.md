# Theoretical: Match, Borrowing, and Ownership

## Rust Enums with Data

Unlike Python's `Enum`, Rust enums can carry data in each variant:

```rust
enum Message {
    Quit,                           // No data
    Move { x: i32, y: i32 },        // Named fields (like a struct)
    Write(String),                  // Single unnamed field
    ChangeColor(u8, u8, u8),        // Multiple unnamed fields
}
```

This is more powerful than Python's `Enum` — variants are like different structs under one name.

## Exhaustive Pattern Matching with `match`

The `match` expression requires you to handle **every** possible variant:

```rust
fn handle_message(msg: Message) {
    match msg {
        Message::Quit => println!("Quitting"),
        Message::Move { x, y } => println!("Move to ({}, {})", x, y),
        Message::Write(text) => println!("Text: {}", text),
        Message::ChangeColor(r, g, b) => println!("RGB({}, {}, {})", r, g, b),
    }  // Compiler verifies all variants are covered
}
```

**The `_` wildcard:**
```rust
match value {
    1 => "one",
    2 => "two",
    _ => "other",  // Matches anything else
}
```

**If you remove any arm, the code won't compile.** This prevents bugs from unhandled cases.

## Borrowing: `&T` vs `T`

```rust
fn print_value(val: &String) {      // Borrows val (read-only)
    println!("{}", val);
}  // val is still valid after this call

fn consume_value(val: String) {     // Takes ownership (moves val)
    println!("{}", val);
}  // val is dropped here, caller can't use it anymore

fn main() {
    let s = String::from("hello");
    
    print_value(&s);    // s is borrowed, still valid
    print_value(&s);    // Can borrow again
    
    consume_value(s);   // s is MOVED into the function
    // println!("{}", s); // ❌ Compile error: value moved
}
```

## Mutable Borrowing: `&mut T`

```rust
fn append_log(log: &mut Vec<String>, entry: String) {
    log.push(entry);    // Modifies through the reference
}

fn main() {
    let mut log = Vec::new();
    
    append_log(&mut log, "entry 1".to_string());
    append_log(&mut log, "entry 2".to_string());
    
    println!("{:?}", log);  // ["entry 1", "entry 2"]
}
```

**Rules:**
- Only ONE `&mut` borrow at a time per value
- Can't have `&mut T` and `&T` simultaneously
- The borrow checker enforces this at compile time

## Move Semantics by Default

In Rust, assigning a value to a new variable **moves** ownership:

```rust
let s1 = String::from("hello");
let s2 = s1;  // s1 is MOVED to s2

// println!("{}", s1);  // ❌ Error: use of moved value
println!("{}", s2);     // ✅ s2 owns the string
```

**To keep using the original, borrow instead:**
```rust
let s1 = String::from("hello");
let s2 = &s1;  // s2 borrows from s1

println!("{}", s1);  // ✅ s1 still valid
println!("{}", s2);  // ✅ s2 is a reference
```

## Quick Reference: Python vs Rust

| Python | Rust | Notes |
|--------|------|-------|
| `match` (3.10+) | `match` | Rust's is exhaustive and expression-based |
| `None` | `Option<T>` | Rust forces you to handle the None case |
| `def f(x)` (always by reference) | `fn f(x: &T)` | Explicit borrowing |
| `def f(x)` (can mutate) | `fn f(x: &mut T)` | Explicit mutable borrow |
| Everything mutable | `let` = immutable, `let mut` = mutable | Default immutability |

## Exercise Checklist

For the CLI parser exercise, you'll need:
1. Define `enum Command` with variants carrying different data
2. Use `match` on strings to parse commands
3. Write `fn execute(cmd: &Command, log: &mut Vec<String>)` demonstrating both borrow types
4. In `main`, show the difference between borrowing (`&cmd`) and moving (`cmd`)

---
**Time estimate:** 10-15 minutes reading, then apply to practical exercise
