# 📱 DIKSHA+ AUTOMATION SUITE — TERMUX & UBUNTU PROOT MOBILE GUIDE

---

## 📌 OVERVIEW

**DIKSHA+ Automation Suite** runs natively on Android smartphones using **Termux & Ubuntu PRoot** with **RealVNC Visible GUI**!

```
 📲 Termux App
   └── 🐧 Ubuntu PRoot Environment
         ├── 🖥️ RealVNC Server (vnc -> port 5901)
         └── ⚡ DIKSHA+ Engine (diksha -> visible browser)
```

---

## ⚡ 1-WORD SHORTCUT COMMANDS IN UBUNTU

| Shortcut Command | What It Does |
| :--- | :--- |
| **`vnc`** | Kills old VNC server & starts fresh VNC server on port `5901` (`:1`) |
| **`diksha`** | Auto-enters project directory, sets `DISPLAY=:1`, & launches DIKSHA+ with visible GUI browser! |
| **`exit`** | Exits Ubuntu PRoot (`root@localhost`) back to Termux (`~ $`) |

---

## 🚀 DAILY 3-COMMAND WORKFLOW

Every day when you open Termux:

```bash
# 1. Log into Ubuntu
proot-distro login ubuntu

# 2. Start VNC Server (1-word shortcut!)
vnc

# 3. Launch DIKSHA+ Engine (1-word shortcut!)
diksha
```

---

## 📺 REALVNC VIEWER APP CONNECTION DETAILS

1. Download **RealVNC Viewer** from Google Play Store.
2. Address: `127.0.0.1:5901`
3. Name: `DIKSHA Plus`
4. Tap **CONNECT** $\rightarrow$ Password: **`123456`**.

---

## 📊 3-WAY EXECUTION MATRIX

| Feature | 💻 Laptop (Windows) | ☁️ Railway Cloud | 📱 Termux (Ubuntu PRoot) |
| :--- | :--- | :--- | :--- |
| **`HEADLESS`** | `False` (Visible Window) | `True` (Background Container) | `False` (RealVNC Visible GUI) |
| **Phone Battery** | N/A | None (Cloud Engine) 🔋 | Uses Phone Battery 🔋 |
| **Interface** | Windows Desktop GUI | Automated Server Backend | RealVNC Visible Mobile GUI |
| **Status** | **100% Preserved** ✅ | **100% Preserved** ✅ | **100% Supported** ✅ |
