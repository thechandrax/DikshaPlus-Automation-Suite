#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Auto-install Playwright ARM64 for Termux if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing Playwright ARM64 wheel into Termux site-packages..."
    SP_PATH=$(python -c "import site; print(site.getsitepackages()[0])")
    pip install --no-deps --platform manylinux2014_aarch64 --only-binary=:all: --target "$SP_PATH" playwright
}

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
