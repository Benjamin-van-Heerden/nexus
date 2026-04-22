// Practical: String Manipulation and Type Safety
//
// This exercise builds on the theoretical reading about String vs &str,
// mutability, and Rust's type system.
//
// Your task: Implement a text processing utility that demonstrates
// proper use of String and &str types.

// TODO 1: Implement this function
// Takes a name (&str) and returns a greeting (String)
// Format: "Hello, {name}! Welcome to Rust."
// Hint: format!() macro returns a String
fn greet(name: &str) -> String {
    todo!("Implement greeting")
}

// TODO 2: Implement this function
// Takes a mutable String reference and appends "!!!" to it
// This demonstrates &mut String
fn emphasize(msg: &mut String) {
    todo!("Append \"!!!\" to msg");
}

// TODO 3: Implement this function
// Takes a string slice (&str) and returns the first word
// A word is defined as characters before the first space
// If no space, return the entire string
// Hint: Use the .find() method on str, and string slicing
fn first_word(s: &str) -> &str {
    todo!("Extract first word from s")
}

// TODO 4: Implement this function
// Takes a string slice and returns a Vec of words
// Words are separated by whitespace
// Hint: Use .split_whitespace() and .collect()
fn words(s: &str) -> Vec<&str> {
    todo!("Split s into words")
}

// TODO 5: Implement this function
// Takes a temperature in Celsius (f64) and returns Fahrenheit
// Formula: F = C * 9.0/5.0 + 32.0
// Note: Must use f64 for floating-point math
fn c_to_f(celsius: f64) -> f64 {
    todo!("Convert Celsius to Fahrenheit")
}

// TODO 6: Implement this function
// Takes a temperature in Fahrenheit and classifies it
// Returns &str (string slice) based on:
//   < 32   → "freezing"
//   32-50  → "cold"
//   50-77  → "mild"
//   77-95  → "warm"
//   >= 95  → "hot"
// Hint: if/else chains in Rust are expressions (return values)
fn classify_temp(fahrenheit: f64) -> &'static str {
    todo!("Classify temperature")
}

fn main() {
    // Test your implementations here
    
    // Test greet()
    let name = "Benjamin";
    let greeting = greet(name);
    println!("{}", greeting);
    // greeting is a String (owned), name is still valid (&str borrow ended)
    
    // Test emphasize()
    let mut msg = String::from("Hello");
    emphasize(&mut msg);
    println!("{}", msg);  // Should print "Hello!!!"
    
    // Test first_word()
    let sentence = "Hello world from Rust";
    let word = first_word(sentence);
    println!("First word: {}", word);  // Should print "Hello"
    
    // Test words()
    let all_words = words(sentence);
    println!("Words: {:?}", all_words);  // Should print ["Hello", "world", "from", "Rust"]
    
    // Test temperature conversion
    for c in [0.0, 10.0, 20.0, 30.0, 40.0] {
        let f = c_to_f(c);
        let classification = classify_temp(f);
        println!("{:.1}°C = {:.1}°F — {}", c, f, classification);
    }
    
    // BONUS: Try uncommenting these lines to see compile errors:
    // let s = "immutable";
    // s.push_str(" string");  // What error do you get?
    
    // let mut owned = String::from("owned");
    // let slice = &owned;  // Borrow
    // owned.push_str(" string");  // Can we modify while borrowed?
}

// COMPILER ERROR CHALLENGE:
// After implementing everything, try these in main() and fix the errors:
//
// 1. let s: String = "hello";  // Type mismatch — how do you create a String from &str?
// 2. let mut x = 5; x = "five";  // Type error — can Rust variables change type?
// 3. fn bad(s: String) -> &str { &s }  // What lifetime error do you get?
