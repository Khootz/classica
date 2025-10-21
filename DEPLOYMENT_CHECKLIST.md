# 🚀 Quick Deployment Checklist

## ✅ Part 1: DONE - Pushed to GitHub
- Repository: https://github.com/Khootz/classica
- All sensitive data protected (API keys in .env, not committed)

---

## 📋 Part 2: Deploy Backend to Render

### You'll Need:
- Your Landing AI API Key: `cGk4MjV1Y2E0ZTZtcHoyNW1oeG5zOmNxZTNMajJQeWhEVlVSS251bVBuUjU1aWMzdzZ2ZEJ5`
- Your OpenRouter API Key: `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`

### Steps:
1. Go to https://render.com and sign up with GitHub
2. Click "New +" → "Web Service"
3. Select your `classica` repository
4. Configure:
   ```
   Name: classica-backend
   Region: Oregon (US West) or closest to you
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: ./build.sh
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

5. **Add Environment Variables** (Click "Environment" tab):
   ```
   LANDINGAI_API_KEY = cGk4MjV1Y2E0ZTZtcHoyNW1oeG5zOmNxZTNMajJQeWhEVlVSS251bVBuUjU1aWMzdzZ2ZEJ5
   OPENROUTER_API_KEY = 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
   ```

6. Click "Create Web Service"
7. Wait 5-10 minutes for deployment
8. **Copy your backend URL** (e.g., `https://classica-backend.onrender.com`)

---

## 🎨 Part 3: Deploy Frontend to Vercel

### Steps:
1. Go to https://vercel.com and sign up with GitHub
2. Click "Add New" → "Project"
3. Import `classica` repository
4. Configure:
   ```
   Framework Preset: Next.js (auto-detected)
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

5. **Add Environment Variable** (Click "Environment Variables"):
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://classica-backend.onrender.com
   ```
   (Replace with your actual Render backend URL from step 2.8)

6. Click "Deploy"
7. Wait 2-5 minutes
8. **Your app is live!** Get the URL (e.g., `https://classica.vercel.app`)

---

## 🔧 Part 4: Update CORS (Important!)

After both are deployed, you need to update the backend CORS:

1. In your local code, edit `backend/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://classica.vercel.app",  # Your actual Vercel URL
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

3. Render will automatically redeploy (takes 2-3 minutes)

---

## 🎉 You're Done!

Your app is now live at:
- **Frontend**: https://classica.vercel.app (or your custom URL)
- **Backend**: https://classica-backend.onrender.com

Share it with the world! 🌍

---

## ⚠️ Important Notes:

1. **Render Free Tier**: Backend spins down after 15 min of inactivity. First request takes 30-60 sec.
2. **Database**: SQLite data is ephemeral on Render (resets on redeploy). Consider PostgreSQL for persistence.
3. **Uploads**: File uploads stored on Render may be lost on redeploy. Consider AWS S3 or Cloudinary.

---

## 🐛 Troubleshooting:

- **Backend build fails**: Check Render logs, may need to fix dependencies
- **Frontend can't connect**: Verify CORS is updated and environment variable is set
- **502 errors**: Backend may be spinning up (wait 60 seconds)

For detailed guide, see: DEPLOYMENT.md
