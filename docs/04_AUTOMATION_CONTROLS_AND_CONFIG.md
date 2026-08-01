# ⚙️ Automation Controls & Configuration Guide

This guide explains all configuration settings, directory paths, keyboard hotkey controls, and runtime behavior controls inside `config.py` for **DIKSHA+ Automation Suite**.

---

## 📁 1. Directory Structure Configuration

All directories are created dynamically upon engine startup:

```python
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"  # Single official screenshot folder
COURSES_DIR = DATA_DIR / "courses"
```

> **Note**: Legacy `data/screenshots/` and temporary `scratch/` folders have been removed. All output screenshots are stored exclusively inside `output/screenshots/`.

---

## ⏸️ 2. Hot-Key Live Pause & Resume Controls

DIKSHA+ includes an active background daemon thread (`msvcrt`) listening for keyboard shortcuts in the terminal window:

| Hotkey | Action | Terminal Output |
| :--- | :--- | :--- |
| **`P`** | Toggle Pause / Resume | `⏸️ [AUTOMATION PAUSED] Press 'P' or 'Spacebar' in terminal to RESUME...` |
| **`Spacebar`** | Toggle Pause / Resume | `▶️ [AUTOMATION RESUMED] Continuing DIKSHA execution...` |

When paused, Playwright safely holds execution without missing server sync checkmarks or dropping browser context. Pressing `P` or `Spacebar` again resumes execution instantly!

---

## 🔑 3. Gemini AI Multi-Key Pool Configuration (`config.py`)

`config.py` dynamically decrypts and loads the Gemini API Key Pool from 256-bit encrypted ciphers and environment variables:

```python
# Gemini AI Multi-API Key Pool (256-Bit Cryptographically Encrypted)
GEMINI_API_KEYS_ENCRYPTED = [
    "ENC256:SkYiA4gM92PfpZXnowXWVpwvAN7i2AXeejQir_fjROpzXEAtsEfrHNGUuJLAOcFqinNNofg=",
    "ENC256:SkYiA4gM92PfoK_Np0H4VrYeDei93B2meggq_PP8XoNTZV8hk3D_V4iHosfCA-hezAlaoOg="
]

GEMINI_API_KEYS = _load_gemini_keys()
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""
AI_LIVE_SOLVER_ENABLED = True
```

### Key Resolution Priority (per Google API Docs):
1. `GOOGLE_API_KEY` environment variable.
2. `GEMINI_API_KEY` environment variable.
3. 256-bit encrypted key pool in `config.py` (`GEMINI_API_KEYS_ENCRYPTED`).

---

## 🕹️ 4. Automation Pacing & Behavior Controls

| Setting | Default Value | Description |
| :--- | :--- | :--- |
| `HEADLESS` | `False` | Set `True` for cloud/background runs, `False` to watch browser GUI. |
| `SLOMO_MS` | `500` | Slow-motion delay between Playwright actions (ms). |
| `MIN_VIDEO_WATCH_SECONDS` | `30` | Minimum watch duration for video activities. |
| `MIN_PDF_READ_SECONDS` | `10` | Minimum duration for PDF reading simulation. |
| `SERVER_SYNC_TIMEOUT_SECONDS` | `20` | Timeout waiting for server progress checkmark verification. |
| `AUTOMATIC_FINAL_SUBMIT` | `True` | Automatically clicks quiz `Review & Submit` and `Submit All` buttons. |
| `KEEP_BROWSER_OPEN` | `True` | Keeps browser open after execution finishes so browser window doesn't close. |

---

## 🔐 5. Multi-User Credentials Registry

`config.py` maintains an encrypted user registry dynamically decrypted in memory using 256-Bit cryptographic security (`utils/security.py`):

```python
USER_CREDENTIALS_ENCRYPTED = {
    "gexowo4534@candaba.com": "ENC256:fld4G4dW0nfblr_x1FjG",
    "borkej@smanthaai.online": "ENC256:e1J6I4wX8GOpgqbQpiL9",
    "8617383566": "ENC256:S0R5KItAxBw=",
    "7044015007": "ENC256:S0R5L4ta0UzY",
    "7908555852": "ENC256:S0R5KItAxBw=",
}
```
