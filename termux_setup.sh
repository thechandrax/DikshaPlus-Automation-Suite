#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ Automation Suite - 1-Click Termux Mobile Installer & Launcher
# ==============================================================================

echo "========================================================================"
echo " 📱 DIKSHA+ AUTOMATION SUITE - TERMUX MOBILE SETUP"
echo "========================================================================"
echo ""

# 1. Update Termux Packages
echo "[1/4] Updating Termux packages..."
pkg update -y && pkg upgrade -y

# 2. Install Git, Python, Node.js, Chromium & Dependencies
echo "[2/4] Installing Git, Python, Chromium, & system libraries..."
pkg install git python nodejs-lts chromium x11-repo tur-repo -y


# 3. Install Required Python Packages
echo "[3/4] Installing Python requirements..."
pip install pandas openpyxl pillow playwright

# 4. Export Termux Environment Variables
echo "[4/4] Setting Termux environment variables..."
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

echo ""
echo "========================================================================"
echo " ✅ TERMUX SETUP COMPLETE! Starting DIKSHA+ Engine..."
echo "========================================================================"
echo ""

python main.py
