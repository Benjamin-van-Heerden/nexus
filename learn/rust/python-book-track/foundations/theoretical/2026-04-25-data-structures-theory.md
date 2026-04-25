# Data Structures and Collections: Rust vs Python

## 1. Tuples and Destructuring

**Python:**
```python
point = (3.0, 4.0)
x, y = point                    # Unpacking
print(f"x={x}, y={y}")

# Named access
record = ("Alice", 30, True)
name, age, active = record
first = record[0]               # Bracket indexing
```

**Rust:**
```rust
let point: (f64, f64) = (3.0, 4.0);
let (x, y) = point;              // Destructuring

// Mixed types ok
let record: (&str, i32, bool) = ("Alice", 30, true);
let (name, age, active) = record;

// Access by INDEX using DOT syntax
let first = record.0;            // "Alice" — note: .0 not [0]
let second = record.1;           // 30
```

> ⚠️ **Common gotcha:** Rust uses `.0`, `.1` for tuple access, NOT `[0]`, `[1]`!

---

## 2. Arrays and Slices

**Arrays are FIXED size (stack-allocated):**
```rust
let numbers: [i32; 5] = [1, 2, 3, 4, 5]; // Type includes SIZE!
// numbers.push(6);  // ❌ Compile error — arrays can't grow

// Initialize all elements:
let zeros = [0; 10];            // [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

**Slices are VIEWS (no copy!):**
```rust
let data = [10, 20, 30, 40, 50];
let first_three = &data[..3];   // &[i32] — view of [10, 20, 30]

// Python: data[:3] creates a NEW list (copy)
// Rust:   &data[..3] creates a VIEW (no allocation, no copy)
```

---

## 3. Structs (Rust's Classes)

**Python dataclass:**
```python
from dataclasses import dataclass

@dataclass
class Rectangle:
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height
```

**Rust struct:**
```rust
#[derive(Debug, Clone)]
struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    // "Constructor" (associated function, no self)
    fn new(width: f64, height: f64) -> Self {
        Rectangle { width, height }  // Field shorthand
    }

    fn area(&self) -> f64 {
        self.width * self.height
    }
}

fn main() {
    let r = Rectangle::new(10.0, 5.0);
    println!("Area: {}", r.area());
}
```

**Key differences:**
- `#[derive(Debug)]` = Python's `__repr__`
- `impl std::fmt::Display` = Python's `__str__`
- No inheritance — use composition + traits

---

## 4. Vec<T> vs list

```rust
// Creating vectors
let numbers = vec![1, 2, 3];            // vec! macro
let empty: Vec<i32> = Vec::new();        // Empty (need type hint)
let repeated = vec![0; 10];              // [0, 0, 0, ...]
let from_range: Vec<i32> = (1..6).collect(); // [1, 2, 3, 4, 5]

// Common operations
let mut nums = vec![1, 2, 3];
nums.push(4);                          // Add to end
nums.pop();                            // Remove last, returns Option<T>
nums.insert(0, 0);                     // Insert at index
let len = nums.len();                  // Length
let contains = nums.contains(&3);      // Check membership
```

| Python | Rust | Notes |
|--------|------|-------|
| `lst.append(x)` | `vec.push(x)` | |
| `lst.pop()` | `vec.pop()` | Returns `Option<T>` (Some/None) |
| `lst[i]` | `vec[i]` | Panics if out of bounds! |
| `lst.get(i)` | `vec.get(i)` | Returns `Option<&T>` (safe) |
| `len(lst)` | `vec.len()` | |

---

## 5. HashMap<K, V> vs dict

```rust
use std::collections::HashMap;

let mut scores = HashMap::from([("Alice", 100), ("Bob", 85)]);

// Insert / update
scores.insert("Charlie", 90);          // Insert
scores.insert("Alice", 95);            // Overwrite

// Access
let val = scores["Alice"];              // Panics if missing!
let val = scores.get("Alice");          // Returns Option<&i32>
let val = scores.get("Alice").copied().unwrap_or(0); // Safe with default

// Check / remove
let exists = scores.contains_key("Alice");
scores.remove("Bob");

// Entry API (like defaultdict!)
let mut word_count: HashMap<&str, i32> = HashMap::new();
for word in words {
    *word_count.entry(word).or_insert(0) += 1;
}
```

---

## Quick Reference: Python → Rust

| Python | Rust |
|--------|------|
| `tuple` | `(T1, T2)` or struct |
| `list` | `Vec<T>` |
| `dict` | `HashMap<K, V>` |
| `set` | `HashSet<T>` |
| `__init__` | `fn new()` |
| `__str__` | `impl Display` |
| `__repr__` | `#[derive(Debug)]` |
| `self.method()` | `&self` or `&mut self` |

---

## Check Your Understanding

1. How do you access the 3rd element of a tuple in Rust? → _______
2. What's the difference between `[i32; 5]` and `Vec<i32>`? → _______
3. What does `vec.get(100)` return if the vec has 3 elements? → _______
4. What's the Rust equivalent of Python's `Counter(words)`? → _______
5. What does `#[derive(Debug)]` do? → _______
