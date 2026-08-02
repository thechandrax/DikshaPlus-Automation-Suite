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

# 2. Install Git, Python 3, Node.js, Chromium & Pre-compiled ARM64 Packages
echo "[2/3] Installing Git, Python 3, Chromium, python-pandas & python-pillow..."
pkg install git python nodejs-lts chromium python-pandas python-pillow -y

# 3. Install Playwright ARM64 manylinux wheel
echo "[3/3] Installing Playwright for Termux ARM64..."
SP_PATH=$(python -c "import site; print(site.getsitepackages()[0])")
pip install --no-deps --platform manylinux2014_aarch64 --only-binary=:all: --target "$SP_PATH" playwright
pip install pyee greenlet openpyxl 2>/dev/null || true

echo ""
echo "========================================================================"
echo " ✅ STEP 1 COMPLETE! Playwright, Pandas, Chromium & Python 3 ready!"
echo "------------------------------------------------------------------------"
echo " git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git"
echo " cd DikshaPlus-Automation-Suite"
echo " chmod +x run_diksha.sh"
echo " ./run_diksha.sh"
echo "========================================================================"
