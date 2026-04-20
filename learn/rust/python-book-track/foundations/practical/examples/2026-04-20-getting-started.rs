// Getting Started: Tooling, Match, and Ownership
//
// This exercise focuses on what matters for a Python developer transitioning to Rust:
// - Exhaustive pattern matching with match
// - Borrowing (&) and mutable borrowing (&mut)
// - The move semantics (implicit ownership transfer)
//
// Your task: Implement a simple CLI argument parser that demonstrates these concepts.

// TODO 1: Define an enum for CLI commands
// Commands: Help, Version, Run { script: String, verbose: bool }, Unknown(String)
// Hint: Variants can carry data, making enums more powerful than Python's Enum

// TODO 2: Implement a function to parse a command string into our enum
// Signature: fn parse_command(input: &str) -> Command
// Use match with string patterns:
//   "help" or "--help" or "-h" => Help
//   "version" or "--version" or "-v" => Version  
//   "run" or starts with "run " => parse the rest, extract script name and --verbose flag
//   anything else => Unknown(input.to_string())

// TODO 3: Implement a function to "execute" a command
// Signature: fn execute(cmd: &Command, log: &mut Vec<String>) -> String
// This demonstrates borrowing (reading cmd without ownership) and mutable borrowing (adding to log)
// Return a response string for each variant:
//   Help => "Usage: cli [help|version|run <script> [--verbose]]"
//   Version => "v0.1.0"
//   Run { script, verbose } => format with verbose indicator if set
//   Unknown(s) => format!("Unknown command: {}", s)
// Also push an entry to log: format!("Executed: {:?} at {:?}", cmd, std::time::Instant::now())

// TODO 4: In main, demonstrate move semantics
// Create a Command::Run with a String, then:
// - Pass it to execute() by reference (&)
// - Try to use the command variable again after execute()
// - Then demonstrate what happens if you pass by value (move)
//
// Expected learning: &T borrows without taking ownership, T moves ownership

fn main() {
    // TODO 5: Test your implementation
    // Parse and execute several commands, demonstrating:
    // - Exhaustive match handling all variants
    // - Borrowing (&Command) vs moving (Command)
    // - Mutable state via &mut Vec<String>
    
    println!("TODO: Implement the CLI parser exercise");
}

// HINT: The match expression is exhaustive - the compiler will error if you miss a variant!
// Try removing one arm to see the error message.

// BONUS: Add a Command::Quit variant. What breaks? Fix all the match expressions.
