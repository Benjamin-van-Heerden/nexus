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

#[derive(Debug)]
enum Command {
    Help,
    Version,
    Run { script: String, verbose: bool },
    Unknown(String),
}

// TODO 2: Implement a function to parse a command string into our enum
// Signature: fn parse_command(input: &str) -> Command
// Use match with string patterns:
//   "help" or "--help" or "-h" => Help
//   "version" or "--version" or "-v" => Version
//   "run" or starts with "run " => parse the rest, extract script name and --verbose flag
//   anything else => Unknown(input.to_string())

fn parse_command(input: &str) -> Command {
    let tokens: Vec<&str> = input.split_whitespace().collect();
    match tokens.as_slice() {
        ["help"] | ["--help"] | ["-h"] => Command::Help,
        ["version"] | ["--version"] | ["-v"] => Command::Version,
        ["run", rest @ ..] if !rest.is_empty() => {
            let verbose = rest.contains(&"--verbose");
            let script = rest
                .iter()
                .filter(|&&t| t != "--verbose")
                .copied()
                .collect::<Vec<_>>()
                .join(" ");
            Command::Run { script, verbose }
        }
        _ => Command::Unknown(input.to_string()),
    }
}

// TODO 3: Implement a function to "execute" a command
// Signature: fn execute(cmd: &Command, log: &mut Vec<String>) -> String
// This demonstrates borrowing (reading cmd without ownership) and mutable borrowing (adding to log)
// Return a response string for each variant:
//   Help => "Usage: cli [help|version|run <script> [--verbose]]"
//   Version => "v0.1.0"
//   Run { script, verbose } => format with verbose indicator if set
//   Unknown(s) => format!("Unknown command: {}", s)
// Also push an entry to log: format!("Executed: {:?} at {:?}", cmd, std::time::Instant::now())
fn execute(cmd: &Command, log: &mut Vec<String>) -> String {
    let out = match cmd {
        Command::Help => String::from("Usage: cli [help|version|run <script> [--verbose]]"),
        Command::Version => String::from("v0.1.0"),
        Command::Run { script, verbose } => format!("script:{} verbose:{}", script, verbose),
        Command::Unknown(s) => format!("{}", s),
    };
    log.push(format!(
        "Executed: {:?} at {:?}",
        cmd,
        std::time::Instant::now()
    ));
    out
}

// TODO 4: In main, demonstrate move semantics
// Create a Command::Run with a String, then:
// - Pass it to execute() by reference (&)
// - Try to use the command variable again after execute()
// - Then demonstrate what happens if you pass by value (move)
//
// Expected learning: &T borrows without taking ownership, T moves ownership

fn main() {
    let command = Command::Run {
        script: String::from("rm -rf /"),
        verbose: true,
    };
    let mut log: Vec<String> = vec![];
    println!("{}", execute(&command, &mut log));
    println!("{}", log.len());

    // TODO 5: Test your implementation
    // Parse and execute several commands, demonstrating:
    // - Exhaustive match handling all variants
    // - Borrowing (&Command) vs moving (Command)
    // - Mutable state via &mut Vec<String>
    let a1 = parse_command("--help");
    println!("{}", execute(&a1, &mut log));
    println!("{}", log.len());
    let a2 = parse_command("run ls -la --verbose");
    println!("{}", execute(&a2, &mut log));
    println!("{}", log.len());
}

// HINT: The match expression is exhaustive - the compiler will error if you miss a variant!
// Try removing one arm to see the error message.

// BONUS: Add a Command::Quit variant. What breaks? Fix all the match expressions.
