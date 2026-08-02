#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Auto-install Playwright ARM64 manylinux wheel for Termux if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing Playwright ARM64 wheel for Termux..."
    pip install --no-deps --platform manylinux2014_aarch64 --only-binary=:all: playwright 2>/dev/null || pip install --no-deps --platform manylinux_2_17_aarch64 --only-binary=:all: playwright
}

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
