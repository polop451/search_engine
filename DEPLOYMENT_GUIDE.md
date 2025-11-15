# Python Vector API - Deployment Guide 🚀

## 🌟 แพลตฟอร์มแนะนำ (FREE Tier)

### 1. **Render.com** (แนะนำที่สุด ⭐⭐⭐⭐⭐)
- **Free Tier**: 750 ชั่วโมง/เดือน (พอเกิน)
- **RAM**: 512MB (พอดีสำหรับโมเดล ML)
- **Pros**: Auto-deploy จาก GitHub, SSL ฟรี, ง่ายมาก
- **Cons**: Cold start ~30-50 วินาที หลังไม่ใช้ 15 นาที
- **เหมาะสำหรับ**: Production-ready, มี custom domain ฟรี

### 2. **Railway.app** (เยี่ยมมาก ⭐⭐⭐⭐)
- **Free Tier**: $5 credit/เดือน (~500 ชั่วโมง)
- **RAM**: 512MB-1GB
- **Pros**: No cold start, deploy ง่าย, logs ดี
- **Cons**: Credit หมดต้องเติม
- **เหมาะสำหรับ**: Development + Light production

### 3. **Fly.io** (ดีแต่ซับซ้อนกว่า ⭐⭐⭐⭐)
- **Free Tier**: 3 shared CPU VMs ฟรี
- **RAM**: 256MB (น้อยไปหน่อย แต่พอใช้ได้)
- **Pros**: Global edge network, ไม่มี cold start
- **Cons**: ต้อง setup CLI, เรียนรู้ยากกว่า
- **เหมาะสำหรับ**: Advanced users

### 4. **Heroku** (ไม่แนะนำแล้ว ⭐⭐)
- **Free Tier**: ยกเลิกไปแล้ว (ต้องจ่าย $7/เดือน)
- **Pros**: ใช้ง่ายมาก
- **Cons**: ไม่ฟรี

---

## 🎯 Quick Start: Deploy บน Render.com

### ขั้นตอนที่ 1: เตรียมโปรเจค

```bash
cd python-vector-api

# ตรวจสอบว่าไฟล์ครบ
ls -la
# ต้องมี: Dockerfile, requirements.txt, app/, .env.example
```

### ขั้นตอนที่ 2: Push โค้ดขึ้น GitHub

```bash
# ถ้ายังไม่มี git repo
git init
git add .
git commit -m "feat: add Python Vector API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/python-vector-api.git
git push -u origin main
```

### ขั้นตอนที่ 3: Deploy บน Render

1. **สมัคร Render.com**:
   - ไปที่ https://render.com
   - Sign up ด้วย GitHub

2. **สร้าง Web Service**:
   - คลิก "New +" → "Web Service"
   - เชื่อมต่อ GitHub repository
   - เลือก repo: `python-vector-api`

3. **ตั้งค่า**:
   ```yaml
   Name: fitrecipes-vector-api
   Environment: Docker
   Region: Singapore (ใกล้สุด)
   Branch: main
   Dockerfile Path: ./Dockerfile
   Instance Type: Free
   ```

4. **เพิ่ม Environment Variables**:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGc...
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

5. **Deploy**:
   - คลิก "Create Web Service"
   - รอ 5-10 นาที (build Docker image)

6. **ทดสอบ**:
   ```bash
   # URL จะได้มาประมาณ: https://fitrecipes-vector-api.onrender.com
   
   curl https://fitrecipes-vector-api.onrender.com/health
   ```

---

## 🚀 Alternative: Deploy บน Railway.app

### ขั้นตอนที่ 1: Install Railway CLI

```bash
# macOS
brew install railway

# หรือใช้ npm
npm install -g @railway/cli
```

### ขั้นตอนที่ 2: Login

```bash
railway login
```

### ขั้นตอนที่ 3: Deploy

```bash
cd python-vector-api

# สร้างโปรเจคใหม่
railway init

# เพิ่ม environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set PYTHON_API_KEY="vsk_..."

# Deploy!
railway up
```

### ขั้นตอนที่ 4: เปิด Public URL

```bash
# สร้าง public domain
railway domain
```

---

## 🎯 Alternative: Deploy บน Fly.io

### ขั้นตอนที่ 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# หรือใช้ script
curl -L https://fly.io/install.sh | sh
```

### ขั้นตอนที่ 2: Login และสร้างแอป

```bash
cd python-vector-api

# Login
flyctl auth login

