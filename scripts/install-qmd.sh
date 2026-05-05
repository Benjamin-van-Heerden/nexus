#!/usr/bin/env bash
set -euo pipefail

QMD_VERSION="2.1.0"
NODE_MIN_MAJOR="22"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK_ONLY=0
SETUP_ARCHIVE=0
WARMUP=0

usage() {
    cat <<EOF
Usage: scripts/install-qmd.sh [--check-only] [--setup-archive] [--warmup]

Installs and verifies QMD for nexus archive.

Pinned versions:
  QMD_VERSION=${QMD_VERSION}
  NODE_MIN_MAJOR=${NODE_MIN_MAJOR}

Options:
  --check-only      Verify prerequisites without installing anything.
  --setup-archive  Run nexus archive setup after QMD is installed.
  --warmup         Run qmd embed and a small query to populate model caches.
  -h, --help       Show this help.

Deployment note:
  Persist ~/.cache/qmd. QMD stores its SQLite index and downloaded GGUF models
  there, and first-run model downloads can be large.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check-only)
            CHECK_ONLY=1
            ;;
        --setup-archive)
            SETUP_ARCHIVE=1
            ;;
        --warmup)
            WARMUP=1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 2
            ;;
    esac
    shift
done

echo "=== Nexus archive QMD bootstrap ==="
echo "QMD_VERSION=${QMD_VERSION}"
echo ""

if ! command -v node >/dev/null 2>&1; then
    echo "[error] node is not installed. QMD requires Node.js >= ${NODE_MIN_MAJOR}." >&2
    exit 1
fi

node_version="$(node --version)"
node_major="${node_version#v}"
node_major="${node_major%%.*}"
if (( node_major < NODE_MIN_MAJOR )); then
    echo "[error] node ${node_version} is too old. QMD requires Node.js >= ${NODE_MIN_MAJOR}." >&2
    exit 1
fi
echo "[ok] node ${node_version}"

if [[ "$(uname -s)" == "Darwin" ]]; then
    if command -v brew >/dev/null 2>&1 && brew --prefix sqlite >/dev/null 2>&1; then
        echo "[ok] Homebrew SQLite: $(brew --prefix sqlite)"
    else
        echo "[error] macOS deployments need Homebrew SQLite for QMD sqlite-vec support." >&2
        echo "        Install with: brew install sqlite" >&2
        exit 1
    fi
fi

install_qmd() {
    if command -v npm >/dev/null 2>&1; then
        npm install -g "@tobilu/qmd@${QMD_VERSION}"
        return
    fi
    if command -v bun >/dev/null 2>&1; then
        bun install -g "@tobilu/qmd@${QMD_VERSION}"
        return
    fi
    echo "[error] neither npm nor bun is installed; cannot install QMD." >&2
    exit 1
}

current_qmd_version=""
if command -v qmd >/dev/null 2>&1; then
    current_qmd_version="$(qmd --version | awk '{print $2}')"
fi

if [[ "${current_qmd_version}" == "${QMD_VERSION}" ]]; then
    echo "[ok] qmd ${current_qmd_version}"
else
    if [[ "${CHECK_ONLY}" == "1" ]]; then
        if [[ -z "${current_qmd_version}" ]]; then
            echo "[error] qmd is not installed; expected ${QMD_VERSION}." >&2
        else
            echo "[error] qmd ${current_qmd_version} installed; expected ${QMD_VERSION}." >&2
        fi
        exit 1
    fi

    if [[ -z "${current_qmd_version}" ]]; then
        echo "[installing] qmd ${QMD_VERSION}"
    else
        echo "[installing] replacing qmd ${current_qmd_version} with ${QMD_VERSION}"
    fi
    install_qmd
    echo "[ok] $(qmd --version)"
fi

echo "[info] QMD cache: ${HOME}/.cache/qmd"
echo "[info] Persist this directory in deployment for indexes and downloaded models."

if [[ "${SETUP_ARCHIVE}" == "1" ]]; then
    echo ""
    echo "[setup] registering nexus archive with QMD"
    "${PROJECT_DIR}/scripts/nexus" archive setup
fi

if [[ "${WARMUP}" == "1" ]]; then
    echo ""
    echo "[warmup] embedding registered QMD collections"
    qmd embed
    echo "[warmup] running a small query to initialize query/rerank models"
    qmd query "nexus archive warmup" -c nexus-archive --json -n 1 >/dev/null || true
fi

echo ""
echo "=== QMD bootstrap complete ==="
