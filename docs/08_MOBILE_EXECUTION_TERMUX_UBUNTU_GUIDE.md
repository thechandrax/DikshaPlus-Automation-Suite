# 📱 DIKSHA+ AUTOMATION SUITE — COMPLETE TERMUX & UBUNTU PROOT SETUP GUIDE

This guide provides exhaustive, step-by-step instructions on **how to install Termux**, **how to setup Ubuntu PRoot**, **how to configure RealVNC Visible Mobile GUI**, and **how to clone public or private repositories**.

---

## 📑 Table of Contents

1. [📱 Step 0: Download & Install Termux App](#-step-0-download--install-termux-app)
2. [⚡ Single-Command 1-Click All-in-One Setup (Quickest)](#-single-command-1-click-all-in-one-setup-quickest)
3. [🛠️ Multi-Step Detailed Command Setup (Step-by-Step)](#%EF%B8%8F-multi-step-detailed-command-setup-step-by-step)
4. [🔒 How to Clone Private Repository in Termux](#-how-to-clone-private-repository-in-termux)
5. [📺 RealVNC Viewer App Connection Setup](#-realvnc-viewer-app-connection-setup)
6. [🚀 Daily 3-Command Execution Workflow](#-daily-3-command-execution-workflow)
7. [⚡ 1-Word Shortcut Reference Table](#-1-word-shortcut-reference-table)

---

## 📱 Step 0: Download & Install Termux App

> ⚠️ **IMPORTANT NOTE**: Do **NOT** install Termux from Google Play Store (it is an outdated 2019 build and will fail).

1. Download the latest **Termux APK** from **F-Droid**:
   👉 **[https://f-droid.org/packages/com.termux/](https://f-droid.org/packages/com.termux/)**
2. Install the APK on your Android smartphone and open **Termux**.

---

## ⚡ Single-Command 1-Click All-in-One Setup (Quickest)

If you want to install everything automatically in one go, copy and paste this **single multi-command block** into Termux:

```bash
# 1-Click Complete Termux & Ubuntu PRoot Setup Script
pkg update -y && pkg upgrade -y && pkg install proot-distro git -y && proot-distro install ubuntu && proot-distro login ubuntu -- bash -c "apt update -y && apt upgrade -y && apt install -y python3 python3-pip git chromium-browser tigervnc-standalone-server tigervnc-common x11-utils && pip3 install pandas openpyxl pillow playwright && python3 -m playwright install-deps && mkdir -p ~/.config/tigervnc && echo 123456 | vncpasswd -f > ~/.config/tigervnc/passwd && chmod 600 ~/.config/tigervnc/passwd && git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git ~/DikshaPlus-Automation-Suite && echo \"alias vnc='vncserver -kill :1 2>/dev/null; vncserver :1'\" >> ~/.bashrc && echo \"alias diksha='cd ~/DikshaPlus-Automation-Suite && export DISPLAY=:1 && python3 main.py'\" >> ~/.bashrc && echo \"alias exit='exit'\" >> ~/.bashrc && source ~/.bashrc && echo '✅ SETUP 100% COMPLETE! Log into Ubuntu using: proot-distro login ubuntu'"
```

---

## 🛠️ Multi-Step Detailed Command Setup (Step-by-Step)

If you prefer to run commands step-by-step:

### 🔹 STEP 1: Update Termux Base Packages & Install `proot-distro`
Open **Termux** app on your phone and paste:
```bash
pkg update -y && pkg upgrade -y
pkg install proot-distro git -y
```

### 🔹 STEP 2: Install Ubuntu Linux Distribution
```bash
proot-distro install ubuntu
```

### 🔹 STEP 3: Log into Ubuntu PRoot
```bash
proot-distro login ubuntu
```
*(Your terminal prompt will change to `root@localhost:~#`)*

### 🔹 STEP 4: Install Linux GUI, Python 3, Chromium & TigerVNC inside Ubuntu
Inside Ubuntu, paste:
```bash
apt update -y && apt upgrade -y
apt install -y python3 python3-pip git chromium-browser tigervnc-standalone-server tigervnc-common x11-utils
pip3 install pandas openpyxl pillow playwright
python3 -m playwright install-deps
```

### 🔹 STEP 5: Set VNC Password (`123456`)
```bash
mkdir -p ~/.config/tigervnc
echo "123456" | vncpasswd -f > ~/.config/tigervnc/passwd
chmod 600 ~/.config/tigervnc/passwd
```

### 🔹 STEP 6: Clone Repository

#### Option A: Public Repository
```bash
cd ~
git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git
```

#### Option B: Private Repository (With Personal Access Token)
If your repository is **Private**, use your GitHub Personal Access Token (`ghp_...`):
```bash
cd ~
git clone https://YOUR_TOKEN@github.com/thechandrax/DikshaPlus-Automation-Suite.git
```
*(Save token permanently in git)*:
```bash
git config --global credential.helper store
```

### 🔹 STEP 7: Create 1-Word Shortcuts (`vnc`, `diksha`, `exit`)
Inside Ubuntu, paste:
```bash
echo "alias vnc='vncserver -kill :1 2>/dev/null; vncserver :1'" >> ~/.bashrc
echo "alias diksha='cd ~/DikshaPlus-Automation-Suite && export DISPLAY=:1 && python3 main.py'" >> ~/.bashrc
echo "alias exit='exit'" >> ~/.bashrc
source ~/.bashrc
```

---

## 🔒 How to Clone Private Repository in Termux

1. **Generate GitHub Personal Access Token (PAT)**:
   * Open **GitHub.com** $\rightarrow$ Profile Icon $\rightarrow$ **Settings** $\rightarrow$ **Developer settings** $\rightarrow$ **Personal access tokens (classic)**.
   * Click **Generate new token**, check the **`repo`** box, and copy your token (`ghp_...`).

2. **Clone Private Repo in Termux**:
   ```bash
   git clone https://ghp_YourPersonalAccessToken123456@github.com/thechandrax/DikshaPlus-Automation-Suite.git
   ```

3. **Save Credentials Permanently**:
   ```bash
   git config --global credential.helper store
   ```
   *(Now `git pull` will never ask for your password again!)*

---

## 📺 RealVNC Viewer App Connection Setup

1. Download **RealVNC Viewer** app from Google Play Store on your Android phone.
2. Open RealVNC Viewer $\rightarrow$ Tap the **`+` (Plus)** button to add connection:
   * **Address**: `127.0.0.1:5901`
   * **Name**: `DIKSHA Plus`
3. Tap **CONNECT** $\rightarrow$ Enter Password: **`123456`**.
4. Check **"Remember password"** $\rightarrow$ Tap **Continue**.
5. You will see your visible Linux desktop browser live on your phone screen!

---

## 🚀 Daily 3-Command Execution Workflow

Every day when you open Termux on your smartphone:

```bash
# 1. Log into Ubuntu PRoot
proot-distro login ubuntu

# 2. Start VNC Server (1-word shortcut!)
vnc

# 3. Launch DIKSHA+ Engine (1-word shortcut!)
diksha
```

---

## ⚡ 1-Word Shortcut Reference Table

| Shortcut Command | What It Does |
| :--- | :--- |
| **`vnc`** | Kills stale VNC sessions & launches fresh VNC server on port `5901` (`:1`) |
| **`diksha`** | Enters project folder, sets `DISPLAY=:1`, & launches DIKSHA+ with visible GUI browser! |
| **`exit`** | Exits Ubuntu PRoot (`root@localhost`) back to standard Termux (`~ $`) |
