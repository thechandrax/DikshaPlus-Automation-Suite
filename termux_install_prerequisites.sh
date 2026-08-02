#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# STEP 1: Termux Prerequisites & Dependencies Installer
# Run this FIRST on your Android phone inside Termux before cloning!
# ==============================================================================

echo "========================================================================"
echo " 📱 STEP 1: INSTALLING TERMUX SYSTEM PACKAGES & PYTHON 3"
echo "========================================================================"
echo ""

# 1. Update Termux Packages
echo "[1/2] Updating Termux package repository..."
pkg update -y && pkg upgrade -y

# 2. Install Git, Python 3, Node.js, Chromium & System Libraries
echo "[2/2] Installing Git, Python 3, Node.js, Chromium & tur-repo..."
pkg install git python nodejs-lts chromium x11-repo tur-repo -y

echo ""
echo "========================================================================"
echo " 🐍 INSTALLING PYTHON LIBRARIES (Playwright, Pandas, Pillow)"
echo "========================================================================"
echo ""

pip install pandas openpyxl pillow playwright

echo ""
echo "========================================================================"
echo " ✅ STEP 1 COMPLETE! You can now clone & run Step 2 setup:"
echo "------------------------------------------------------------------------"
echo " git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git"
echo " cd DikshaPlus-Automation-Suite"
echo " chmod +x termux_setup.sh"
echo " ./termux_setup.sh"
echo "========================================================================"
