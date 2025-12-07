# Deployment Guide: TODO App

This guide will help you deploy your full-stack TODO application to production.

## Architecture

- **Frontend**: Next.js → Vercel
- **Backend**: FastAPI → Railway (or Render)
- **Database**: Neon PostgreSQL (already cloud-hosted)

---

## Option 1: Deploy Backend to Railway (Recommended - Free Tier)

### Step 1: Deploy Backend to Railway

1. **Install Railway CLI** (optional, can use web UI):
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create New Project on Railway**:
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo" or "Empty Project"

3. **If using Empty Project**:
   ```bash
   cd backend
   railway init
   railway up
   ```

4. **Set Environment Variables** in Railway Dashboard:
   ```
   DATABASE_URL=your_neon_postgres_url
   BETTER_AUTH_SECRET=your-secret-key-must-be-at-least-32-characters-long
   FRONTEND_URL=https://your-app.vercel.app
   DEBUG=false
   ```

5. **Railway will automatically detect** `requirements.txt` and deploy!

6. **Get your backend URL**: Railway will provide a URL like `https://your-app.railway.app`

---

### Step 2: Deploy Frontend to Vercel

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel
   ```

3. **Follow prompts**:
   - Set up and deploy? **Yes**
   - Which scope? Select your account
   - Link to existing project? **No**
   - Project name? **todo-app-hackathon** (or your choice)
   - Directory? **./frontend** (or leave as current)
   - Override settings? **No**

4. **Set Environment Variables** in Vercel Dashboard:
   - Go to your project settings on https://vercel.com
   - Navigate to "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend.railway.app
     BETTER_AUTH_SECRET=your-secret-key-must-be-at-least-32-characters-long
     ```

5. **Redeploy** after setting env vars:
   ```bash
   vercel --prod
   ```

---

## Option 2: Deploy Backend to Render (Alternative - Free Tier)

### Step 1: Deploy Backend to Render

1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: todo-api
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables**:
   ```
   DATABASE_URL=your_neon_postgres_url
   BETTER_AUTH_SECRET=your-secret-key
   FRONTEND_URL=https://your-app.vercel.app
   DEBUG=false
   ```

6. Click "Create Web Service"

7. Get your backend URL: `https://your-app.onrender.com`

### Step 2: Deploy Frontend (Same as Option 1)

Follow the Vercel deployment steps above, using your Render backend URL.

---

## Option 3: Full Vercel Deployment (Experimental)

⚠️ **Warning**: Vercel's Python support is limited. This may not work for all FastAPI features.

1. **Deploy from root directory**:
   ```bash
   vercel
   ```

2. Vercel will use the `vercel.json` at root to deploy both frontend and backend

3. **Set Environment Variables** in Vercel project settings:
   ```
   DATABASE_URL=your_neon_postgres_url
   BETTER_AUTH_SECRET=your-secret-key
   NEXT_PUBLIC_API_URL=/api
   ```

---

## Database Setup (Neon PostgreSQL)

Your Neon database is already configured for local testing. For production:

1. Go to https://console.neon.tech
2. Get your production connection string
3. Update `DATABASE_URL` in your deployment platform
4. Run migrations (if using Alembic):
   ```bash
   # SSH into your backend server or run locally
   alembic upgrade head
   ```

**Note**: Currently using SQLite for local testing. For production, uncomment PostgreSQL in `requirements.txt`:
```txt
psycopg2-binary==2.9.9  # Uncomment this line
```

---

## Post-Deployment Checklist

- [ ] Backend is accessible at deployment URL
- [ ] Frontend is accessible at Vercel URL
- [ ] Test `/health` endpoint: `curl https://your-backend.railway.app/health`
- [ ] Test user signup via frontend
- [ ] Test user login via frontend
- [ ] Verify CORS is working (frontend can call backend)
- [ ] Check that tasks are being created/retrieved
- [ ] Verify database persistence (refresh page, data remains)

---

## Quick Start Commands

### Deploy Backend (Railway):
```bash
cd backend
railway login
railway init
railway up
```

### Deploy Frontend (Vercel):
```bash
cd frontend
vercel
vercel --prod  # For production deployment
```

### View Logs:
```bash
# Railway
railway logs

# Vercel
vercel logs
```

---

## Environment Variables Summary

### Backend Environment Variables:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Shared secret (min 32 chars)
- `FRONTEND_URL`: Your Vercel frontend URL (for CORS)
- `DEBUG`: Set to `false` in production

### Frontend Environment Variables:
- `NEXT_PUBLIC_API_URL`: Your backend URL (Railway/Render)
- `BETTER_AUTH_SECRET`: Same as backend (for JWT verification)

---

## Troubleshooting

### Backend not responding:
- Check environment variables are set correctly
- Check logs: `railway logs` or in Render dashboard
- Verify `requirements.txt` installed successfully
- Check that PORT is being read from environment

### Frontend can't reach backend:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in backend `main.py`
- Verify backend `FRONTEND_URL` includes your Vercel domain

### Database connection errors:
- Verify Neon connection string is correct
- Check if Neon database is active (free tier may sleep)
- Ensure IP whitelist includes deployment platform IPs

---

## Cost Estimate

All recommended services have free tiers:

- **Railway**: 500 hours/month free, $5/month after
- **Vercel**: Unlimited hobby projects, 100GB bandwidth
- **Neon**: 3GB storage free, always-on compute
- **Total**: $0/month for hobby use

---

## Production Optimization

For production use, consider:

1. **Enable PostgreSQL**: Switch from SQLite to Neon PostgreSQL
2. **Add Alembic migrations**: For database version control
3. **Enable production mode**: Set `DEBUG=false`
4. **Add monitoring**: Use Railway/Vercel analytics
5. **Add rate limiting**: Protect API from abuse
6. **Enable HTTPS**: Automatic on Railway/Vercel
7. **Add error tracking**: Sentry integration

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Neon Docs: https://neon.tech/docs
