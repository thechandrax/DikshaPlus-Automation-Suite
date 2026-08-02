# 📱 TERMUX_INFO.md — COMPLETE TERMUX MOBILE SETUP & WORKFLOW GUIDE

---

## 📌 OVERVIEW

**DIKSHA+ Automation Suite** is 100% compatible with **Android Termux**. You can run the entire automation engine directly on your smartphone using native Termux ARM64 Chromium and Python 3.

---

## ⚡ FAST PRE-COMPILED ARM64 BINARIES (`python-playwright` & `python-pandas`)

In Termux on Android ARM64, Playwright and Pandas are installed as pre-compiled binary packages directly via Termux package manager:
`pkg install python-playwright python-pandas python-pillow -y`.

---

## 🚀 2-STEP TERMUX INSTALLATION & LAUNCH WORKFLOW

### 1️⃣ STEP 1: Install Termux Repositories, Pre-Compiled Playwright & Python 3

Open the **Termux app** on your Android phone and paste this exact command block:

```bash
# 1. Enable x11-repo and tur-repo FIRST (required for Chromium & Playwright)
pkg update -y && pkg upgrade -y
pkg install x11-repo tur-repo -y
pkg update -y

# 2. Install Git, Python 3, Node.js, Chromium, python-playwright & python-pandas
pkg install git python nodejs-lts chromium python-playwright python-pandas python-pillow -y

# 3. Install pure Python libraries (instant 2-second install)
pip install openpyxl
```

---

### 2️⃣ STEP 2: Clone Repository & Launch DIKSHA+ (`run_diksha.sh`)

After Step 1 finishes, copy and paste this command block:

```bash
# 1. Clone repository from GitHub
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git

# 2. Enter project folder (Exact folder name: DikshaPlus-Automation-Suite)
cd DikshaPlus-Automation-Suite

# 3. Direct launch DIKSHA+!
chmod +x run_diksha.sh
./run_diksha.sh
```

---

## 🔄 HOW TO UPDATE CODE WHEN NEW COMMITS ARE PUSHED

If new updates or commits are pushed to GitHub:

```bash
cd DikshaPlus-Automation-Suite
git reset --hard origin/main
git pull origin main
./run_diksha.sh
```

---

## 📋 INTERACTIVE USER & COURSE SELECTION MENU IN TERMUX

When `./run_diksha.sh` runs in Termux, it displays the interactive CLI selection menu:

```text
===================================================================
 ⚡ DIKSHA+ AUTOMATION SUITE
===================================================================
🔒 Enter 6-digit Security Access PIN: 541563
✅ [PIN VERIFIED] Access Granted!

[Login] Registered accounts:
  [1] Sumanta Halder           : 7044015007
  [2] Chandra                  : 7001XXXXXX
  [3] Stephen Rodgroz          : 9830XXXXXX
-------------------------------------------------------------------
Select account [1-3] (or press Enter for Account #1): 1
```

1. Enter Security PIN: `541563`.
2. Select User Profile (e.g. Account #1 Sumanta Halder `7044015007`).
3. Select target enrolled course.

---

## 📊 4-WAY EXECUTION COMPARISON MATRIX

| Mode | Platform | System Role | Interface | Phone Battery Impact | Laptop Code Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode 1** | 💻 **Laptop** | Local Desktop Run | Visible GUI Window | N/A | **100% Preserved** ✅ |
| **Mode 2** | ☁️ **Railway Cloud** | Automated Server Backend | Headless Container | None (Cloud Engine) | **100% Preserved** ✅ |
| **Mode 3** | ☁️ **Railway Cloud** | Mobile Remote Control | Phone Web Browser | **0% Drain** 🔋 | **100% Preserved** ✅ |
| **Mode 4** | 📱 **Termux App** | Native Mobile Run | Android Terminal | Uses Phone Battery 🔋 | **100% Supported** ✅ |
