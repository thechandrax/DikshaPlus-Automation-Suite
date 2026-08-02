# 📱 TERMUX_INFO.md — COMPLETE TERMUX MOBILE SETUP & WORKFLOW GUIDE

---

## 📌 OVERVIEW

**DIKSHA+ Automation Suite** is 100% compatible with **Android Termux**. You can run the entire automation engine directly on your smartphone using native Termux ARM64 Chromium and Python 3.

---

## 🐍 PYTHON VERSION REQUIREMENT

* **Python 3 REQUIRED** (`pkg install python` in Termux automatically installs Python 3.10+ / 3.11+ / 3.12+).
* **Python 2** is obsolete and **will NOT work** with Playwright, Pandas, or AI solver libraries.

---

## 🚀 2-STEP TERMUX INSTALLATION & LAUNCH WORKFLOW

### 1️⃣ STEP 1: Install Termux System Packages & Python 3 Libraries

Open the **Termux app** on your Android phone and paste this exact command block:

```bash
# 1. Update Termux repositories & install Git, Python 3, Node.js, Chromium
pkg update -y && pkg upgrade -y
pkg install git python nodejs-lts chromium x11-repo tur-repo -y

# 2. Install Python 3 libraries
pip install pandas openpyxl pillow playwright
```

---

### 2️⃣ STEP 2: Clone Repository & Launch DIKSHA+ (`termux_setup.sh`)

After Step 1 finishes, copy and paste this command block:

```bash
# 1. Clone repository from GitHub
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git

# 2. Enter project folder (Exact folder name: DikshaPlus-Automation-Suite)
cd DikshaPlus-Automation-Suite

# 3. Make launcher script executable & run
chmod +x termux_setup.sh
./termux_setup.sh
```

---

## 🔄 HOW TO UPDATE CODE WHEN NEW COMMITS ARE PUSHED

If new updates or commits are pushed to GitHub:

### 🌟 Method 1: Automatic Auto-Update (Recommended)
`termux_setup.sh` automatically checks GitHub and pulls latest commits every time it is launched! Simply run:
```bash
cd DikshaPlus-Automation-Suite
./termux_setup.sh
```

### 🛠️ Method 2: Manual `git pull` Update
If you want to manually update:
```bash
cd DikshaPlus-Automation-Suite
git pull origin main
./termux_setup.sh
```

---

## 📋 INTERACTIVE USER & COURSE SELECTION MENU IN TERMUX

When `./termux_setup.sh` runs in Termux, it displays the interactive CLI selection menu:

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
