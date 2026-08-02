#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Auto-install pure Python Playwright for Termux ARM64 if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing pure Python Playwright package..."
    pip install --no-deps playwright
    pip install pyee greenlet 2>/dev/null || true
}

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
