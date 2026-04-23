// Control Flow Practical Exercises
// Run with: cargo run --example 2026-04-23-control-flow-practical

fn main() {
    // === Exercise 1: if as expression ===
    // Convert this Python to Rust:
    // temperature = 75
    // status = "hot" if temperature > 80 else "comfortable" if temperature > 60 else "cold"

    let temperature = 75;
    let status = if temperature > 80 {
        "hot"
    } else {
        if temperature > 60 {
            "comfortable"
        } else {
            "cold"
        }
    };

    println!("Temperature: {}°F - Status: {}", temperature, status);

    // === Exercise 2: loop with return value ===
    // Create a loop that counts attempts and returns the first even number found
    // Hint: use break with a value

    let numbers = [3, 7, 9, 4, 12, 15];
    let (first_even, attempts) = {
        let mut attempts = 0;
        let first_even: Option<i32> = loop {
            if attempts < numbers.len() {
                if numbers[attempts] % 2 == 0 {
                    break Some(numbers[attempts]);
                }
            } else {
                break None;
            }
            attempts += 1;
        };
        (first_even, attempts)
    };

    println!(
        "First even: {:?} (found after {} checks)",
        first_even, attempts
    );

    // === Exercise 3: Range mastery ===
    // Print numbers 1 through 10 (inclusive) using the correct range syntax
    print!("1 to 10: ");
    for i in 1..=10 {
        print!("{} ", i);
    }
    println!();

    // Print even numbers 0, 2, 4, 6, 8 using step_by
    print!("Even numbers: ");
    for i in (0..=10).step_by(2) {
        print!("{} ", i);
    }
    println!();

    // === Exercise 4: Block expressions ===
    // Create a block that calculates the area of a rectangle
    // and returns it as the value of a variable

    let width = 10;
    let height = 5;
    let area = { width * height };

    println!("Area: {} (expected: 50)", area);

    // === Exercise 5: match for categorization ===
    // Classify a number as "small" (<10), "medium" (10-100), or "large" (>100)

    let value = 42;
    let category = match value {
        value if value < 10 => "small",
        value if value < 100 => "medium",
        _ => "large",
    };

    println!("{} is {}", value, category);

    // === Exercise 6: Iterator chain ===
    // Use filter and map to create a vector of squares of odd numbers from 0..20
    // Expected: [1, 9, 25, 49, 81, 121, 169, 225, 289, 361]

    let odd_squares: Vec<i32> = (0..20).filter(|x| x % 2 == 1).map(|x| x * x).collect();
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
        match n {
            n if n % 5 == 0 && n % 3 == 0 => println!("FizzBuzz"),
            n if n % 5 == 0 => println!("Buzz"),
            n if n % 3 == 0 => println!("Fizz"),
            _ => println!("{}", n),
        }
    }
}

// === BONUS: Fix the errors ===
// Uncomment and fix each line

fn _fix_me() {
    let x = 42;
    if x == 42 {
        // What's wrong here?
        println!("true");
    }

    let y = {
        let a = 5;
        a + 10 // What's wrong here if we want y to be 15?
    };
    println!("{}", y);
}
