# 📱 TERMUX & UBUNTU PROOT ULTIMATE AUTOMATION GUIDE

Welcome to the complete, step-by-step guide for running **DIKSHA+ Automation Suite** on Android using **Termux** & **Ubuntu PRoot** with **RealVNC Visible Browser GUI**!

---

## 🚀 1. FIRST-TIME INSTALLATION (Run ONCE Only)

### 📲 Step A: Setup Termux & Install Ubuntu PRoot

Open the **Termux app** on your Android phone and run these commands:

```bash
# 1. Update Termux packages and install proot-distro
pkg update -y && pkg upgrade -y
pkg install proot-distro -y

# 2. Install Ubuntu environment
proot-distro install ubuntu

# 3. Log into Ubuntu
proot-distro login ubuntu
```

---

### 📦 Step B: Install Ubuntu Packages & Clone Repository

Once inside Ubuntu (`root@localhost:~#`), run this command block:

```bash
# 1. Update Ubuntu packages and install Python 3, Node.js, Chromium, XFCE Desktop & TigerVNC
apt update && apt install git python3 python3-pip nodejs chromium-browser xfce4 tigervnc-standalone-server -y

# 2. Install Python Playwright & dependencies
pip3 install playwright openpyxl pandas pillow requests groq google-generativeai

# 3. Install Playwright Chromium browser drivers
playwright install chromium --with-deps

# 4. Clone DIKSHA+ repository
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
```

---

### ⚡ Step C: Add 1-Word Command Shortcuts (Run ONCE)

Paste this command block inside Ubuntu to enable **`vnc`** and **`diksha`** 1-word shortcuts:

```bash
echo "alias vnc='vncserver -kill :1 2>/dev/null; vncserver :1'" >> ~/.bashrc
echo "alias diksha='cd ~/DikshaPlus-Automation-Suite && export DISPLAY=:1 && python3 main.py'" >> ~/.bashrc
source ~/.bashrc
```

---

## 🎮 2. DAILY EASY WORKFLOW (Using 1-Word Shortcuts!)

Every day when you open Termux, running DIKSHA+ takes just **3 easy commands**:

```bash
# 1. Log into Ubuntu
proot-distro login ubuntu

# 2. Start VNC Server (1-word shortcut!)
vnc

# 3. Launch DIKSHA+ Engine (1-word shortcut!)
diksha
```

---

## 📺 3. HOW TO WATCH THE BROWSER LIVE IN REALVNC VIEWER APP

1. Download free **RealVNC Viewer** from Google Play Store.
2. Open RealVNC Viewer $\rightarrow$ Tap **`+`** (New Connection):
   * **Address**: `127.0.0.1:5901`
   * **Name**: `DIKSHA Plus`
   * Tap **CREATE**.
3. Tap the green **CONNECT** button.
4. When prompted for password, enter **`123456`** and tap **OK**!
5. **Result**: You will see Chromium open live on your phone screen, clicking options, playing videos, and completing DIKSHA courses in real-time! 🖥️📱

---

## 🔒 4. SECURITY ACCESS PIN & ASTERISK (`*`) MASKING

When prompted for the Security Access PIN:

```text
🔒 DIKSHA+ SECURITY ACCESS VERIFICATION (256-BIT SHA-256)
[Security] Enter 6-digit Security PIN to unlock: ******
```

* **PIN**: `541563`
* **Live Asterisks (`*`)**: As you type each digit on your keyboard, asterisks `******` appear live on screen! Backspace erases characters live!

---

## 🚪 5. HOW TO EXIT UBUNTU & TERMUX

* **Type `exit` once**: Exits Ubuntu PRoot (`root@localhost`) back to Termux (`~ $`).
* **Type `exit` twice**: Closes the Termux app completely!

---

## 🛠️ 6. TROUBLESHOOTING GUIDE

| Issue / Error | Cause | Quick Fix |
| :--- | :--- | :--- |
| **`RealVNC: Port could not be contacted`** | `vncserver` is not running yet | Type **`vnc`** in Ubuntu terminal |
| **`bash: vnc: command not found`** | Aliases not loaded yet | Type **`source ~/.bashrc`** |
| **`Error: Unsupported platform: android`** | Native Playwright check | Automatically patched by `config.py` & `run_diksha.sh` |
| **`NameError: name 'completed_items'`** | Scope issue in old code | Run **`git pull origin main`** to update |
| **`View` button skipping** | Generic button label bug | Automatically isolated by item title memory |

---

## 🔄 7. HOW TO GET THE LATEST UPDATES FROM GITHUB

To pull the latest updates pushed to GitHub:

```bash
cd ~/DikshaPlus-Automation-Suite
git pull origin main
```