# สร้างแอป
flyctl launch
# เลือก: 
# - App name: fitrecipes-vector-api
# - Region: Singapore
# - RAM: 512MB
```

### ขั้นตอนที่ 3: ตั้งค่า Secrets

```bash
# เพิ่ม environment variables
flyctl secrets set DATABASE_URL="postgresql://..."
flyctl secrets set PYTHON_API_KEY="vsk_..."
flyctl secrets set SUPABASE_URL="https://..."
```

### ขั้นตอนที่ 4: Deploy

```bash
flyctl deploy
```

---

## 📊 เปรียบเทียบแพลตฟอร์ม

| Platform | Free Tier | RAM | Cold Start | Ease of Use | Recommendation |
|----------|-----------|-----|------------|-------------|----------------|
| **Render.com** | 750h/mo | 512MB | 30-50s | ⭐⭐⭐⭐⭐ | **Best for beginners** |
| **Railway.app** | $5/mo | 512MB | ❌ None | ⭐⭐⭐⭐ | **Best performance** |
| **Fly.io** | 3 VMs | 256MB | ❌ None | ⭐⭐⭐ | **Advanced users** |
| **PythonAnywhere** | Limited | 100MB | ❌ None | ⭐⭐⭐ | Too limited for ML |
| **Google Cloud Run** | 2M req/mo | 512MB | 1-5s | ⭐⭐⭐ | Need credit card |

---

## ⚙️ ไฟล์ที่ต้องมีก่อน Deploy

### 1. Dockerfile (✅ สร้างแล้ว)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. .dockerignore
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.git/
.gitignore
*.md
tests/
scripts/
```

### 3. render.yaml (สำหรับ Render)
```yaml
services:
  - type: web
    name: fitrecipes-vector-api
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: PYTHON_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: ENVIRONMENT
        value: production
```

---

## 🔧 การเชื่อมต่อจาก Backend

### Update .env (Backend Hono.js)

```bash
# Development
PYTHON_API_URL=http://localhost:8000

# Production (Render)
PYTHON_API_URL=https://fitrecipes-vector-api.onrender.com

# API Key (เหมือนกัน)
PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
```

### ทดสอบการเชื่อมต่อ

```typescript
// src/controllers/healthController.ts
import { checkVectorApiHealth } from '../utils/vectorApi';

export const checkServices = async (c: Context) => {
  const pythonApiHealth = await checkVectorApiHealth();
  
  return c.json({
    backend: 'healthy',
    pythonApi: pythonApiHealth.status,
    modelLoaded: pythonApiHealth.model_loaded,
  });
};
```

---

## 🚨 Troubleshooting

### Issue 1: Build ล้มเหลว (Out of Memory)

**Solution**: ลด workers หรือใช้ pre-built wheels
```dockerfile
# ใน Dockerfile เพิ่ม
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue 2: Cold Start นานมาก

**Solution 1 - Keep Alive Service**:
```bash
# ใช้ cron-job.org เรียก API ทุก 10 นาที
curl https://your-api.onrender.com/health
```

**Solution 2 - Upgrade to Paid**:
- Render: $7/เดือน (no cold start)
- Railway: Always-on instance

### Issue 3: Database Connection Failed

**Solution**: ตรวจสอบ SSL mode
```bash
# ใน .env ใส่ sslmode=require
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

---

## 📈 Monitoring & Logs

### Render.com
```bash
# ดู logs แบบ real-time
# ไปที่ Render Dashboard → Service → Logs
```

### Railway.app
```bash
railway logs
```

### Fly.io
```bash
flyctl logs
```

---

## 💰 Cost Estimation

### Scenario: 10,000 API calls/วัน

| Platform | Monthly Cost | Notes |
|----------|--------------|-------|
| **Render (Free)** | $0 | Cold start หลัง 15 นาที |
| **Render (Paid)** | $7 | No cold start, 512MB RAM |
| **Railway** | $5-10 | Based on usage |
| **Fly.io** | $0-5 | 3 VMs ฟรี |

---

## ✅ Recommended Setup

### For Development:
```bash
localhost:8000  # Run locally
```

### For Staging:
```bash
Render.com (Free Tier)  # Cold start OK for staging
```

### For Production:
```bash
Railway.app ($5-10/mo)  # No cold start, better performance
# หรือ
Render.com ($7/mo)  # Stable, predictable
```

---

## 🎯 Next Steps

1. ✅ เลือกแพลตฟอร์ม: **Render.com** (แนะนำ)
2. ✅ Push code ขึ้น GitHub
3. ✅ Deploy บน Render (follow steps ด้านบน)
4. ✅ ทดสอบด้วย curl
5. ✅ Update `PYTHON_API_URL` ใน backend .env
6. ✅ Test integration

**Time to deploy**: 15-20 นาที (first time)

Need help? พิมพ์ว่า "deploy render" หรือ "deploy railway" เพื่อดู step-by-step guide! 🚀
