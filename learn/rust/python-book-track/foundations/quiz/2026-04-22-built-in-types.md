# Quiz: Built-in Types and Variables

Answer each question. Check your answers at the end.

---

## Question 1: Mutability

What is the output/error of this code?

```rust
let x = 10;
let x = x + 5;
let mut x = x * 2;
x = 100;
println!("{}", x);
```

**A)** Compile error on line 2 — cannot reassign immutable variable  
**B)** Compile error on line 4 — cannot reassign immutable variable  
**C)** 100 --> this 
**D)** 30  

---

## Question 2: String Types

You have this function:

```rust
fn process(s: &str) -> String {
    s.to_uppercase()
}
```

Which of these CANNOT be passed directly to `process()`?

**A)** `let x = "hello"; process(x);`  
**B)** `let x = String::from("hello"); process(&x);`  
**C)** `let x = String::from("hello"); process(x);`  
**D)** All of the above work --> this  

---

## Question 3: Type Inference

What is the inferred type of `x`?

```rust
let x = 42;
```

**A)** i64  
**B)** i32 --> this 
**C)** usize  
**D)** The compiler cannot infer — requires explicit type  

---

## Question 4: String Operations

Which operation returns a `&str` (no allocation)?

**A)** `"hello".to_uppercase()`  
**B)** `"  hello  ".trim()`  
**C)** `"hello".replace("l", "L")` --> this (I think) 
**D)** `format!("hello {}", "world")`  

---

## Question 5: Ownership and Borrowing

What error does this code produce?

```rust
fn main() {
    let s = String::from("hello");
    let slice = &s;
    s.push_str(" world");
    println!("{}", slice);
}
```

**A)** No error — compiles and runs  
**B)** Cannot borrow `s` as mutable because it is also borrowed as immutable --> something like this, but idk what would happen if you start with let mut s = ...  
**C)** Use of moved value: `s`  
**D)** Mismatched types  

---

## Question 6: Type Conversions

You need to index into a Vec with an `i32`. What must you do?

```rust
let vec = vec![1, 2, 3];
let i: i32 = 1;
// let item = vec[i];  // Error — how do you fix this?
```

**A)** `vec[i as i64]`  
**B)** `vec[i as usize]` --> this 
**C)** `vec[i32::from(i)]`  
**D)** Change `i` to `let i: usize = 1;`  

---

## Question 7: Fixed-Size Types

What happens with this code?

```rust
let x: u8 = 255;
let y = x + 1;
```

**A)** y equals 256  
**B)** Compile error — overflow  
**C)** Panic at runtime  
**D)** y wraps around to 0 (in release mode) --> this  

---

## Question 8: Function Design

You're designing a function that takes a name and returns a formatted greeting. What's the best signature?

**A)** `fn greet(name: String) -> String`  
**B)** `fn greet(name: &str) -> String` --> this  
**C)** `fn greet(name: String) -> &str`  
**D)** `fn greet(name: &str) -> &str`

---

# Answer Key

<details>
<summary>Click to reveal answers</summary>

**1. C (100)** — Variable shadowing creates a new binding each time. The final `x` is mutable and set to 100.

**2. C** — `process(x)` moves the String, but `process` expects `&str`. You'd need `&x` or `x.as_str()`.

**3. B (i32)** — The default integer type is i32 unless context suggests otherwise.

**4. B (trim)** — `.trim()` returns a slice of the original string, no allocation. The others create new Strings.

**5. B** — You can't have a mutable borrow (`s.push_str`) while an immutable borrow (`slice`) is active.

**6. B or D** — Both work. `as usize` casts, or changing the variable type to `usize`.

**7. D (in release mode) / B (in debug)** — In debug mode, Rust panics. In release, it wraps. The question notes "what happens" — best answer is D since it's common in production.

**8. B** — `&str` is most flexible for input (accepts both string types). `String` for output because format! creates a new String.

**Scoring:**
- 8/8: Excellent grasp of Rust's type system!
- 6-7: Solid understanding, review String/&str distinction
- 4-5: Review mutability and ownership rules
- 0-3: Re-read the chapter, focus on borrow checker fundamentals

</details>
