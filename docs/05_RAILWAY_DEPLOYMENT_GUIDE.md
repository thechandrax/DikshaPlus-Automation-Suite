# ☁️ RAILWAY CLOUD DEPLOYMENT GUIDE

This guide explains how to deploy **DIKSHA+ Automation Suite** to **Railway.app** for 24/7 automated cloud execution.

---

## 🛠️ Fixing Docker Build Error (`/requirements.txt: not found`)

If you encountered this error during deployment:
```text
Build Failed: build daemon returned an error < failed to solve: failed to compute cache key: ... "/requirements.txt": not found >
```

### **Root Cause & Solution**:
1. **Root Cause**: Setting **Root Directory** = `railway` in Railway settings scoped Docker's build context strictly to `railway/`. Since `requirements.txt` was only at root level, Docker threw a missing file error.
2. **The Fix**:
   * We added `requirements.txt` inside `railway/` **AND** added a root-level `Dockerfile` to the repository!
   * **In Railway Settings**: Set **Root Directory** to **EMPTY / BLANK** (or `/`). Railway will automatically detect root `Dockerfile` and build the entire repository in 1 click!

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

## 🚀 Steps to Deploy on Railway.app (1-Click)

1. **Connect GitHub Repository**:
   * Open [Railway.app](https://railway.app) dashboard.
   * Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
   * Select `thechandrax/DikshaPlus-Automation-Suite`.

2. **Configure Root Directory in Railway**:
   * Go to **Settings** $\rightarrow$ **Root Directory** $\rightarrow$ Leave **EMPTY / BLANK**!

3. **Deploy**:
   * Click **Deploy**. Railway will automatically detect `Dockerfile`, build the container, and start headless automated execution!
