# 🚀 Quick Deploy Guide - Python Vector API

## Option 1: Render.com (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
cd python-vector-api
git init
git add .
git commit -m "feat: Python Vector API"
git push origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `fitrecipes-vector-api`
   - **Environment**: Docker
   - **Branch**: main
   - **Region**: Singapore
   - **Instance Type**: Free

5. Add Environment Variables:
   ```
   DATABASE_URL=your_supabase_url
   PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGc...
   ```

6. Click "Create Web Service"
7. Wait 5-10 minutes
8. Done! Your API: `https://fitrecipes-vector-api.onrender.com`

### Step 3: Test
```bash
curl https://fitrecipes-vector-api.onrender.com/health
```

---

## Option 2: Railway.app (Best Performance)

### Step 1: Install CLI
```bash
brew install railway
railway login
```

### Step 2: Deploy
```bash
cd python-vector-api
railway init
railway up

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set PYTHON_API_KEY="vsk_..."

# Create public URL
railway domain
```

---

## Option 3: Fly.io (Advanced)

### Step 1: Install CLI
```bash
brew install flyctl
flyctl auth login
```

### Step 2: Deploy
```bash
cd python-vector-api
flyctl launch
flyctl secrets set DATABASE_URL="postgresql://..."
flyctl deploy
```

---

## 🔧 Update Backend to Use Deployed API

### In your Hono.js Backend (.env):
```bash
# Production
PYTHON_API_URL=https://fitrecipes-vector-api.onrender.com

# API Key (same as Python API)
PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
```

### Test Connection:
```typescript
import { checkVectorApiHealth } from './utils/vectorApi';

const health = await checkVectorApiHealth();
console.log('Python API:', health.status);
```

---

## 📊 Platform Comparison

| Platform | Deploy Time | Cold Start | Cost/mo |
|----------|-------------|------------|---------|
| **Render** | 10 min | 30-50s | $0 (Free) |
| **Railway** | 5 min | None | $5 credit |
| **Fly.io** | 8 min | None | $0 (3 VMs) |

**Recommendation**: Start with **Render.com** (easiest) → Upgrade to **Railway** if you need better performance

---

## ✅ Checklist

- [ ] Push code to GitHub
- [ ] Deploy on Render/Railway/Fly.io
- [ ] Set environment variables
- [ ] Test `/health` endpoint
- [ ] Update backend `.env` with deployed URL
- [ ] Test integration from backend
- [ ] Monitor logs for errors

---

## 🆘 Need Help?

See full guide: `DEPLOYMENT_GUIDE.md`

Common issues:
- **Build failed**: Check `requirements.txt` and Dockerfile
- **Cold start**: Normal for Render free tier
- **Connection refused**: Check `PYTHON_API_URL` in backend .env
