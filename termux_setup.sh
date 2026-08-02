#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# STEP 2: Termux Environment Configurator & Engine Launcher
# Run this SECOND inside the cloned DikshaPlus-Automation-Suite folder!
# ==============================================================================

echo "========================================================================"
echo " 📱 STEP 2: CONFIGURING TERMUX CHROMIUM & LAUNCHING DIKSHA+"
echo "========================================================================"
echo ""

# 1. Export Termux Chromium Environment Variables
echo "[1/2] Exporting Playwright Termux ARM64 Chromium environment paths..."
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

echo "[2/2] Chromium path verified: $(which chromium)"
echo ""
echo "========================================================================"
echo " 🚀 LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
