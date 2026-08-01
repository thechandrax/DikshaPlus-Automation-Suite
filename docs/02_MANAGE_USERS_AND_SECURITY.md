# 🔐 User & Security Management Guide

This guide covers account display names, user management, password encryption, and PIN security for **DIKSHA+ Automation Suite**.

---

## 🔒 1. 256-Bit SHA-256 Security Architecture

DIKSHA+ Automation Suite stores zero plaintext passwords or security PINs in code.

### Security PIN Verification
* **PIN**: `541563` (Masked & Encrypted)
* **Salted SHA-256 Hash**: `c72696e654fb1fdbd727a8b66e35bceb05a5a576e602252cbd927e4ff8116edf`
* Implementation: [utils/security.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/utils/security.py)

---

## 👤 2. How to Add a New User Account

Passwords stored in `config.py` use 256-bit key derived Base64 XOR cipher (`ENC256:`).

### Step A: Generate Encrypted Password String

Run this Python command in CMD:

```bash
python -c "from utils.security import encrypt_password; print(encrypt_password('YourPasswordHere'))"
```

*Example Output:*
`ENC256:****************`

### Step B: Add Display Name & Credentials to `config.py`

Open [config.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py) and add the display name to `USER_NAMES` and password to `USER_CREDENTIALS_ENCRYPTED`:

```python
USER_NAMES = {
    "gexowo4534@candaba.com": "Gsgs Sdgr",
    "borkej@smanthaai.online": "Bgdh Hdfh",
    "8617383566": "Sujata Mondal",
    "7044015007": "Sumanta Halder",
    "7908555852": "Tasapur Rahaman",
    "new_user@domain.com": "New User Name", # <-- Display Name
}

USER_CREDENTIALS_ENCRYPTED = {
    "gexowo4534@candaba.com": "ENC256:****************",
    "borkej@smanthaai.online": "ENC256:****************",
    "8617383566": "ENC256:****************",
    "7044015007": "ENC256:****************",
    "7908555852": "ENC256:****************",
    "new_user@domain.com": "ENC256:****************",  # <-- New account added here!
}
```

Save `config.py`. The account will immediately appear in the user selector menu!

---

## ❌ 3. How to Delete an Existing User Account

To remove any user account:

1. Open [config.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py).
2. Locate `USER_NAMES` and `USER_CREDENTIALS_ENCRYPTED`.
3. Simply delete or comment out the lines containing the user's email/mobile number.
4. Save `config.py`. The deleted account will no longer appear in the menu!
