#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Auto-install Playwright via tur-repo or TUR PyPI wheel if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing Playwright for Termux ARM64..."
    pkg install tur-repo -y && pkg update -y
    pkg install python-playwright -y 2>/dev/null || pip install --extra-index-url https://termux-user-repository.github.io/pypi/ playwright
}

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
