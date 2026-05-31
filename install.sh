#!/usr/bin/env bash
# bedrock-code installer for Linux / macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/AditHash/Bedrock-coder/main/install.sh | bash
# Or locally: bash install.sh
set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; GRAY='\033[0;90m'; NC='\033[0m'
step() { echo -e "\n${CYAN}[$1]${NC} $2"; }
ok()   { echo -e "  ${GREEN}OK${NC}  $1"; }
info() { echo -e "  ${GRAY}     $1${NC}"; }
fail() { echo -e "  ${RED}ERR${NC} $1"; exit 1; }

echo ""
echo -e "${CYAN}  bedrock-code installer${NC}"
echo -e "${CYAN}  ----------------------${NC}"
echo ""

# ── Step 1: Python 3.11+ ────────────────────────────────────────────────────
step "1/4" "Checking Python"
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=${ver%%.*}; minor=${ver##*.}
        if [[ $major -ge 3 && $minor -ge 11 ]]; then
            PYTHON=$cmd; break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    fail "Python 3.11+ not found.\n  macOS: brew install python@3.12\n  Linux: sudo apt install python3.12"
fi
ok "$PYTHON $($PYTHON --version)"

# ── Step 2: uv ──────────────────────────────────────────────────────────────
step "2/4" "Checking uv"
if ! command -v uv &>/dev/null; then
    info "uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    ok "uv installed"
else
    ok "$(uv --version)"
fi

# ── Step 3: Install bc as a uv tool ─────────────────────────────────────────
step "3/4" "Installing bedrock-code"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "Source: $REPO_DIR"
info "Running: uv tool install -e ."

(cd "$REPO_DIR" && uv tool install -e . --force)
ok "bedrock-code installed"

# ── Step 4: PATH ─────────────────────────────────────────────────────────────
step "4/4" "Verifying"
UV_BIN="$HOME/.local/bin"
export PATH="$UV_BIN:$PATH"

SHELL_RC=""
case "$SHELL" in
    */zsh)  SHELL_RC="$HOME/.zshrc" ;;
    */bash) SHELL_RC="$HOME/.bashrc" ;;
    *)      SHELL_RC="$HOME/.profile" ;;
esac

if ! grep -q 'HOME/.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo '' >> "$SHELL_RC"
    echo '# bedrock-code (uv tools)' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    info "Added ~/.local/bin to PATH in $SHELL_RC"
fi

if command -v bc &>/dev/null; then
    ok "bc is available at $(command -v bc)"
else
    echo ""
    echo -e "  ${YELLOW}NOTE:${NC} Run 'source $SHELL_RC' or open a new terminal, then run bc"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}Installation complete!${NC}"
echo ""
echo "  Next steps:"
echo "    1.  aws login          (if not already logged in)"
echo "    2.  bc                 (setup wizard runs automatically)"
echo "    3.  bc setup           (re-run wizard anytime)"
echo ""
