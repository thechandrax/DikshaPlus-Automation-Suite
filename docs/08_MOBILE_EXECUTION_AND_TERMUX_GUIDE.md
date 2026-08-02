# 📱 DIKSHA+ AUTOMATION SUITE — COMPLETE MOBILE EXECUTION GUIDE

---

## 📌 OVERVIEW

**DIKSHA+ Automation Suite** provides **2 complete mobile workflows** so you can run, monitor, and control your automations directly from your smartphone:

1. ☁️ **METHOD 1: Railway Cloud via Mobile Phone Browser** *(Recommended - 0% Battery Drain)*
2. 📱 **METHOD 2: Native Android Run inside Termux App** *(Direct On-Device Local Run)*

---

## ☁️ METHOD 1: Railway Cloud via Mobile Phone Browser (0% Battery Usage)

This method lets you control your entire automation suite from your phone's web browser without draining your phone's battery or processing power.

### 🌐 Step-by-Step Instructions:

1. **Open Mobile Browser**:
   Open Chrome, Safari, Firefox, or Brave on your smartphone.

2. **Access Railway Dashboard**:
   Navigate to **[https://railway.app/dashboard](https://railway.app/dashboard)** and sign in.

3. **Select DIKSHA+ Project**:
   Tap your **DikshaPlus-Automation-Suite** deployment service.

4. **Change Account or Course (Variables Tab)**:
   Tap the **Variables** tab to set your target user profile:
   * `SELECTED_USER=1` $\rightarrow$ Account #1 (Sumanta Halder `7044015007`)
   * `SELECTED_USER=2` $\rightarrow$ Account #2 (Chandra)
   * `SELECTED_USER=3` $\rightarrow$ Account #3
   * `SELECTED_USER=all` $\rightarrow$ Auto-runs all accounts sequentially!

5. **Monitor Live Execution (View Logs)**:
   Tap the **Deployments** tab and click **View Logs**.
   You will see live color-coded logs on your phone screen in real time:
   ```text
   [17:20:00] INFO [Main] Starting DIKSHA+ Automation Suite...
   [17:20:05] INFO [DikshaEngine] 📚 MODULE [1/3]: Module 01: Introduction to FLN
   [17:20:12] INFO [DikshaEngine] 🧠 [GEMINI AI SUCCESS] Solved via Key #1 -> 'Mission'
   ```

---

## 📱 METHOD 2: Native Android Execution inside Termux App

This method runs Playwright Python and Chromium directly inside the **Termux app** on your Android device.

### 🚀 1-Click Automated Setup:

Open **Termux** on your Android phone and run:

```bash
# 1. Clone repository
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
cd "Diksha+ Automation Suite"

# 2. Run 1-click Termux setup script
chmod +x termux_setup.sh
./termux_setup.sh
```

---

### 🛠️ Manual Step-by-Step Installation:

If you prefer installing packages manually:

```bash
# Step 1: Update Termux & install Linux tools
pkg update -y && pkg upgrade -y
pkg install python nodejs-lts chromium x11-repo tur-repo -y

# Step 2: Install Python libraries
pip install pandas openpyxl pillow playwright

# Step 3: Set Termux environment variables
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export HEADLESS=True

# Step 4: Run DIKSHA+
python main.py
```

---

## 📊 ENVIRONMENT & WORKFLOW COMPARISON MATRIX

| Feature | 💻 Laptop GUI | ☁️ Railway Cloud (Phone Browser) | 📱 Termux App (Direct Phone) |
| :--- | :--- | :--- | :--- |
| **`IS_DOCKER`** | `False` | `True` | `False` |
| **`IS_TERMUX`** | `False` | `False` | `True` |
| **`HEADLESS`** | `False` (Visible Desktop GUI) | `True` (Headless Container) | `True` (Headless Mobile) |
| **Phone Battery Usage** | N/A | **0% (Zero Drain)** 🔋 | Uses Phone Battery 🔋 |
| **Execution Speed** | Desktop Speed | **Cloud Speeds** ⚡ | Phone CPU Speed 📱 |
| **Setup Time** | 0 Minutes | 0 Minutes | 2-3 Minutes |
| **Laptop Code Status** | **100% Preserved** ✅ | **100% Preserved** ✅ | **100% Preserved** ✅ |
