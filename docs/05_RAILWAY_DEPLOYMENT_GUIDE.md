# 🚀 Railway Cloud 24/7 Deployment Guide

This guide provides step-by-step instructions for deploying **DIKSHA+ Automation Suite** to **[Railway.app](https://railway.app)** so your automation runs 24/7 in the cloud without requiring your local PC/laptop to stay powered on.

---

## 📑 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step-by-Step Deployment Instructions](#2-step-by-step-deployment-instructions)
3. [How to Select User & Course on Railway](#3-how-to-select-user--course-on-railway)
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

---

## 🎛️ 3. How to Select User & Course on Railway

Because cloud servers run headlessly without a manual keyboard input prompt, you can easily control **which User** and **which Course** to run using **Railway Environment Variables**:

### In Railway Dashboard $\rightarrow$ **Variables** Tab:

| Variable Name | Value Examples | Description |
| :--- | :--- | :--- |
| **`SELECTED_USER`** | `1`, `2`, `3`, `4`, `5`, or `all` | Selects User #1, #2, #3, etc. Set to `all` to process all registered users automatically. (Default: `1`) |
| **`SELECTED_COURSE`** | `1`, `2`, `3`, or `all` | Selects Course #1, #2, etc. Set to `all` to process all ongoing courses automatically. (Default: `1`) |

### Example Scenarios:
* **To process User #2 and Course #1**:  
  Set `SELECTED_USER` = `2` and `SELECTED_COURSE` = `1`.
* **To process ALL Users and ALL Courses automatically**:  
  Set `SELECTED_USER` = `all` and `SELECTED_COURSE` = `all`.

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
