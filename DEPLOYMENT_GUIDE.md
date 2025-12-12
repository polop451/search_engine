# Python Vector API - Deployment Guide 🚀

## ✅ Before You Begin
- Create accounts for your deployment platform (Render, Railway, Fly) and for Supabase/Postgres.
- Provision a Postgres instance with pgvector (see section below) and confirm the connection string works from your laptop.
- Install Docker Desktop, Git, and the relevant platform CLI (`render`, `railway`, or `flyctl`) if you plan to deploy via CLI.
- Run the API locally (`uvicorn app.main:app --reload`) and verify `http://localhost:8000/health` returns `{"status":"ok"}` before attempting any remote deploy.
- Store secrets in a password manager so you can rotate them quickly if leaked.

## 🔐 Environment Variables Reference
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | Postgres connection string with `sslmode=require`; must point to the pgvector-enabled database. |
| `PYTHON_API_KEY` | ✅ | Shared secret for authenticating the backend to the Python API. Rotate if exposed. |
| `SUPABASE_URL` | ✅ | Supabase REST URL used by the API when fetching metadata. |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anon/service key; prefer a service role key for production deployments. |
| `ENVIRONMENT` | ✅ | `production`, `staging`, or `development`; drives logging verbosity and feature flags. |
| `LOG_LEVEL` | ⚙️ | Defaults to `INFO`; set to `DEBUG` temporarily when troubleshooting (but watch log noise). |
| `EXTRA_ALLOWED_ORIGINS` | ⚙️ | Comma-separated origins for CORS overrides if the frontend lives on multiple domains. |

Keep the `.env` file out of version control (`.gitignore` already handles this). When using managed platforms, prefer their built-in secrets managers instead of storing credentials in code.

## 🌟 Recommended Platforms (FREE Tier)

### 1. **Render.com** (Top pick ⭐⭐⭐⭐⭐)
- **Free Tier**: 750 hours/month (plenty)
- **RAM**: 512MB (enough for this ML workload)
- **Pros**: Auto-deploy from GitHub, free SSL, very easy to use
- **Cons**: Cold start ~30-50 seconds after 15 minutes idle
- **Best for**: Production-ready services with free custom domains

### 2. **Railway.app** (Great choice ⭐⭐⭐⭐)
- **Free Tier**: $5 credit/month (~500 hours)
- **RAM**: 512MB-1GB
- **Pros**: No cold start, easy deploys, great logs
- **Cons**: Need to top up once the monthly credit ends
- **Best for**: Development + light production

### 3. **Fly.io** (Powerful but more complex ⭐⭐⭐⭐)
- **Free Tier**: 3 shared CPU VMs
- **RAM**: 256MB (tight but workable)
- **Pros**: Global edge network, zero cold start
- **Cons**: Requires CLI setup and has a steeper learning curve
- **Best for**: Advanced users

### 4. **Heroku** (No longer recommended ⭐⭐)
- **Free Tier**: Discontinued (starts at $7/month)
- **Pros**: Extremely easy to use
- **Cons**: Not free anymore

---

## 🎯 Quick Start: Deploy on Render.com

### Step 1: Prep the project

```bash
cd python-vector-api

# Double-check required files are present
ls -la
# Required: Dockerfile, requirements.txt, app/, .env.example
```

### Step 2: Push code to GitHub

```bash
# If the repo is not initialized yet
git init
git add .
git commit -m "feat: add Python Vector API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/python-vector-api.git
git push -u origin main
```

### Step 3: Deploy on Render

1. **Create a Render account**:
   - Visit https://render.com
   - Sign up with GitHub

2. **Create a Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select repo: `python-vector-api`

3. **Configure the service**:
   ```yaml
   Name: fitrecipes-vector-api
   Environment: Docker
   Region: Singapore (closest)
   Branch: main
   Dockerfile Path: ./Dockerfile
   Instance Type: Free
   ```

4. **Add environment variables**:
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGc...
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

