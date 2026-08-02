#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
