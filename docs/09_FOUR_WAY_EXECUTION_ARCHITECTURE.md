# 🚀 DIKSHA+ AUTOMATION SUITE — 3-WAY EXECUTION ARCHITECTURE & WORKFLOW GUIDE

---

## 📌 OVERVIEW & CORE PLATFORMS

**DIKSHA+ Automation Suite** is engineered with a flexible, multi-platform architecture. It spans **3 Core Platforms** and **3 Execution Workflows**, letting you run, monitor, and control your course automations across desktop laptops, cloud containers, and mobile Android devices seamlessly.

```
                               ┌─────────────────────────────────────────────────────────┐
                               │             DIKSHA+ AUTOMATION SUITE                    │
                               │        (256-Bit SHA-256 Encrypted Security)            │
                               └────────────────────────────┬────────────────────────────┘
                                                            │
         ┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
         │                                                  │                                                  │
         ▼                                                  ▼                                                  ▼
┌─────────────────┐                        ┌──────────────────────────────────┐                       ┌─────────────────┐
│   PLATFORM 1    │                        │            PLATFORM 2            │                       │   PLATFORM 3    │
│  LOCAL LAPTOP   │                        │       RAILWAY CLOUD SYSTEM       │                       │  TERMUX MOBILE  │
│  (DESKTOP GUI)  │                        │        (DOCKER CONTAINER)        │                       │  (UBUNTU PROOT) │
└────────┬────────┘                        └────────────────┬─────────────────┘                       └────────┬────────┘
         │                                                  │                                                  │
         ▼                                                  ▼                                                  ▼
    [ MODE 1 ]                                         [ MODE 2 ]                                         [ MODE 3 ]
 Local Laptop GUI                                 Railway Cloud Server                                Termux Mobile Run
 (Visible Window)                                (Background Container)                              (RealVNC Visible GUI)
```

---

## 💻 MODE 1: LOCAL LAPTOP EXECUTION (DESKTOP GUI)

### 📖 Description:
Mode 1 runs directly on your Windows, Mac, or Linux laptop. It opens a visible desktop Chromium browser window, allowing you to watch the automation navigate DIKSHA in real time.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=False`, `HEADLESS=False`.
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
* **Environment Flags**: `IS_DOCKER=True`, `HEADLESS=True`.
* **Container**: Official Playwright Python Docker environment (`Dockerfile`).
* **Auto-Start**: Automatically triggers execution upon container boot using `SELECTED_USER=1` (Sumanta Halder `7044015007`) or configured default.
* **Resiliency**: Built-in 8-Key Multi-AI API Pool (5 Gemini + 3 Groq Cloud LPU) and Circuit Breaker safeguards.

### 🚀 How to Deploy:
1. Push repository to GitHub: `https://github.com/thechandrax/DikshaPlus-Automation-Suite`.
2. Connect repository to **Railway.app**.
3. Railway automatically builds the Dockerfile and starts execution.

---

## 📱 MODE 3: ANDROID TERMUX UBUNTU PROOT (REALVNC VISIBLE GUI)

### 📖 Description:
Mode 3 runs `python3 main.py` directly inside **Ubuntu PRoot** on your Android smartphone using **RealVNC Viewer** to display the browser live on your phone screen.

### 🔑 Features & Characteristics:
* **Environment Flags**: `IS_DOCKER=False`, `HEADLESS=False` (when `DISPLAY=:1` is set).
* **On-Device Run**: Executes locally on your phone using 1-word shortcuts (`vnc` and `diksha`).
* **Live Visual GUI**: Open RealVNC Viewer (`127.0.0.1:5901`) to watch Chromium work live on your phone!

### 🚀 How to Run:
In your Termux terminal, run:
```bash
proot-distro login ubuntu
vnc
diksha
```

---

## 📊 3-MODE EXECUTION COMPARISON MATRIX

| Mode | Platform | System Role | Interface | Phone Battery Impact | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode 1** | 💻 **Laptop** | Local Desktop Run | Visible GUI Window | N/A | **100% Preserved** ✅ |
| **Mode 2** | ☁️ **Railway Cloud** | Automated Server Backend | Headless Container | None (Cloud Engine) | **100% Preserved** ✅ |
| **Mode 3** | 📱 **Termux Ubuntu PRoot** | Native Mobile Run | RealVNC Visible GUI | Uses Phone Battery 🔋 | **100% Supported** ✅ |
