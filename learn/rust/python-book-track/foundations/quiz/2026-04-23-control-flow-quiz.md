# Control Flow Quiz

## Multiple Choice

**1. What is the value of `x`?**
```rust
let x = if true { 5 } else { 10 };
```
- A) `()` (unit type)
- B) `5` --> this
- C) `true`
- D) Compilation error

**2. What's wrong with this code?**
```rust
let items = vec![1, 2, 3];
if items {
    println!("has items");
}
```
- A) `vec![]` creates a fixed-size array, not a vector
- B) Rust requires `if items.len() > 0`
- C) Rust requires `if !items.is_empty()`
- D) Both B and C are valid fixes --> this

**3. What does `0..=5` produce?**
- A) 0, 1, 2, 3, 4 (exclusive of 5)
- B) 0, 1, 2, 3, 4, 5 (inclusive) --> this
- C) 1, 2, 3, 4, 5 (starts at 1)
- D) Compilation error

**4. Which loop type can return a value with `break`?**
- A) `for` loops only
- B) `while` loops only
- C) `loop` only --> this
- D) All of them

**5. What is the type of `result`?**
```rust
let result = {
    let x = 5;
    x + 10;
};
```
- A) `i32` with value 15
- B) `()` (unit type) --> this
- C) Compilation error
- D) `i32` with value 5

## Fill in the Blank

**6.** In Rust, the last expression in a block without a _______ (semicolon) becomes the block's value.

**7.** The idiomatic way to write an infinite loop in Rust is _______ (loop), not `while true`.

**8.** To make a range inclusive (include the end value), use _______ (..=) instead of `..`.

**9.** In Rust, conditions must be _______ (boolean) type — there's no truthy/falsy like in Python.

## Code Analysis

**10. What does this print?**
```rust
let nums = vec![2, 4, 6, 7, 8];
let result = nums.iter()
    .filter(|&&x| x % 2 == 0)
    .map(|x| x * 2)
    .collect::<Vec<_>>();
println!("{:?}", result);
```

It prints [4, 8, 12, 16], but explain to me the double &&

## Code Correction

**11. Fix this code:**
```rust
let score = 85;
let grade = match score {
    90..=100 => "A",
    80..90 => "B",
    70..80 => "C",
    _ => "F",
};
```

Fixed (I think)

**12. Fix this code:**
```rust
let first_positive = loop {
    for n in [-5, -3, 0, 4, 7] {
        if n > 0 {
            break n
        }
    }
};
```

Fixed (there was a semicolon after the break n)

---

## Answer Key (Don't peek until you're done!)

<details>
<summary>Click to reveal answers</summary>

1. **B) 5** — if is an expression that returns a value
2. **D) Both B and C** — Rust has no truthiness; must use explicit comparison
3. **B) 0, 1, 2, 3, 4, 5** — `..=` is inclusive range
4. **C) `loop` only** — `for` and `while` cannot return values with break
5. **B) `()`** — the semicolon makes it a statement, returning unit type
6. **semicolon** (or "semicolon ;")
7. **`loop`**
8. **`..=`** (or "double-dot-equals")
9. **bool** (or "boolean")
10. **`[4, 8, 12, 16]`** — filter keeps evens [2,4,6,8], map doubles them
11. Change ranges to inclusive: `90..=100`, `80..=89`, `70..=79` (or use guards)
12. The `break n` only breaks the inner `for`, not the outer `loop`. Fix:
    ```rust
    let nums = [-5, -3, 0, 4, 7];
    let first_positive = 'outer: loop {
        for n in nums {
            if n > 0 {
                break 'outer n;  // labeled break
            }
        }
        break -1; // handle case where no positive found
    };
    ```

</details>
