#!/usr/bin/env bash
# Render build script for a Python + Vue (Vite) monorepo.
# Render's Python web service image ships without Node.js, so we load nvm
# (which IS pre-installed) and pin Node 20 LTS before running the SPA build.
set -euo pipefail

# ── 1. Python dependencies ──────────────────────────────────────────────────
echo ">>> Installing Python dependencies..."
pip install -r requirements.txt

# ── 2. Node.js via nvm ─────────────────────────────────────────────────────
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [ -s "$NVM_DIR/nvm.sh" ]; then
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
else
    echo ">>> nvm not found — installing nvm..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
fi

echo ">>> Installing Node.js 20 LTS..."
nvm install 20
nvm use 20
echo "Node: $(node --version)  npm: $(npm --version)"

# ── 3. Vue SPA build ────────────────────────────────────────────────────────
echo ">>> Installing JS dependencies..."
npm install

echo ">>> Building Vue SPA..."
npm run build

# ── 4. Sanity check ─────────────────────────────────────────────────────────
echo "=== dist/ contents ==="
ls -la dist/

if [ ! -f dist/index.html ]; then
    echo "ERROR: dist/index.html was not produced — build failed!"
    exit 1
fi

echo ">>> Build complete. dist/index.html exists."
