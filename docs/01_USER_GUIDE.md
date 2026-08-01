# 📖 User Guide & Workflow

This document explains how to launch and operate **DIKSHA+ Automation Suite**.

---

## 🚀 1. Launching DIKSHA+ Automation Suite

### Method A: Double-Click Batch File (Recommended)
Double-click the launcher batch file in the project folder:
`diksha+.bat`

### Method B: Command Prompt / Terminal
Open CMD or PowerShell in the project directory (`C:\Users\thego\.gemini\antigravity\scratch\Diksha+ Automation Suite`) and run:
```bash
python main.py
```

---

## 🔒 2. Security Access PIN Verification

Upon launch, DIKSHA+ prompts for a 6-digit Security PIN:

```text
===================================================================
               LAUNCHING DIKSHA+ AUTOMATION SUITE
===================================================================

===================================================================
 🔒 DIKSHA+ SECURITY ACCESS VERIFICATION (256-BIT SHA-256)
===================================================================

[Security] Enter 6-digit Security PIN to unlock: ******
 ✔ [Security] 256-Bit Cryptographic PIN verified! Access granted.
```

* **Security PIN**: `******` (Protected via 256-Bit SHA-256 Salted Hash)

* **Live Asterisk (`*`) Feedback**: As you type your PIN digits, live `*` symbols echo on screen.
* **Backspace Support**: Pressing <kbd>Backspace</kbd> erases asterisks live.
* **Security Lock**: You have 3 attempts before access is denied.

---

## 👤 3. Account Selection Menu with User Display Names

After PIN verification, the registered account selector appears formatted with user display names:

```text
===================================================================
 ⚡ DIKSHA+ AUTOMATION SUITE
===================================================================

[Login] Registered accounts:
  [1] Gsgs Sdgr                : gexowo4534@candaba.com
  [2] Bgdh Hdfh                : borkej@smanthaai.online
  [3] Sujata Mondal            : 8617383566
  [4] Sumanta Halder           : 7044015007
  [5] Tasapur Rahaman           : 7908555852
-------------------------------------------------------------------
👉 Select user number (1-5) or type custom email/mobile:
```

* **Select Registered Account**: Type `1`, `2`, `3`, `4`, or `5` and press <kbd>Enter</kbd>.
* **Custom Account**: Type any custom email or mobile number, then enter its password.

---

## 🎓 4. Enrolled Courses Dashboard & Selection

Once logged in, DIKSHA+ scans your **Ongoing Courses** and **Finished Courses** tabs and displays the interactive dashboard:

```text
======================================================================
  🎓 DIKSHA+ ENROLLED COURSES (4 ONGOING • 0 FINISHED)
======================================================================

 ⚡ ONGOING COURSES:
  [01] NISHTHA FLN English                           [█░░░░░░░░░  12%] ⌛ Ongoing
  [02] Power of Audio in Education                   [█████████░  92%] ⌛ Ongoing
  [03] Online and Digital Education in the Len... [█████████░  92%] ⌛ Ongoing
  [04] কাৰ্যভিত্তিক গৱেষণা (Action Research)         [██░░░░░░░░  15%] ⌛ Ongoing

-----------------------------------------------------------------------
 👉 Select course number to automate (1-4) [Enter for 1]:
```

* Type the number of the course you wish to automate (e.g. `1` or `2`).
* Press <kbd>Enter</kbd> (defaults to `1`).
