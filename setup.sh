#!/usr/bin/env bash
set -euo pipefail

echo "=== Nexus Setup ==="
echo ""

# --- uv (Python package manager) ---
if command -v uv &> /dev/null; then
    echo "[ok] uv is installed: $(uv --version)"
else
    echo "[installing] uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "[ok] uv installed"
fi

# --- Rust + Cargo ---
if command -v rustc &> /dev/null; then
    echo "[ok] rust is installed: $(rustc --version)"
else
    echo "[installing] rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # Source cargo env for current session
    . "$HOME/.cargo/env"
    echo "[ok] rust installed: $(rustc --version)"
fi

echo ""
echo "=== Setup complete ==="
