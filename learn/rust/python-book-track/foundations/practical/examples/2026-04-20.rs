// Practical Exercise: Type Safety and Performance
// 
// This exercise demonstrates two key Rust advantages over Python:
// 1. Compile-time type checking (no runtime surprises)
// 2. Performance without sacrificing safety
//
// Your task: Fix the compilation errors and observe the performance difference.

use std::time::Instant;

// TODO 1: Fix the type error in this function
// The function should accept an integer and return its square
// Hint: In Rust, types are explicit and enforced at compile time
fn square(n: i32) -> i32 {
    n * n
}

// TODO 2: This function calculates the sum of squares from 1 to n
// It currently has a type mismatch - fix it
fn sum_of_squares(n: i64) -> i64 {
    let mut sum = 0;
    for i in 1..=n {
        // TODO 3: The square() function takes i32, but we're passing i64
        // How do you handle this in Rust? (Hint: types must match exactly)
        sum += (i as i32 * i as i32) as i64;
    }
    sum
}

fn main() {
    // Performance comparison section
    let n = 10_000_000;
    
    let start = Instant::now();
    let result = sum_of_squares(n);
    let elapsed = start.elapsed();
    
    println!("Sum of squares from 1 to {} = {}", n, result);
    println!("Time elapsed: {:?}", elapsed);
    
    // BONUS: Try running with `cargo run --release` vs `cargo run`
    // The --release flag enables optimizations. What's the performance difference?
    
    // Type safety demonstration
    println!("\n--- Type Safety Check ---");
    
    let x = 5i32;
    let y = square(x);
    println!("square({}) = {}", x, y);
    
    // TODO 4 (uncomment to see the error):
    // let z = square(3.14);  // This should fail - why?
    // println!("square(3.14) = {}", z);
    
    // TODO 5: Create a version that works with f64
    // Add a square_f64() function above and call it here
}

// TODO 5 solution space:
// fn square_f64(n: f64) -> f64 {
//     n * n
// }
