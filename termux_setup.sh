#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# STEP 2: Termux Environment Configurator & Engine Launcher
# Run this SECOND inside the cloned DikshaPlus-Automation-Suite folder!
# ==============================================================================

echo "========================================================================"
echo " 📱 STEP 2: CONFIGURING TERMUX CHROMIUM & LAUNCHING DIKSHA+"
echo "========================================================================"
echo ""

# 1. Pull Latest GitHub Commits
echo "[1/3] Checking for latest GitHub updates (git pull)..."
git pull origin main --quiet || true

# 2. Export Termux Chromium Environment Variables
echo "[2/3] Exporting Playwright Termux ARM64 Chromium environment paths..."
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

echo "[3/3] Chromium path verified: $(which chromium)"

echo ""
echo "========================================================================"
echo " 🚀 LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
