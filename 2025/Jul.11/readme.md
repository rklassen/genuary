# Genuary 2025 - July 11

A minimal Rust application with a modular structure.

## Project Structure

```
/
├── Cargo.toml              # Project configuration
├── .gitignore              # Git ignore file
└── src/
    ├── main.rs             # Main binary entry point
    └── models/             # Subfolder for structs and types
        ├── mod.rs          # Module declaration file
        └── point.rs        # Example struct file
```

## Features

- Demonstrates Rust module organization
- Contains a simple `Point` struct with utility methods
- Shows how to use modules in a single-binary application

## Running the Project

```bash
# Build and run the project
cargo run

# Check for compile errors without producing an executable
cargo check

# Build in release mode
cargo build --release
```

## Development

This project is structured to allow easy expansion by adding more data structures to the `models` directory. Each new struct should have its own file and be exported through the `models/mod.rs` file.

july11.bpy - correct locations, can't
