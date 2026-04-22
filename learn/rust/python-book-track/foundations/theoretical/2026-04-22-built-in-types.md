# Theoretical: Built-in Types and Variables

## Part 1: Variable Mutability

Read the following code snippets and answer the questions below.

```rust
// Snippet A
let x = 5;
x = 10;  // What happens here?

// Snippet B
let mut y = 5;
y = 10;  // What happens here?

// Snippet C (variable shadowing)
let z = "hello";
let z = z.len();  // What type is z now?
```

**Questions:**
1. Why does Snippet A fail to compile? What error message would you expect?
2. What does `mut` signify in Rust that differs from Python's default behavior?
3. In Snippet C, how many distinct variables named `z` exist? What happened to the first one?

---

## Part 2: Numeric Types

Python has arbitrary-precision integers (`int`). Rust has fixed-size types.

```rust
let a: i32 = 42;        // 32-bit signed
let b: u64 = 100;       // 64-bit unsigned
let c = 3.14;           // What type is inferred?
let d: f32 = 2.5;       // Explicit 32-bit float
let e: usize = 0;       // What does usize represent?
```

**Questions:**
1. Why can't you assign a negative value to a `u32` variable? What error would you get?
2. When would you use `usize` instead of `i32` for indexing?
3. What happens if you compute `2_i32.pow(31)`? Why?

---

## Part 3: String Types — The Critical Distinction

This is the most important concept in this chapter. Rust has two string types where Python has one.

```rust
// &str (string slice)
let name: &str = "Alice";  // Borrowed, immutable, fixed-size

// String (owned)
let mut greeting = String::from("Hello");  // Owned, mutable, growable
greeting.push_str(", Alice!");
```

**Key Differences:**

| Aspect | `&str` | `String` |
|--------|--------|----------|
| Ownership | Borrowed (reference) | Owned |
| Mutability | Always immutable | Mutable if binding is `mut` |
| Storage | Usually in binary or borrowed from String | Heap-allocated |
| Size | Fixed at compile time (known length) | Dynamic (can grow/shrink) |
| Use in functions | `fn greet(name: &str)` — preferred | `fn create() -> String` — when returning |

**Questions:**
1. Why does `fn greet(name: &str)` accept both `&str` AND `&String`? (Hint: Deref coercion)
2. You have a `String` and need to pass it to a function expecting `&str`. What do you do?
3. You need to modify a string (push characters, concatenate). Which type must you use?
4. What's the difference between `"hello".to_string()` and `String::from("hello")`?

---

## Part 4: Type Inference vs Dynamic Typing

**Python (dynamic):**
```python
x = 42        # int
x = "hello"   # Now it's str — same variable, new type
```

**Rust (inferred but static):**
```rust
let x = 42;        // Compiler infers i32
// x = "hello";    // Error: expected integer, found &str

let y = 3.14;      // Compiler infers f64
let z = "hello";   // Compiler infers &str
```

**Question:** In Rust, types are inferred at compile time but can never change. Why is this design choice important for memory safety?

---

## Reflection

Write 2-3 sentences about which concept (mutability, numeric types, or String/&str distinction) will require the most mental adjustment coming from Python, and why.
