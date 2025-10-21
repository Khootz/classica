# 🚀 Deployment Guide

## Overview
- **Frontend**: Vercel (Next.js)
- **Backend**: Render (FastAPI)

---

## Part 1: ✅ Code is on GitHub
Repository: https://github.com/Khootz/classica

---

## Part 2: Deploy Backend to Render

1. **Sign up at https://render.com** with GitHub
2. Click **"New +" → "Web Service"**
3. Select your **`classica`** repository
4. Configure:
   - **Name**: `classica-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

5. **Add Environment Variables** (in Render dashboard):
   - `LANDINGAI_API_KEY` = [Your Landing AI API Key]
   - `OPENROUTER_API_KEY` = [Your OpenRouter API Key]

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. **Copy your backend URL** (e.g., `https://classica-backend.onrender.com`)

---

## Part 3: Deploy Frontend to Vercel

1. **Sign up at https://vercel.com** with GitHub
2. Click **"Add New" → "Project"**
3. Import your **`classica`** repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - Build/Output settings should auto-detect

5. **Add Environment Variable**:
   - `NEXT_PUBLIC_API_URL` = [Your Render backend URL from Part 2, step 8]

6. Click **"Deploy"**
7. Wait 2-5 minutes
8. **Your app is live!**

---

## Part 4: Update CORS (Important!)

**✅ CORS is already configured!** 

The backend now accepts requests from:
- `http://localhost:3000` (local development)
- `https://classica.vercel.app` (your production frontend)
- `https://classica-frontend.vercel.app` (alternate Vercel URL)

If your Vercel URL is different, edit `backend/main.py` line 20 to add your actual URL.

---

## 🎉 Done!

Your app is live at:
- **Frontend**: Your Vercel URL
- **Backend**: Your Render URL

---

## ⚠️ Important Notes

- **Render Free Tier**: Spins down after 15 min inactivity
- **Database**: SQLite is ephemeral on Render (resets on redeploy)
- **File Uploads**: May be lost on redeploy - consider cloud storage

---

## 🐛 Troubleshooting

### Backend 502 Errors
1. **Wait 60-90 seconds** - Render free tier spins down after inactivity
2. Check Render logs for errors:
   - Go to Render dashboard → Your service → Logs
3. Verify environment variables are set:
   - `LANDINGAI_API_KEY`
   - `OPENROUTER_API_KEY`
4. Check health endpoint: `https://classica-backend.onrender.com/health`

### Frontend "Failed to fetch" Errors
1. **Verify `NEXT_PUBLIC_API_URL` in Vercel**:
   - Go to Vercel → Project Settings → Environment Variables
   - Should be: `https://classica-backend.onrender.com` (no trailing slash)
2. **Redeploy frontend** after changing env vars:
   - Vercel → Deployments → Redeploy
3. **Check CORS**: Your Vercel URL must match one in `backend/main.py` line 20
4. **Check browser console** (F12) for exact error message

### Build Failures
- **Render build timeout**: Should be fixed now with lightweight requirements
- **Missing dependencies**: Check that `build.sh` uses `requirements-render.txt`
- **Permission errors**: Verify `build.sh` has execute permissions (should be automatic)

### First Request Takes Long Time
- Normal! Render free tier spins down after 15 minutes of inactivity
- First request wakes it up (can take 30-60 seconds)
- Consider upgrading to paid tier for 24/7 availability
