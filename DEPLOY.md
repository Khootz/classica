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

After both are deployed:

1. Edit `backend/main.py` and update the CORS origins:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://your-app.vercel.app",  # Replace with your actual Vercel URL
           "https://*.vercel.app"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Commit and push:
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push
   ```

3. Render will automatically redeploy

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

- Backend build fails? Check Render logs
- Frontend can't connect? Verify CORS and environment variables
- 502 errors? Backend may be spinning up (wait 60 seconds)
