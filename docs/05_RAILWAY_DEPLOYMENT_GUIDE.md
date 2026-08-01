# ☁️ RAILWAY CLOUD DEPLOYMENT GUIDE

This document provides complete instructions for deploying, configuring, controlling, and monitoring **DIKSHA+ Automation Suite** on **Railway.app** for 24/7 cloud execution.

---

## ⚙️ 1. Standby Control & Manual Execution Variables

DIKSHA+ features **0% automatic default runs**. All fallback code that automatically selected User #1 or Course #1 has been completely removed.

### ⏸️ Putting Railway in Standby / Pause Mode
To keep Railway on standby without executing any browser automation:
* Go to Railway Dashboard $\rightarrow$ **Variables** tab $\rightarrow$ Add:
  * `AUTO_START` = `False`
* DIKSHA+ will log:
  ```text
  ===================================================================
   ⏸️ [RAILWAY STANDBY MODE] AUTO_START is set to False.
   Container is standing by on Railway Cloud. Automation paused.
  ===================================================================
  ```

### 🎯 Flexible User & Course Selection Options

You can specify users and courses in Railway Variables using **Index Numbers**, **Names**, **Emails**, or **Keywords**:

1. **`SELECTED_USER` Options**:
   * **By Index Number**: `SELECTED_USER` = `1` (or `2`, `3`, `all`)
   * **By Account Name**: `SELECTED_USER` = `Gsgs Sdgr` (or `Sujata`, `Tasapur`)
   * **By Email / Mobile**: `SELECTED_USER` = `gexowo4534@candaba.com` (or `8617383566`)

2. **`SELECTED_COURSE` Options**:
   * **By Index Number**: `SELECTED_COURSE` = `1` (or `2`, `3`, `all`)
   * **By Course Title / Keyword**: `SELECTED_COURSE` = `Power of Audio` (or `audio`, `NEP 2020`, `NEP`, `Action Research`)


---

## 🔑 2. Do I Need to Add Gemini API Keys in Railway Variables?

### **Short Answer**: **NO, IT IS NOT NECESSARY!**

1. **Option A (Default - Built-In & Recommended)**:
   * Your Gemini API keys are already **256-bit AES encrypted directly inside `config.py`** (`GEMINI_API_KEYS_ENCRYPTED = ["ENC256:...", ...]`).
   * When deployed on Railway, the engine runs automatically inside the Docker container and decrypts the keys in memory.
   * **Zero Setup Required**: You do NOT need to set any API key variables in Railway!

2. **Option B (Optional Environment Variable Override)**:
   * If you ever want to provide a custom API key via Railway without touching code:
   * Go to Railway **Variables** tab and add:
     * `GOOGLE_API_KEY` = `your_gemini_api_key_here` (or `GEMINI_API_KEY`)
   * `config.py` will automatically detect your variable and use it as top priority!

---

## 🤖 3. Smart Headless Auto-Detection

DIKSHA+ automatically detects Railway Cloud Docker environments:
* On your local computer desktop: `HEADLESS = False` (Visible browser window so you can watch live!).
* On Railway Cloud: `HEADLESS = True` (Automated headless background container).

---

## 🛠️ 4. Docker Build & Playwright Version Matching Fixes

### 1. Missing `requirements.txt` Fix:
* **Issue**: Setting Root Directory = `railway` scoped Docker's build context strictly to `railway/`.
* **Fix**: Leave **Root Directory** = **EMPTY / BLANK** (or `/`). Railway will automatically detect the root `Dockerfile` and build the complete repository!

### 2. Playwright Executable Version Match Fix:
* Pinned `playwright==1.40.0` in both `requirements.txt` and `railway/requirements.txt`.
* Included `RUN pip install --no-cache-dir -r requirements.txt && playwright install chromium` in Dockerfile.

---

## 🚀 5. Step-by-Step Deployment Instructions

1. **Connect GitHub Repository**:
   * Open [Railway.app](https://railway.app) dashboard.
   * Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
   * Select `thechandrax/DikshaPlus-Automation-Suite`.

2. **Configure Settings**:
   * Go to **Settings** $\rightarrow$ **Root Directory** $\rightarrow$ Leave **EMPTY / BLANK**!

3. **Configure Variables (Optional)**:
   * `AUTO_START` = `False` (for Standby mode) or `True` (to run).
   * `SELECTED_USER` = `1` (or `2`, `3`, `all`).
   * `SELECTED_COURSE` = `2` (or `1`, `3`, `all`).

4. **Deploy**:
   * Click **Deploy**. Railway will build the container and manage cloud execution!
