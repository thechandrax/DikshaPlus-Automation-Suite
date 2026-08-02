#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Auto-install pure Python Playwright wheel for Termux if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing Playwright Python wheel for Termux..."
    pip install --no-deps "https://files.pythonhosted.org/packages/py3/p/playwright/playwright-1.50.0-py3-none-any.whl" 2>/dev/null || pip install --no-deps playwright
}

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
