# 🚀 DIKSHA+ AUTOMATION SUITE — EXECUTION ARCHITECTURE & WORKFLOW GUIDE

---

## 📌 OVERVIEW & CORE PLATFORMS

**DIKSHA+ Automation Suite** is engineered with a flexible, multi-platform architecture. It spans **3 Core Platforms** and **4 Execution Workflows**, letting you run, monitor, and control your course automations across desktop laptops, cloud containers, mobile browsers, and native mobile terminals seamlessly.

```
                               ┌─────────────────────────────────────────────────────────┐
                               │             DIKSHA+ AUTOMATION SUITE                    │
                               │        (256-Bit SHA-256 Encrypted Security)            │
                               └────────────────────────────┬────────────────────────────┘
                                                            │
         ┌───────────────────────────┬──────────────────────┴────────────────────────────┐
         │                           │                                                   │
         ▼                           ▼                                                   ▼
┌─────────────────┐       ┌──────────────────────────────────────────────────┐  ┌─────────────────┐
│   PLATFORM 1    │       │                    PLATFORM 2                    │  │   PLATFORM 3    │
│  LOCAL LAPTOP   │       │               RAILWAY CLOUD SYSTEM               │  │  TERMUX MOBILE  │
│  (DESKTOP GUI)  │       │                                                  │  │  (NATIVE APP)   │
└────────┬────────┘       └──────────┬────────────────────────────┬──────────┘  └────────┬────────┘
         │                           │                            │                      │
         ▼                           ▼                            ▼                      ▼
    [ MODE 1 ]                  [ MODE 2 ]                   [ MODE 3 ]              [ MODE 4 ]
 Local Laptop GUI          Railway Cloud Server         Railway Mobile Browser     Termux Mobile Run
 (Visible Window)         (Background Container)        (Remote Control 0% Battery) (Native Terminal)
```

> 💡 **Note on Railway Cloud (Mode 2 vs Mode 3)**:
> Mode 2 and Mode 3 share the **EXACT SAME Railway Cloud deployment backend**!
> * **Mode 2** is the automated Playwright container engine running 24/7 on Railway servers.
> * **Mode 3** is the mobile phone web dashboard interface (`https://railway.app/dashboard`) used to control Mode 2, switch user profiles (`SELECTED_USER`), and monitor live logs from your phone with 0% battery drain.

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

## ☁️ MODE 2: RAILWAY CLOUD AUTONOMOUS SERVER (BACKGROUND CONTAINER)

### 📖 Description:
Mode 2 is the automated engine of your Railway Cloud deployment. It runs as a containerized 24/7 background service on Railway Cloud, requiring zero user interaction and processing enrolled courses in headless mode.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=True`, `IS_TERMUX=False`, `HEADLESS=True`.
* **Container**: Official Playwright Python Docker environment (`Dockerfile`).
* **Auto-Start**: Automatically triggers execution upon container boot using `SELECTED_USER=1` (Sumanta Halder `7044015007`) or configured default.
* **Resiliency**: Built-in 8-Key Multi-AI API Pool (5 Gemini + 3 Groq Cloud LPU) and Circuit Breaker safeguards.

### 🚀 How to Deploy:
1. Push repository to GitHub: `https://github.com/thechandrax/DikshaPlus-Automation-Suite`.
2. Connect repository to **Railway.app**.
3. Railway automatically builds the Dockerfile and starts execution.

---

## 📱 MODE 3: RAILWAY CLOUD MOBILE CONTROL (VIA PHONE BROWSER)

### 📖 Description:
Mode 3 is the smartphone control interface for your Mode 2 Railway deployment. It allows you to control, monitor, and trigger your Railway Cloud deployment directly from your phone's web browser with **0% battery drain on your phone**.

### 🔑 Features & Characteristics:
* **Phone Battery Drain**: **0%** (All browser automation runs on Railway Cloud servers).
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
cd DikshaPlus-Automation-Suite

chmod +x termux_setup.sh
./termux_setup.sh
```

---

## 📊 4-MODE EXECUTION COMPARISON MATRIX

| Mode | Platform | System Role | Interface | Phone Battery Impact | Laptop Code Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode 1** | 💻 **Laptop** | Local Desktop Run | Visible GUI Window | N/A | **100% Preserved** ✅ |
| **Mode 2** | ☁️ **Railway Cloud** | Automated Server Backend | Headless Container | None (Cloud Engine) | **100% Preserved** ✅ |
| **Mode 3** | ☁️ **Railway Cloud** | Mobile Remote Control | Phone Web Browser | **0% Drain** 🔋 | **100% Preserved** ✅ |
| **Mode 4** | 📱 **Termux App** | Native Mobile Run | Android Terminal | Uses Phone Battery 🔋 | **100% Supported** ✅ |
