# 🚀 DIKSHA+ AUTOMATION SUITE — 4-WAY EXECUTION ARCHITECTURE

---

## 📌 OVERVIEW & ARCHITECTURE SUMMARY

**DIKSHA+ Automation Suite** is engineered with a **4-Way Flexible Execution Architecture**. It allows users to execute, monitor, and manage automated course completion across desktop computers, cloud servers, mobile browsers, and native mobile terminals seamlessly.

```
                               ┌─────────────────────────────────────────────────────────┐
                               │             DIKSHA+ AUTOMATION SUITE                    │
                               │        (256-Bit SHA-256 Encrypted Security)            │
                               └────────────────────────────┬────────────────────────────┘
                                                            │
         ┌───────────────────────────┬──────────────────────┴────┬───────────────────────────┐
         │                           │                           │                           │
         ▼                           ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     MODE 1      │         │     MODE 2      │         │     MODE 3      │         │     MODE 4      │
│  LOCAL LAPTOP   │         │ RAILWAY CLOUD   │         │ RAILWAY MOBILE  │         │ TERMUX MOBILE   │
│  (DESKTOP GUI)  │         │  (24/7 DOCKER)  │         │ (PHONE BROWSER) │         │ (NATIVE APP)    │
└─────────────────┘         └─────────────────┘         └─────────────────┘         └─────────────────┘
```

---

## 💻 MODE 1: LOCAL LAPTOP EXECUTION (DESKTOP GUI)

### 📖 Description:
Mode 1 runs directly on your Windows, Mac, or Linux laptop. It opens a visible desktop Chromium browser window, allowing you to watch the automation navigate DIKSHA in real time.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=False`, `IS_TERMUX=False`, `HEADLESS=False`.
* **Interface**: Interactive Terminal Menu with PIN Lock (`541563`) and visible browser GUI window.
* **Hotkeys**: Press **`P`** or **`Spacebar`** in terminal at any time to Live Pause / Resume execution.
* **Speed & Safety**: Smooth pacing, full visual feedback, 100% preserved local code.

### 🚀 How to Run:
```bash
python main.py
```

---

## ☁️ MODE 2: RAILWAY CLOUD AUTONOMOUS SERVER (24/7 DOCKER)

### 📖 Description:
Mode 2 runs as a containerized 24/7 background service on Railway Cloud. It requires zero user interaction and automatically processes enrolled courses and modules in headless mode.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=True`, `IS_TERMUX=False`, `HEADLESS=True`.
* **Container**: Official Playwright Python Docker environment (`Dockerfile`).
* **Auto-Start**: Automatically triggers execution upon container boot using `SELECTED_USER=1` (Sumanta Halder) or configured default.
* **Resiliency**: Built-in 8-Key Multi-AI API Pool (5 Gemini + 3 Groq Cloud LPU) and Circuit Breaker safeguards.

### 🚀 How to Deploy:
1. Push repository to GitHub: `https://github.com/thechandrax/DikshaPlus-Automation-Suite`.
2. Connect repository to **Railway.app**.
3. Railway automatically builds the Dockerfile and starts execution.

---

## 📱 MODE 3: RAILWAY CLOUD MOBILE CONTROL (VIA PHONE BROWSER)

### 📖 Description:
Mode 3 allows you to control, monitor, and trigger your Railway Cloud deployment directly from your smartphone's web browser (Chrome, Safari, Firefox, Brave) with **0% battery drain on your phone**.

### 🔑 Features & Characteristics:
* **Phone Battery Drain**: **0%** (All processing occurs on Railway Cloud servers).
* **Remote User Selection**: Change `SELECTED_USER` variable from your phone screen (`1`, `2`, `3`, `4`, `5`, `all`).
* **Real-Time Live Logs**: View color-coded terminal log output live on your phone screen.

### 🚀 How to Use:
1. Open **[Railway.app/dashboard](https://railway.app/dashboard)** in your phone's browser.
2. Select **DikshaPlus-Automation-Suite** $\rightarrow$ **Variables** tab.
3. Set `SELECTED_USER` to `1` (Sumanta Halder `7044015007`) or `all`.
4. Tap **Deployments** $\rightarrow$ **View Logs** to watch live progress on your phone screen!

---

## 📲 MODE 4: NATIVE ANDROID TERMUX EXECUTION (DIRECT MOBILE APP)

### 📖 Description:
Mode 4 runs `python main.py` directly inside the **Termux terminal app** on your Android smartphone using native ARM64 Chromium.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=False`, `IS_TERMUX=True`, `HEADLESS=True`.
* **On-Device Run**: Executes locally on your phone without needing a computer or cloud account.
* **1-Click Setup**: Includes automated `termux_setup.sh` script to install Python, Node.js, and Termux Chromium.

### 🚀 How to Run:
Open **Termux** on your Android phone and paste:
```bash
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
cd "Diksha+ Automation Suite"
chmod +x termux_setup.sh
./termux_setup.sh
```

---

## 📊 4-WAY EXECUTION COMPARISON MATRIX

| Feature | 💻 Mode 1: Laptop | ☁️ Mode 2: Railway Server | 📱 Mode 3: Railway Mobile | 📲 Mode 4: Termux App |
| :--- | :--- | :--- | :--- | :--- |
| **`IS_DOCKER`** | `False` | `True` | `True` | `False` |
| **`IS_TERMUX`** | `False` | `False` | `False` | `True` |
| **`HEADLESS`** | `False` (GUI Window) | `True` (Headless) | `True` (Headless) | `True` (Headless) |
| **Primary Device** | Laptop / PC | Cloud Server | Phone Browser | Android Phone |
| **Phone Battery Impact** | N/A | None (Cloud Run) | **0% Drain** 🔋 | Uses Phone Battery 🔋 |
| **Interactive Menu** | Yes (Terminal Menu) | No (Auto-Start) | Remote Variables | Command Line |
| **Code Preservation** | **100% Untouched** ✅ | **100% Optimized** ✅ | **100% Accessible** ✅ | **100% Supported** ✅ |
