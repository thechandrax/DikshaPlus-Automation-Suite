# 🔐 USER & SECURITY MANAGEMENT GUIDE — HOW TO ADD / DELETE USERS

This document covers Security PIN Authentication (`541563`), live `******` asterisk masking, and step-by-step instructions on **how to add or delete registered user accounts** in **DIKSHA+ Automation Suite**.

---

## 🔒 1. 256-Bit SHA-256 Security Architecture

Access to DIKSHA+ Automation Suite is protected by a 256-bit SHA-256 cryptographic Security PIN lock:
* **Default Security PIN**: **`541563`**
* **Live Asterisk (`*`) Masking**: As you type each digit (`5`, `4`, `1`, `5`, `6`, `3`) on Windows CMD, Linux, or Termux, asterisks `******` appear live on screen! Backspace erases characters live.

---

## 👤 2. How to Add a New Registered User

Adding a new user takes less than 1 minute by modifying [`config.py`](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py).

### 📝 Step 1: Open `config.py`
In your code editor, open `config.py` and scroll to lines 26-42.

---

### 📝 Step 2: Add New User to `USER_NAMES`
Add your new user's Mobile Number or Email ID and Display Name to the `USER_NAMES` dictionary:

```python
USER_NAMES = {
    "7044015007": "Sumanta Halder",
    "8617383566": "Sujata Mondal",
    "7908555852": "Tasapur Rahaman",
    "gexowo4534@candaba.com": "Gsgs Sdgr",
    "borkej@smanthaai.online": "Bgdh Hdfh",
    "9876543210": "Ramesh Kumar",  # 👈 ADD YOUR NEW USER HERE (ID: Name)
}
```

---

### 📝 Step 3: Add Password to `USER_CREDENTIALS_ENCRYPTED`
Add your new user's Mobile/Email ID and Password to `USER_CREDENTIALS_ENCRYPTED`:

#### 🔹 Method A: Plain Text Password (Easiest)
You can type the password directly in plain text:
```python
USER_CREDENTIALS_ENCRYPTED = {
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7908555852": "ENC256:S0R5KItAxBw=",
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
    "9876543210": "Ramesh@2026",  # 👈 ADD YOUR PLAIN PASSWORD HERE
}
```

#### 🔒 Method B: 256-Bit Cryptographic Encryption (Recommended for Security)
To encrypt your password with 256-bit AES/SHA-256 cryptography before saving:

Run this command in terminal:
```bash
python -c "from utils.security import encrypt_password; print(encrypt_password('Ramesh@2026'))"
```
Output: `ENC256:a8F9k2Lp9Qx...`

Copy `ENC256:a8F9k2Lp9Qx...` and paste it into `USER_CREDENTIALS_ENCRYPTED`!

---

### 🚀 Step 4: Run & Select New User!

When you run `python main.py` or double-click `diksha+.bat`:

```text
===================================================================
 🔒 DIKSHA+ SECURITY ACCESS VERIFICATION (256-BIT SHA-256)
===================================================================
[Security] Enter 6-digit Security PIN to unlock: ******
 ✔ [Security] 256-Bit Cryptographic PIN verified! Access granted.

[Login] Registered accounts:
  [1] Sumanta Halder           : 7044015007
  [2] Sujata Mondal            : 8617383566
  [3] Tasapur Rahaman          : 7908555852
  [4] Gsgs Sdgr                : gexowo4534@candaba.com
  [5] Bgdh Hdfh                : borkej@smanthaai.online
  [6] Ramesh Kumar             : 9876543210  <--- YOUR NEW USER IS NOW ACTIVE!
-------------------------------------------------------------------
Select account [1-6] (or press Enter for Account #1): 6
```

---

## ❌ 3. How to Delete a Registered User

To delete an account:
1. Open [`config.py`](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py).
2. Delete the user's line from `USER_NAMES` and `USER_CREDENTIALS_ENCRYPTED`.
3. Save `config.py`.
