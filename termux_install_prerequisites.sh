#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# STEP 1: Termux Prerequisites & Dependencies Installer
# Run this FIRST on your Android phone inside Termux before cloning!
# ==============================================================================

echo "========================================================================"
echo " 📱 STEP 1: ENABLING TERMUX REPOSITORIES (X11 & TUR REPO)"
echo "========================================================================"
echo ""

# 1. Update Termux Packages & Enable Repositories FIRST
echo "[1/3] Updating Termux repositories & enabling x11-repo + tur-repo..."
pkg update -y && pkg upgrade -y
pkg install x11-repo tur-repo -y
pkg update -y

# 2. Install Git, Python 3, Node.js & Chromium
echo "[2/3] Installing Git, Python 3, Node.js & Chromium..."
pkg install git python nodejs-lts chromium -y

echo ""
echo "========================================================================"
echo " 🐍 [3/3] INSTALLING PYTHON LIBRARIES (Playwright, Pandas, Pillow)"
echo "========================================================================"
echo ""

pip install pandas openpyxl pillow playwright

echo ""
echo "========================================================================"
echo " ✅ STEP 1 COMPLETE! Chromium & Python 3 installed successfully!"
echo "------------------------------------------------------------------------"
echo " git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git"
echo " cd DikshaPlus-Automation-Suite"
echo " chmod +x termux_setup.sh"
echo " ./termux_setup.sh"
echo "========================================================================"
