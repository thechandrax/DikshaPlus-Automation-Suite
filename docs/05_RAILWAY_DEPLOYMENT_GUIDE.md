# 🚀 Railway Cloud 24/7 Deployment Guide

This guide provides step-by-step instructions for deploying **DIKSHA+ Automation Suite** to **[Railway.app](https://railway.app)** so your automation runs 24/7 in the cloud without requiring your local PC/laptop to stay powered on.

---

## 📑 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step-by-Step Deployment Instructions](#2-step-by-step-deployment-instructions)
3. [How Railway Runs Your Project](#3-how-railway-runs-your-project)
4. [Monitoring Logs & Outputs](#4-monitoring-logs--outputs)
5. [Frequently Asked Questions (FAQ)](#5-frequently-asked-questions-faq)

---

## 1. Prerequisites

Before you begin, ensure you have:
* A **GitHub Account** with access to your repository:  
  **`https://github.com/thechandrax/DikshaPlus-Automation-Suite`**
* A free **[Railway.app](https://railway.app)** account (sign up with GitHub).

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Sign In to Railway
1. Go to **[https://railway.app](https://railway.app)**.
2. Click **Login** and select **Continue with GitHub**.

### Step 2: Create a New Project
1. On your Railway Dashboard, click the **`+ New Project`** button.
2. Select **`Deploy from GitHub repo`**.
3. Choose your repository: **`DikshaPlus-Automation-Suite`**.

### Step 3: Deploy Service
1. Click **Deploy Now**.
2. Railway will automatically detect the **[Dockerfile](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/Dockerfile)** and **[railway.json](file:///C:/Users/thego/.gemini/antigravity/scratch/Diksha+%20Automation%20Suite/railway.json)** in your repository.
3. Railway will start building the Playwright Python container image automatically.

### Step 4: Add Environment Variables (Optional)
If you want to customize execution options:
1. In your Railway service dashboard, click the **Variables** tab.
2. Add any custom keys if needed:
   * `HEADLESS` = `True`
   * `PYTHONUNBUFFERED` = `1`

---

## 3. How Railway Runs Your Project

* **Docker Build**: Railway builds a cloud container using `mcr.microsoft.com/playwright/python:v1.40.0-jammy` which has Chromium pre-installed.
* **Execution Command**:
  ```bash
  python main.py --headless --skip-pin --all-users
  ```
* **Auto-Restart**: If configured under `railway.json`, Railway will automatically restart the engine if DIKSHA server drops connection.

---

## 4. Monitoring Logs & Outputs

1. Go to your Railway project dashboard.
2. Click on the **Deployments** tab.
3. Select **View Logs** to watch real-time automation progress (login redirects, module scanning, video acceleration, and quiz submissions).

---

## 5. Frequently Asked Questions (FAQ)

### Q: Do I need to keep my laptop on?
**No.** Once deployed to Railway, the automation runs entirely on cloud servers. You can turn off your laptop, and the automation will continue running seamlessly.

### Q: How do I trigger a new run on Railway?
Whenever you push changes to your GitHub `main` branch, Railway automatically redeploys and runs the updated pipeline!
