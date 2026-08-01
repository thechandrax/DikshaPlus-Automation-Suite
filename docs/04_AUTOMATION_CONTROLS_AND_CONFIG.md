# ⚙️ Automation Controls & Configuration Guide

This guide explains all configuration settings, directory paths, and runtime behavior controls inside `config.py` for **DIKSHA+ Automation Suite**.

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

> **Note**: Legacy `data/screenshots/` has been removed. All screenshots are stored exclusively inside `output/screenshots/`.

---

## 🔑 2. Gemini AI Live Solver Configuration

`config.py` dynamically loads the Gemini API Key from environment variables or local secret files:

```python
# Gemini AI Live Solver Configuration
GEMINI_API_KEY = _load_gemini_key()
AI_LIVE_SOLVER_ENABLED = True
```

### Key Lookup Priority:
1. `GEMINI_API_KEY` environment variable.
2. `gemini_key.txt` local secret file (ignored by Git).
3. `.env` file (ignored by Git).

---

## 🕹️ 3. Automation Pacing & Behavior Controls

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

## 🔐 4. Multi-User Credentials Registry

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
