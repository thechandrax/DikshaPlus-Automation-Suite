# 📱 DIKSHA+ AUTOMATION SUITE — TERMUX MOBILE EXECUTION GUIDE

---

## 📌 OVERVIEW

**DIKSHA+ Automation Suite** supports **3 execution environments**:
1. 💻 **Local Laptop (Desktop GUI)**: Visible browser window, interactive terminal menu (`IS_DOCKER=False`, `IS_TERMUX=False`).
2. ☁️ **Railway Cloud (Docker Container)**: Headless background execution, zero battery usage (`IS_DOCKER=True`).
3. 📱 **Android Mobile (Termux App)**: Native mobile execution using Termux & ARM64 Chromium (`IS_TERMUX=True`).

---

## 🚀 METHOD 1: 1-Click Automated Setup on Termux

Open **Termux** on your Android mobile phone and paste:

```bash
# Clone repository
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
cd "Diksha+ Automation Suite"

# Make setup script executable & run
chmod +x termux_setup.sh
./termux_setup.sh
```

---

## 🛠️ METHOD 2: Manual Step-by-Step Termux Command List

If you prefer installing dependencies step-by-step:

### Step 1: Update Packages & Install Tools
```bash
pkg update -y && pkg upgrade -y
pkg install python nodejs-lts chromium x11-repo tur-repo -y
```

### Step 2: Install Python Requirements
```bash
pip install pandas openpyxl pillow playwright
```

### Step 3: Configure Termux Environment Variables
```bash
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True
```

### Step 4: Run DIKSHA+
```bash
python main.py
```

---

## 📊 ENVIRONMENT COMPATIBILITY MATRIX

| Environment | `IS_DOCKER` | `IS_TERMUX` | `HEADLESS` | Interface | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 💻 **Local Laptop** | `False` | `False` | `False` | Visible Desktop GUI Window | **100% Preserved** ✅ |
| ☁️ **Railway Cloud** | `True` | `False` | `True` | Background Headless Container | **100% Preserved** ✅ |
| 📱 **Termux Mobile** | `False` | `True` | `True` | Native Headless Mobile Console | **100% Supported** ✅ |
