# 🚆 Railway Cloud Deployment Guide

This guide explains how to deploy **DIKSHA+ Automation Suite** to [Railway.app](https://railway.app) for automated cloud execution.

---

## 🚀 Step-by-Step Railway Deployment

### Step 1: Create a Railway Account & New Project
1. Go to [https://railway.app](https://railway.app) and sign in with your GitHub account.
2. Click **"+ New Project"**.
3. Select **"Deploy from GitHub repo"**.

### Step 2: Select GitHub Repository
1. Select your repository: `thechandrax/DikshaPlus-Automation-Suite`.
2. Railway will automatically detect the **`Dockerfile`** and **`railway.json`** files.

### Step 3: Deploy & Monitor
1. Click **"Deploy Now"**.
2. Railway will build the Playwright container and execute:
   ```bash
   python main.py --headless --skip-pin --all-users
   ```
3. Check the **Deploy Logs** tab in Railway to see live execution logs!

---

## ⚙️ Environment Variables (Optional)
If you want to override settings on Railway, you can add environment variables under the **Variables** tab in Railway:
* `HEADLESS=True`
* `AUTO_SUBMIT=True`
