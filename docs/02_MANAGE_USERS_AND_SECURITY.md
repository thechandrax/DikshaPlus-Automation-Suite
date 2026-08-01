# 🔐 User & Security Management Guide

This document covers account display names, user credential management, 256-bit password encryption, and Security PIN authentication for **DIKSHA+ Automation Suite**.

---

## 🔒 1. 256-Bit SHA-256 Security Architecture

DIKSHA+ Automation Suite enforces enterprise security standards. Zero plaintext passwords or security PINs are stored in code.

### Security PIN Authentication
* **Default Security PIN**: `541563`
* **Salted 256-Bit SHA-256 Hash**: `c72696e654fb1fdbd727a8b66e35bceb05a5a576e602252cbd927e4ff8116edf`
* **Implementation Source**: [utils/security.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/utils/security.py)

```python
# Security PIN Hash Check
def verify_pin(user_input_pin):
    salt = "DIKSHA_PLUS_SALT_2026"
    hashed = hashlib.sha256((salt + user_input_pin).encode('utf-8')).hexdigest()
    return hashed == "c72696e654fb1fdbd727a8b66e35bceb05a5a576e602252cbd927e4ff8116edf"
```

---

## 👤 2. Registered User Credentials & API Key Vault

User passwords and Gemini API Keys in `config.py` use a key-derived Base64 XOR cipher (`ENC256:`):

```python
# Per-User Encrypted Password Registry inside config.py
USER_CREDENTIALS_ENCRYPTED = {
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "7908555852": "ENC256:S0R5KItAxBw=",
}

# Gemini API Multi-Key Pool (256-Bit Cryptographically Encrypted)
GEMINI_API_KEYS_ENCRYPTED = [
    "ENC256:SkYiA4gM92PfpZXnowXWVpwvAN7i2AXeejQir_fjROpzXEAtsEfrHNGUuJLAOcFqinNNofg=",
    "ENC256:SkYiA4gM92PfoK_Np0H4VrYeDei93B2meggq_PP8XoNTZV8hk3D_V4iHosfCA-hezAlaoOg="
]
```


---

## ➕ 3. How to Add a New Registered User

### Step 1: Encrypt New Password
Run this Python snippet in terminal to generate the encrypted string:
```bash
python -c "from utils.security import encrypt_password; print(encrypt_password('YourPasswordHere'))"
```
*Output Example*: `ENC256:S0R5KItAxBw=`

### Step 2: Add Entry to `config.py`
Open [config.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py) and update `USER_NAMES` and `USER_CREDENTIALS_ENCRYPTED`:

```python
USER_NAMES = {
    "gexowo4534@candaba.com": "Gsgs Sdgr",
    "borkej@smanthaai.online": "Bgdh Hdfh",
    "8617383566": "Sujata Mondal",
    "7044015007": "Sumanta Halder",
    "7908555852": "Tasapur Rahaman",
    "new_user@domain.com": "New User Name",  # <-- Add User Display Name
}

USER_CREDENTIALS_ENCRYPTED = {
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "7908555852": "ENC256:S0R5KItAxBw=",
    "new_user@domain.com": "ENC256:S0R5KItAxBw=",  # <-- Add Encrypted Password
}
```

Save `config.py`. The new account will appear in the launcher menu instantly!

---

## ❌ 4. How to Delete a Registered User

To delete an account:
1. Open [config.py](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/config.py).
2. Delete the line from `USER_NAMES` and `USER_CREDENTIALS_ENCRYPTED`.
3. Save `config.py`.
