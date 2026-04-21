// Practical Exercise: Type Safety and Performance
//
// This exercise demonstrates two key Rust advantages over Python:
// 1. Compile-time type checking (no runtime surprises)
// 2. Performance without sacrificing safety
//
// Your task: Make this file compile, then observe the performance difference
// between debug and release builds.

use std::iter::Sum;
use std::ops::Mul;
use std::time::Instant;

// TODO 1: `square` takes an i32 and returns its square.
// Leave this signature alone for now — it's the *caller* that has to adapt.
fn square_dumb(n: i32) -> i32 {
    n * n
}

fn square_smart<T: Mul<Output = T> + Copy>(n: T) -> T {
    n * n
}

// TODO 2: This should calculate the sum of squares from 1 to n.
// As written, it will NOT compile. Two things to figure out:
//   (a) `square(i)` — `i` is i64, `square` wants i32. How do you reconcile?
//   (b) Once you fix (a), think: for n = 10_000_000, what is i*i at the top
//       of the range? Does it fit in i32? What does Rust do in debug vs
//       release when an i32 multiplication overflows? Try both and see.
//
// You have a few options — pick one and justify it to yourself:
//   - Cast `i` down to i32 before calling square (dangerous — why?)
//   - Change `square` to take i64 (but TODO 4 wants an f64 version too…)
//   - Make `square` generic over numeric types (stretch goal — needs a
//     trait bound like `std::ops::Mul<Output = T> + Copy`)
fn sum_of_squares<T>(items: impl IntoIterator<Item = T>) -> T
where
    T: Mul<Output = T> + Copy + Sum<T>,
{
    items.into_iter().map(square_smart).sum()
}

fn square_f64(n: f64) -> f64 {
    n * n
}

fn main() {
    let n = 10_000_000;

    let start = Instant::now();
    let result = sum_of_squares(1i128..n);
    let elapsed = start.elapsed();

    println!("Sum of squares from 1 to {} = {}", n, result);
    println!("Time elapsed: {:?}", elapsed);

    // BONUS: Run with `cargo run --release` vs `cargo run`.
    // Record both times. The gap should be dramatic — why?
    // (Hint: in debug, the compiler also inserts overflow checks.)

    // --- Type safety demonstration ---
    println!("\n--- Type Safety Check ---");

    let x = 5i32;
    let y = square_dumb(x);
    println!("square({}) = {}", x, y);

    // TODO 3: Leave this line uncommented. It WILL fail to compile.
    // Read the error carefully — this is the kind of bug Python only
    // catches at runtime (or silently coerces and gives you a float
    // when you expected an int). What exactly does rustc tell you,
    // and what would Python have done with `square(3.14)`?
    // let z = square(3.14);
    // println!("square(3.14) = {}", z);

    // TODO 4: Write a `square_f64` function (above `main`) that squares
    // an f64, and call it here with 3.14. Why does Rust make you write
    // a whole second function instead of reusing `square`? What bugs
    // does Python's implicit numeric coercion enable that Rust prevents?
    let z = square_f64(3.14);
    println!("square({}) = {}", 3.14, z);
}
