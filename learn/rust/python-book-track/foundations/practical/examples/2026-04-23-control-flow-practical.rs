// Control Flow Practical Exercises
// Run with: cargo run --example 2026-04-23-control-flow-practical

fn main() {
    // === Exercise 1: if as expression ===
    // Convert this Python to Rust:
    // temperature = 75
    // status = "hot" if temperature > 80 else "comfortable" if temperature > 60 else "cold"
    
    let temperature = 75;
    let status = // Your code here
    
    println!("Temperature: {}°F - Status: {}", temperature, status);
    
    // === Exercise 2: loop with return value ===
    // Create a loop that counts attempts and returns the first even number found
    // Hint: use break with a value
    
    let numbers = [3, 7, 9, 4, 12, 15];
    let (first_even, attempts) = // Your code here
        // loop through numbers, track attempts, return (first_even, attempt_count)
    };
    
    println!("First even: {} (found after {} checks)", first_even, attempts);
    
    // === Exercise 3: Range mastery ===
    // Print numbers 1 through 10 (inclusive) using the correct range syntax
    print!("1 to 10: ");
    for i in // Your code here
        print!("{} ", i);
    }
    println!();
    
    // Print even numbers 0, 2, 4, 6, 8 using step_by
    print!("Even numbers: ");
    for i in // Your code here
        print!("{} ", i);
    }
    println!();
    
    // === Exercise 4: Block expressions ===
    // Create a block that calculates the area of a rectangle
    // and returns it as the value of a variable
    
    let width = 10;
    let height = 5;
    let area = // Your code here
        // calculate and return width * height
    };
    
    println!("Area: {} (expected: 50)", area);
    
    // === Exercise 5: match for categorization ===
    // Classify a number as "small" (<10), "medium" (10-100), or "large" (>100)
    
    let value = 42;
    let category = // Your code here
    
    println!("{} is {}", value, category);
    
    // === Exercise 6: Iterator chain ===
    // Use filter and map to create a vector of squares of odd numbers from 0..20
    // Expected: [1, 9, 25, 49, 81, 121, 169, 225, 289, 361]
    
    let odd_squares: Vec<i32> = // Your code here
        // hint: (0..20).filter(...).map(...).collect()
    
    println!("Odd squares: {:?}", odd_squares);
    
    // === Exercise 7: Challenge - fizzbuzz ===
    // Print numbers 1-15, but:
    // - "Fizz" if divisible by 3
    // - "Buzz" if divisible by 5
    // - "FizzBuzz" if both
    // - the number otherwise
    
    println!("\nFizzBuzz:");
    for n in 1..=15 {
        // Your code here
        // Hint: use match with guards (if conditions)
    }
}

// === BONUS: Fix the errors ===
// Uncomment and fix each line

// fn fix_me() {
//     let x = 42;
//     if x {  // What's wrong here?
//         println!("true");
//     }
//     
//     let y = {
//         let a = 5;
//         a + 10;  // What's wrong here if we want y to be 15?
//     };
// }