5. **Deploy**:
   - Click "Create Web Service"
  - Wait 5-10 minutes while the Docker image builds
  - Watch the **Logs** tab; build failures often mean missing env vars or insufficient memory

6. **Test**:
   ```bash
   # Expect a URL similar to: https://fitrecipes-vector-api.onrender.com
   curl https://fitrecipes-vector-api.onrender.com/health
   ```

7. **Observe & harden**:
  - Turn on **Auto-Deploy** only after the first successful deploy so that unreviewed commits do not break production unexpectedly.
  - Enable Render **Health Checks** (`/health`) so unhealthy instances are restarted automatically.
  - If you hit cold starts frequently, configure an uptime monitor (BetterStack, Cronitor, or cron-job.org) to ping the API every 10 minutes.

**Rollback plan**: Duplicate the service, pin it to the last known-good commit, and flip traffic by updating DNS/custom domains. Render keeps the previous image for a short window, so you can also hit "Redeploy last build" when needed.

---

## 🚀 Alternative: Deploy on Railway.app

### Step 1: Install the Railway CLI

```bash
# macOS
brew install railway

# Or via npm
npm install -g @railway/cli
```

### Step 2: Log in

```bash
railway login
```

### Step 3: Deploy

```bash
cd python-vector-api

# Create a new project
railway init

# Add environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set PYTHON_API_KEY="vsk_..."

# Deploy!
railway up
```

### Step 4: Create a public URL

```bash
# Create a public domain
railway domain
```

**Reliability tips**
- Run `railway status` after each deploy; it surfaces unhealthy builds quickly.
- Use `railway logs -f` during the first traffic spike to ensure workers do not crash under load.
- Railway snapshots your Postgres add-on. Schedule exports to Supabase Storage/S3 if you need longer retention.

**Rollback plan**
1. `railway releases` to list past deployments.
2. `railway rollback <release-id>` to revert to a previous image.
3. Re-run smoke tests (`/health`, `/v1/search?q=chicken`) before reopening traffic.

---

## 🎯 Alternative: Deploy on Fly.io

### Step 1: Install the Fly CLI

```bash
# macOS
brew install flyctl

# Or use the script
curl -L https://fly.io/install.sh | sh
```

### Step 2: Log in and launch

```bash
cd python-vector-api

# Log in
flyctl auth login

# Launch the app
flyctl launch
# Choose:
# - App name: fitrecipes-vector-api
# - Region: Singapore
# - RAM: 512MB
```

### Step 3: Configure secrets

```bash
# Add environment variables
flyctl secrets set DATABASE_URL="postgresql://..."
flyctl secrets set PYTHON_API_KEY="vsk_..."
flyctl secrets set SUPABASE_URL="https://..."
```

### Step 4: Deploy

```bash
flyctl deploy
```

**Reliability tips**
- Add a Fly **Machine Check** pointing to `/health` so unhealthy VMs recycle.
- Pin the app to a region close to your database to minimize latency.
- Use `flyctl scale memory 512` (or higher) if embeddings exceed available RAM—otherwise deployments may crash mid-request.

**Rollback plan**
- `flyctl releases list` to view previous versions; `flyctl releases info <version>` to inspect.
- `flyctl releases revert <version>` to redeploy the previous image.
- Keep `fly.toml` committed so a teammate can redeploy the same config quickly.

---

## 📊 Platform Comparison

| Platform | Free Tier | RAM | Cold Start | Ease of Use | Recommendation |
|----------|-----------|-----|------------|-------------|----------------|
| **Render.com** | 750h/mo | 512MB | 30-50s | ⭐⭐⭐⭐⭐ | **Best for beginners** |
| **Railway.app** | $5/mo | 512MB | ❌ None | ⭐⭐⭐⭐ | **Best performance** |
| **Fly.io** | 3 VMs | 256MB | ❌ None | ⭐⭐⭐ | **Advanced users** |
| **PythonAnywhere** | Limited | 100MB | ❌ None | ⭐⭐⭐ | Too limited for ML |
| **Google Cloud Run** | 2M req/mo | 512MB | 1-5s | ⭐⭐⭐ | Requires credit card |

