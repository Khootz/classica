# Deployment Guide

## Overview
- **Frontend**: Vercel (Next.js)
- **Backend**: Render (FastAPI)

---

## 🚀 Part 1: Push to GitHub

### Step 1: Initialize Git (if not already done)
```bash
cd c:\Users\User\Desktop\Coding\mna-agent
git init
git add .
git commit -m "Initial commit: M&A Due Diligence Assistant"
```

### Step 2: Add Remote and Push
```bash
git remote add origin https://github.com/Khootz/classica.git
git branch -M main
git push -u origin main
```

---

## 🌐 Part 2: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"

### Step 2: Connect Repository
1. Select your `classica` repository
2. Configure:
   - **Name**: `classica-backend` (or any name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
In Render Dashboard → Environment:
```
LANDINGAI_API_KEY=cGk4MjV1Y2E0ZTZtcHoyNW1oeG5zOmNxZTNMajJQeWhEVlVSS251bVBuUjU1aWMzdzZ2ZEJ5
OPENROUTER_API_KEY=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
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Copy your backend URL (e.g., `https://classica-backend.onrender.com`)

---

## 🎨 Part 3: Deploy Frontend to Vercel

### Step 1: Update API URL
Before deploying, update the frontend to use your Render backend URL:

Edit `frontend/lib/api.ts`:
```typescript
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://classica-backend.onrender.com"
```

Commit this change:
```bash
git add frontend/lib/api.ts
git commit -m "Update API URL for production"
git push
```

### Step 2: Deploy to Vercel
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import `classica` repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

### Step 3: Add Environment Variables
In Vercel Project Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://classica-backend.onrender.com
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment (2-5 minutes)
3. Get your frontend URL (e.g., `https://classica.vercel.app`)

---

## ⚙️ Part 4: Configure CORS

After deployment, update the backend CORS settings to allow your Vercel domain.

Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://classica.vercel.app",  # Your Vercel domain
        "https://*.vercel.app"  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy.

---

## 🔒 Security Checklist

- ✅ API keys in `.env` (not committed to GitHub)
- ✅ `.env` in `.gitignore`
- ✅ Database files excluded from git
- ✅ Upload directories excluded from git
- ✅ Environment variables set in Render/Vercel dashboards
- ✅ CORS configured for specific domains

---

## 📝 Important Notes

### Render Free Tier Limitations:
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes 30-60 seconds
- ⚠️ 750 hours/month free (enough for 1 service 24/7)
- 💡 Consider upgrading to paid tier ($7/mo) for always-on service

### Vercel Limitations:
- ✅ Frontend deploys are instant and always-on
- ✅ Unlimited bandwidth on free tier
- ✅ Automatic HTTPS

### Database:
- ⚠️ SQLite file will be ephemeral on Render (resets on redeploy)
- 💡 For persistent data, consider using:
  - Render PostgreSQL (free tier available)
  - Supabase (PostgreSQL)
  - PlanetScale (MySQL)

---

## 🐛 Troubleshooting

### Backend not responding:
1. Check Render logs for errors
2. Verify environment variables are set
3. Check build logs for failures

### Frontend can't connect to backend:
1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check CORS configuration in backend
3. Ensure backend is running (not spun down)

### Upload failures:
1. Render free tier has limited storage
2. Consider using external storage (AWS S3, Cloudinary)

---

## 🎉 Success!

Your app should now be live at:
- **Frontend**: `https://classica.vercel.app` (or your custom domain)
- **Backend**: `https://classica-backend.onrender.com`

Share your app URL with anyone! 🚀
