# ☁️ Railway Cloud Deployment Guide

This guide explains how to deploy **DIKSHA+ Automation Suite** to **Railway.app** for 24/7 cloud execution.

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

3. **Add Environment Variables**:
   In Railway **Variables** tab, add:
   * `GEMINI_API_KEY` = `your_gemini_api_key_here`
   * `HEADLESS` = `True`

4. **Deploy**:
   Railway will automatically build the Docker container and start headless automated execution!
