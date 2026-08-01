# ☁️ RAILWAY CLOUD DEPLOYMENT GUIDE

This guide explains how to deploy **DIKSHA+ Automation Suite** to **Railway.app** for 24/7 automated cloud execution.

---

## 🔑 Do I Need to Add Gemini API Keys in Railway Variables?

### **Short Answer**: **NO, IT IS NOT NECESSARY!**

1. **Option A (Default - Built-In & Recommended)**:
   * Your Gemini API keys are already **256-bit AES encrypted directly inside `config.py`** (`GEMINI_API_KEYS_ENCRYPTED = ["ENC256:...", ...]`).
   * When deployed on Railway, the engine runs automatically inside the Docker container and decrypts the keys in memory.
   * **You do NOT need to set any environment variables in Railway!** It works 100% out of the box.

2. **Option B (Optional Environment Variable Override)**:
   * If you ever want to provide a custom or new API key via Railway without touching code:
   * Go to Railway **Variables** tab and add:
     * `GOOGLE_API_KEY` = `your_gemini_api_key_here`  (or `GEMINI_API_KEY`)
   * `config.py` will automatically detect your Railway environment variable and use it as top priority!

---

## 📁 1. Consolidated Railway Directory Structure (`railway/`)

All Railway configuration files are consolidated inside `railway/`:

```text
railway/
├── Dockerfile           # Headless Python + Playwright Linux container
├── railway.json         # Railway build & deployment configuration
└── .dockerignore        # Excludes temporary logs & screenshots
```

### `railway/railway.json` Specification:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

---

## 🚀 2. Steps to Deploy on Railway.app

1. **Connect GitHub Repository**:
   * Open [Railway.app](https://railway.app) dashboard.
   * Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
   * Select `thechandrax/DikshaPlus-Automation-Suite`.

2. **Configure Root Directory in Railway**:
   * Go to **Settings** $\rightarrow$ **Root Directory** $\rightarrow$ Set to `railway`.

3. **Deploy**:
   * Click **Deploy**. Railway will automatically build the Docker container and start headless automated execution!