---

## 🔍 Post-Deployment Verification
Perform these checks immediately after any deploy, no matter the platform:

1. **Health endpoint**: `curl -i https://<host>/health` should return `200` plus `{ "status": "ok" }`.
2. **Embedding workflow**: Run `python scripts/generate_embeddings.py --limit 1` against the remote API or call `/v1/search?q=chicken` to confirm pgvector writes succeed.
3. **Logs**: Ensure there are no `psycopg2` or `vector` errors. Spikes usually signal a missing extension or invalid connection string.
4. **Metrics**: On Render/Railway, confirm CPU and RAM stay below 70% during load; scale up if they breach that threshold for more than 5 minutes.
5. **Alerting**: Configure a simple uptime check that notifies Slack/Email on repeated failures (BetterStack, UptimeRobot, or PagerDuty).

## 🧠 Enable pgvector on Supabase

Before deploying the API, make sure your Supabase Postgres instance has the `pgvector` extension enabled. This extension adds the `vector` column type that stores 768-dimension embeddings produced by the Sentence Transformers model—without it every vector insert/update will fail.

1. **Open** `Supabase Dashboard → SQL Editor → New query`
2. **Run** the following SQL script once:

```sql
-- Supabase Dashboard → SQL Editor → New query

-- Enable pgvector extension (already available in Supabase)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

If the verification query returns a row, you're good to go. Re-run these commands only when setting up a brand-new Supabase project.

---

## ⚙️ Files to Prepare Before Deploying

### 1. Dockerfile (already created)
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

### 3. render.yaml (for Render)
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

## 🔧 Connecting From the Backend

### Update .env (Backend Hono.js)

```bash
# Development
PYTHON_API_URL=http://localhost:8000

# Production (Render)
PYTHON_API_URL=https://fitrecipes-vector-api.onrender.com

# Same API key for both
PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9
```

### Test the connection

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

### Issue 1: Build failed (Out of Memory)

**Solution**: Reduce workers or install pre-built wheels
```dockerfile
# In the Dockerfile add
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue 2: Cold starts are too long

**Solution 1 - Keep-alive service**:
```bash
# Use cron-job.org (or similar) to ping the API every 10 minutes
curl https://your-api.onrender.com/health
```

**Solution 2 - Upgrade to a paid plan**:
- Render: $7/month (no cold start)
- Railway: Always-on instance

### Issue 3: Database connection failed

**Solution**: Ensure SSL mode is set
```bash
# Add sslmode=require to `.env`
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

---

## 📈 Monitoring & Logs

### Render.com
```bash
# Real-time logs live inside Render Dashboard → Service → Logs
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

### Scenario: 10,000 API calls/day

| Platform | Monthly Cost | Notes |
|----------|--------------|-------|
| **Render (Free)** | $0 | Cold starts after 15 minutes |
| **Render (Paid)** | $7 | No cold start, 512MB RAM |
| **Railway** | $5-10 | Usage-based |
| **Fly.io** | $0-5 | 3 free VMs |

---

## ✅ Recommended Setup

### For Development:
```bash
localhost:8000  # Run locally
```

### For Staging:
```bash
Render.com (Free Tier)  # Cold start acceptable for staging
```

### For Production:
```bash
Railway.app ($5-10/mo)  # No cold start, better performance
# or
Render.com ($7/mo)      # Stable, predictable
```

---

## 🎯 Next Steps

1. ✅ Choose a platform: **Render.com** (recommended)
2. ✅ Push the code to GitHub
3. ✅ Deploy on Render (follow the steps above)
4. ✅ Test with curl
5. ✅ Update `PYTHON_API_URL` in the backend `.env`
6. ✅ Test the integration end-to-end

**Time to deploy**: 15-20 minutes (first run)

Need more help? Type "deploy render" or "deploy railway" for a detailed walkthrough! 🚀
