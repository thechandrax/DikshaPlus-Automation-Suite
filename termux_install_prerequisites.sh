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

# 2. Install Git, Python 3, Node.js, Chromium & Pre-compiled Python Packages (Fast Binary Install)
echo "[2/3] Installing Git, Python 3, Chromium, python-pandas & python-pillow..."
pkg install git python nodejs-lts chromium python-pandas python-pillow -y

echo ""
echo "========================================================================"
echo " 🐍 [3/3] INSTALLING PURE PYTHON PACKAGES (Playwright, OpenPyXL)"
echo "========================================================================"
echo ""

pip install openpyxl playwright

echo ""
echo "========================================================================"
echo " ✅ STEP 1 COMPLETE! Pre-compiled Pandas, Chromium & Python 3 ready!"
echo "------------------------------------------------------------------------"
echo " git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git"
echo " cd DikshaPlus-Automation-Suite"
echo " chmod +x termux_setup.sh"
echo " ./termux_setup.sh"
echo "========================================================================"
