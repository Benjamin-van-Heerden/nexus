# Control Flow Theory: Rust vs Python

## 1. The Expression Mindset

In Python, `if` is a statement (mostly). In Rust, `if` is an **expression** that returns a value.

```python
# Python - assignment happens INSIDE the if
if temperature > 100:
    status = "hot"
else:
    status = "ok"
# Or using ternary (limited)
status = "hot" if temperature > 100 else "ok"
```

```rust
// Rust - if IS the value
let status = if temperature > 100 { "hot" } else { "ok" };
```

**Key insight:** The last expression in a block (without semicolon!) becomes the block's value.

## 2. The Semicolon Rule

```rust
let x = {
    let a = 5;
    let b = 10;
    a + b  // No semicolon → THIS IS THE VALUE (returns 15)
};

let y = {
    let a = 5;
    let b = 10;
    a + b;  // WITH semicolon → returns () (unit type, like None)
};
```

**Mental model:** Semicolon = "discard this value." No semicolon on last line = "return this value."

## 3. Loop Variants

| Python | Rust | Notes |
|--------|------|-------|
| `for i in range(5)` | `for i in 0..5` | Half-open: 0,1,2,3,4 |
| `range(1, 6)` | `1..=5` | Inclusive: 1,2,3,4,5 |
| `while True` | `loop { }` | `loop` is the idiomatic infinite loop |
| `break` | `break` or `break value` | Rust loops can return values! |

## 4. loop as Expression

```rust
let result = loop {
    let input = get_user_input();
    if let Ok(num) = input.parse::<i32>() {
        break num;  // break WITH a value!
    }
    println!("Invalid, try again");
};
// result now holds the parsed number
```

## 5. Pattern Matching with match

```rust
let grade = match score {
    90..=100 => "A",
    80..89   => "B",  // Note: 80..89 is WRONG (exclusive), use 80..=89
    70..=79  => "C",
    _        => "F",  // _ is catch-all (like else)
};
```

## 6. Iterator Chains vs List Comprehensions

```python
# Python - eager list comprehension
evens = [x for x in range(100) if x % 2 == 0]
```

```rust
// Rust - lazy iterator chain
let evens: Vec<i32> = (0..100).filter(|x| x % 2 == 0).collect();
// Nothing happens until .collect() forces evaluation
```

## Check Your Understanding

1. What does this return? `let x = { 5; };` → x - 5
2. What's the difference between `0..5` and `0..=5`? → exclusive vs inclusive
3. Can a `while` loop return a value with `break`? → in python no, in rust, yes
4. How do you check if a string is empty in an `if` condition? → if let Some(val) = expression
