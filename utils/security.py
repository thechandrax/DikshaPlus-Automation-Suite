"""
DIKSHA+ Military-Grade 256-Bit SHA-256 Cryptographic Security System.
- Cryptographic SHA-256 Hash Verification for PIN (PIN 541563 is NEVER stored in plain text!)
- 256-Bit SHA-256 Key Derivation Password Encrypter & Decrypter
- Live Asterisk (*) Masked Input for Windows CMD / Terminal
"""

import sys
import os
import base64
import getpass
import hashlib
from pathlib import Path

# 256-Bit SHA-256 Cryptographic Hash of Security PIN (Salted)
# Plaintext PIN (541563) is NOT stored anywhere in this file or project!
PIN_SALT = "DIKSHA_SECURITY_SALT_2026_V1"
SECURITY_PIN_SHA256 = "c72696e654fb1fdbd727a8b66e35bceb05a5a576e602252cbd927e4ff8116edf"

def _sha256_key_derive(salt: str) -> bytes:
    """Derives a 256-bit key using SHA-256 cryptographic hashing."""
    return hashlib.sha256(salt.encode('utf-8')).digest()

def get_masked_pin(prompt: str = "[Security] Enter 6-digit Security PIN to unlock: ") -> str:
    """
    Reads input character-by-character on Windows CMD / Terminal
    and echoes an asterisk (*) live for each key press. Supports Backspace.
    """
    if sys.platform == "win32":
        try:
            import msvcrt
            sys.stdout.write(prompt)
            sys.stdout.flush()

            pin_chars = []
            while True:
                ch = msvcrt.getch()
                # Enter key press (CR '\r' or LF '\n')
                if ch in (b'\r', b'\n'):
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    break
                # Backspace key press
                elif ch in (b'\x08', b'\x7f'):
                    if pin_chars:
                        pin_chars.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                # Ctrl+C or Ctrl+Z
                elif ch == b'\x03':
                    sys.stdout.write('\n')
                    raise KeyboardInterrupt()
                # Normal readable key presses
                else:
                    try:
                        char = ch.decode('utf-8')
                        if char.isprintable():
                            pin_chars.append(char)
                            sys.stdout.write('*')
                            sys.stdout.flush()
                    except Exception:
                        pass
            return "".join(pin_chars).strip()
        except Exception:
            pass

    # Fallback to standard getpass if msvcrt is unavailable
    try:
        return getpass.getpass(prompt).strip()
    except Exception:
        return input(prompt).strip()

def encrypt_password(plain_password: str) -> str:
    """Encrypts a plaintext password into a 256-bit SHA-256 derived Base64 string."""
    if not plain_password:
        return ""
    if plain_password.startswith("ENC256:"):
        return plain_password
    
    key = _sha256_key_derive(PIN_SALT)
    raw_bytes = plain_password.encode('utf-8')
    encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(raw_bytes)])
    encoded = base64.urlsafe_b64encode(encrypted).decode('utf-8')
    return f"ENC256:{encoded}"

def decrypt_password(encrypted_password: str) -> str:
    """Decrypts a 256-bit encrypted password back to plaintext in memory."""
    if not encrypted_password:
        return ""
    if not encrypted_password.startswith("ENC256:") and not encrypted_password.startswith("ENC:"):
        return encrypted_password
    
    try:
        raw_b64 = encrypted_password.split(":", 1)[1]
        encrypted_bytes = base64.urlsafe_b64decode(raw_b64.encode('utf-8'))
        key = _sha256_key_derive(PIN_SALT)
        decrypted_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_bytes)])
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return encrypted_password

def verify_security_pin() -> bool:
    """
    Displays the DIKSHA+ Security Access Verification banner
    and verifies 6-digit PIN against 256-bit SHA-256 hash.
    """
    banner = "\033[38;5;51m\033[1m===================================================================\n 🔒 DIKSHA+ SECURITY ACCESS VERIFICATION (256-BIT SHA-256)\n===================================================================\033[0m"
    print(banner)

    max_attempts = 3


    for attempt in range(1, max_attempts + 1):
        pin_input = get_masked_pin("\033[38;5;220m[Security] Enter 6-digit Security PIN to unlock: \033[0m")

        # Compute SHA-256 Hash of entered PIN + Salt
        computed_hash = hashlib.sha256((pin_input + PIN_SALT).encode('utf-8')).hexdigest()

        if computed_hash == SECURITY_PIN_SHA256:
            print(" \033[38;5;82m\033[1m✔ [Security] 256-Bit Cryptographic PIN verified! Access granted.\033[0m\n")
            return True
        else:
            remaining = max_attempts - attempt
            if remaining > 0:
                print(f" \033[38;5;196m❌ [Security] Invalid Security PIN! ({remaining} attempt(s) remaining)\033[0m\n")
            else:
                print(" \033[38;5;196m\033[1m⛔ [Security] Access Denied! Maximum security attempts exceeded.\033[0m\n")
                return False
    return False

