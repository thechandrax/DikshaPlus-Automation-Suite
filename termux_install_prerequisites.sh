#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# STEP 1: Termux Prerequisites & Dependencies Installer
# Run this FIRST on your Android phone inside Termux before cloning!
# ==============================================================================

echo "========================================================================"
echo " 📱 STEP 1: ENABLING TERMUX REPOSITORIES & PRE-COMPILED BINARIES"
echo "========================================================================"
echo ""

# 1. Update Termux Packages & Enable Repositories FIRST
echo "[1/3] Updating Termux repositories & enabling x11-repo + tur-repo..."
pkg update -y && pkg upgrade -y
pkg install x11-repo tur-repo -y
pkg update -y

# 2. Install Git, Python 3, Node.js, Chromium & Pre-compiled ARM64 Packages (Playwright, Pandas, Pillow)
echo "[2/3] Installing Git, Python 3, Chromium, python-playwright, python-pandas & python-pillow..."
pkg install git python nodejs-lts chromium python-playwright python-pandas python-pillow -y

echo ""
echo "========================================================================"
echo " 🐍 [3/3] INSTALLING PURE PYTHON PACKAGES (OpenPyXL)"
echo "========================================================================"
echo ""

pip install openpyxl

echo ""
echo "========================================================================"
echo " ✅ STEP 1 COMPLETE! Playwright, Pandas, Chromium & Python 3 ready!"
echo "------------------------------------------------------------------------"
echo " git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git"
echo " cd DikshaPlus-Automation-Suite"
echo " chmod +x run_diksha.sh"
echo " ./run_diksha.sh"
echo "========================================================================"
