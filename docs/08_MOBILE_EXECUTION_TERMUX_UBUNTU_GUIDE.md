# 📱 DIKSHA+ AUTOMATION SUITE — COMPLETE TERMUX & UBUNTU PROOT SETUP GUIDE

This guide provides exhaustive, step-by-step instructions on **how to install Termux**, **how to setup Ubuntu PRoot**, **how to run WITH VNC (Visible Mobile GUI)**, **how to run WITHOUT VNC (Headless Background Mode)**, **how to update code via Git (`git pull`)**, **how to fix Playwright installation errors**, **how to keep Termux awake (`termux-wake-lock`)**, and **how to configure system timezone (`dpkg-reconfigure tzdata`)**.

---

## 📑 Table of Contents

1. [📱 Step 0: Download & Install Termux App](#-step-0-download--install-termux-app)
2. [⚡ Single-Command 1-Click All-in-One Setup (Quickest)](#-single-command-1-click-all-in-one-setup-quickest)
3. [🛠️ Multi-Step Detailed Command Setup (Step-by-Step)](#%EF%B8%8F-multi-step-detailed-command-setup-step-by-step)
4. [⏰ How to Change System Timezone (`dpkg-reconfigure tzdata`)](#-how-to-change-system-timezone-dpkg-reconfigure-tzdata)
5. [🔋 How to Keep Termux Awake (`termux-wake-lock`)](#-how-to-keep-termux-awake-termux-wake-lock)
6. [🛠️ Playwright Installation Error Fix (`No module named playwright`)](#%EF%B8%8F-playwright-installation-error-fix-no-module-named-playwright)
7. [📺 How to Run WITH VNC (RealVNC Visible Mobile GUI)](#-how-to-run-with-vnc-realvnc-visible-mobile-gui)
8. [🙈 How to Run WITHOUT VNC (Headless Background Mode)](#-how-to-run-without-vnc-headless-background-mode)
9. [🔄 How to Update Code to Latest Commit (`git pull`)](#-how-to-update-code-to-latest-commit-git-pull)
10. [🔒 How to Clone Private Repository in Termux](#-how-to-clone-private-repository-in-termux)
11. [📺 RealVNC Viewer App Connection Setup](#-realvnc-viewer-app-connection-setup)
12. [⚡ 1-Word Shortcut Reference Table](#-1-word-shortcut-reference-table)

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
pkg update -y && pkg upgrade -y && pkg install proot-distro git -y && proot-distro install ubuntu && proot-distro login ubuntu -- bash -c "apt update -y && apt upgrade -y && apt install -y python3 python3-pip git chromium-browser tigervnc-standalone-server tigervnc-common x11-utils && pip3 install pandas openpyxl pillow playwright && python3 -m playwright install-deps && mkdir -p ~/.config/tigervnc && echo 123456 | vncpasswd -f > ~/.config/tigervnc/passwd && chmod 600 ~/.config/tigervnc/passwd && git clone https://github.com/thechandrax/DikshaPlus-Automation-Suite.git ~/DikshaPlus-Automation-Suite && echo \"alias vnc='vncserver -kill :1 2>/dev/null; vncserver :1'\" >> ~/.bashrc && echo \"alias diksha='cd ~/DikshaPlus-Automation-Suite && export DISPLAY=:1 && python3 main.py'\" >> ~/.bashrc && echo \"alias update='cd ~/DikshaPlus-Automation-Suite && git pull'\" >> ~/.bashrc && echo \"alias exit='exit'\" >> ~/.bashrc && source ~/.bashrc && echo '✅ SETUP 100% COMPLETE! Log into Ubuntu using: proot-distro login ubuntu'"
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

### 🔹 STEP 2: Enable Wake Lock (Prevent Sleep)
```bash
termux-wake-lock
```

### 🔹 STEP 3: Install Ubuntu Linux Distribution
```bash
proot-distro install ubuntu
```

### 🔹 STEP 4: Log into Ubuntu PRoot
```bash
proot-distro login ubuntu
```
*(Your terminal prompt will change to `root@localhost:~#`)*

### 🔹 STEP 5: Install Linux GUI, Python 3, Chromium & TigerVNC inside Ubuntu
Inside Ubuntu, paste:
```bash
apt update -y && apt upgrade -y
apt install -y python3 python3-pip git chromium-browser tigervnc-standalone-server tigervnc-common x11-utils tzdata
pip3 install pandas openpyxl pillow playwright
python3 -m playwright install-deps
```

### 🔹 STEP 6: Set VNC Password (`123456`)
```bash
mkdir -p ~/.config/tigervnc
echo "123456" | vncpasswd -f > ~/.config/tigervnc/passwd
chmod 600 ~/.config/tigervnc/passwd
```

### 🔹 STEP 7: Clone Repository

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

### 🔹 STEP 8: Create 1-Word Shortcuts (`vnc`, `diksha`, `headless`, `update`, `exit`)
Inside Ubuntu, paste:
```bash
echo "alias vnc='vncserver -kill :1 2>/dev/null; vncserver :1'" >> ~/.bashrc
echo "alias diksha='cd ~/DikshaPlus-Automation-Suite && export DISPLAY=:1 && python3 main.py'" >> ~/.bashrc
echo "alias headless='cd ~/DikshaPlus-Automation-Suite && export HEADLESS=True && python3 main.py'" >> ~/.bashrc
echo "alias update='cd ~/DikshaPlus-Automation-Suite && git pull'" >> ~/.bashrc
echo "alias exit='exit'" >> ~/.bashrc
source ~/.bashrc
```


---

## ⏰ How to Change System Timezone (`dpkg-reconfigure tzdata`)

If you want to configure or fix your system timezone in Termux / Ubuntu PRoot:

```bash
dpkg-reconfigure tzdata
```

1. Select your geographic area (e.g. **Asia**).
2. Select your city / timezone (e.g. **Kolkata** for IST +05:30).
3. Press **Enter**. You can run this command as many times as you need whenever you want to change timezone!

---

## 🔋 How to Keep Termux Awake (`termux-wake-lock`)

To prevent Android OS from putting Termux to sleep during long background automations:

```bash
termux-wake-lock
```

* This holds an active CPU wake-lock so your automation runs continuously without sleeping!

---

## 🛠️ Playwright Installation Error Fix (`No module named playwright`)

### 🔍 Why This Happens:
If you try to run `python3 -m playwright install-deps` before installing Playwright via pip, Python throws an error: `No module named playwright`.

### 🛠️ How to Fix:
You MUST install the Playwright Python package using `pip3` **first**:

#### Step 1: Install Playwright Python Package
```bash
pip3 install playwright
```
*(Wait for pip installation to completely finish)*

#### Step 2: Install Browser Dependencies
```bash
python3 -m playwright install-deps
```

---

## 📺 How to Run WITH VNC (RealVNC Visible Mobile GUI)

Use this method when you want to **watch the browser live on your smartphone screen** using RealVNC Viewer!

```bash
# 1. Log into Ubuntu PRoot
proot-distro login ubuntu

# 2. Start VNC Server (1-word shortcut!)
vnc

# 3. Launch DIKSHA+ Engine with Visible GUI Browser (1-word shortcut!)
diksha
```

* Open **RealVNC Viewer** app (`127.0.0.1:5901`, password `123456`) to watch the browser live!

---

## 🙈 How to Run WITHOUT VNC (Headless Background Mode)

Use this method when you want to run the automation **100% silently in the background** without opening RealVNC Viewer:

```bash
# 1. Log into Ubuntu PRoot
proot-distro login ubuntu

# 2. Enter project folder & run in Headless mode
cd ~/DikshaPlus-Automation-Suite
export HEADLESS=True
python3 main.py
```

---

## 🔄 How to Update Code to Latest Commit (`git pull`)

When new features, bug fixes, or answer key updates are pushed to GitHub, update your Termux code to the latest commit in 1 step:

### 🔹 Method A: Using 1-Word `update` Shortcut (Easiest)
Inside Ubuntu, simply type:
```bash
update
```

### 🔹 Method B: Direct Git Command
```bash
cd ~/DikshaPlus-Automation-Suite && git pull
```

* **Verification**:
  If code is already up to date, it outputs: `Already up to date.`
  If new updates were downloaded, it prints the updated commit summary!

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

## ⚡ 1-Word Shortcut Reference Table

| Shortcut Command | What It Does |
| :--- | :--- |
| **`vnc`** | Kills stale VNC sessions & launches fresh VNC server on port `5901` (`:1`) |
| **`diksha`** | Enters project folder, sets `DISPLAY=:1`, & launches DIKSHA+ with visible GUI browser! |
| **`update`** | Enters project folder & downloads latest code updates from GitHub (`git pull`)! |
| **`exit`** | Exits Ubuntu PRoot (`root@localhost`) back to standard Termux (`~ $`) |
