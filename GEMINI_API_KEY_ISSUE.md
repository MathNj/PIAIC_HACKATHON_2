# Gemini API Key Issue - Troubleshooting Summary

**Date**: 2025-12-09
**Branch**: `003-ai-chatbot`
**Issue**: Gemini API key expired/leaked, causing 403 errors in AI chat

---

## Problem Description

The original Gemini API key was flagged as leaked by Google and disabled. Even after updating the API key in Vercel dashboard, the backend deployment continued to fail with various errors.

---

## Root Cause Analysis

The issue was **environment variable loading** in `backend/app/config.py`. The original code used:

```python
load_dotenv(dotenv_path=env_path, override=True)
```

This `override=True` parameter was **overriding Vercel's system environment variables** with nothing (since no .env file exists in production), preventing the new GEMINI_API_KEY from being loaded.

---

## Fixes Applied

### Commit 1: `2a7c7ac` - Initial attempt
- Changed `override=True` to `override=False`
- Added check for .env file existence
- Made GEMINI_API_KEY Optional[str]

**Result**: Still failed - DATABASE_URL couldn't be parsed

### Commit 2: `20bf267` - Pydantic-only approach
- Removed manual `load_dotenv()` completely
- Relied on Pydantic Settings built-in loading

**Result**: Still failed - DATABASE_URL still not loading

### Commit 3: `6ba2825` - Final fix (current)
- Added back `load_dotenv(override=False)`
- This ensures:
  - Local dev: loads from .env file
  - Vercel prod: respects system environment variables

**Result**: Deployment succeeds, but health endpoint still returns FUNCTION_INVOCATION_FAILED

---

## Current Status

### ✅ Completed
- [x] Generated new Gemini API key (confirmed working in other apps)
- [x] Updated GEMINI_API_KEY in Vercel dashboard (Production environment)
- [x] Fixed environment variable loading logic in config.py
- [x] Deployed 4 times to Vercel with different fixes
- [x] Pushed all fixes to GitHub branch `003-ai-chatbot`

### ❌ Still Failing
- [ ] Health endpoint returns `FUNCTION_INVOCATION_FAILED`
- [ ] Chat endpoint untested (health fails first)
- [ ] Actual error details unclear from Vercel logs

---

## Vercel Environment Variables Status

| Variable | Environment | Status | Notes |
|----------|-------------|--------|-------|
| DATABASE_URL | Production, Preview, Development | ✅ Set | Neon PostgreSQL connection |
| BETTER_AUTH_SECRET | Production, Preview, Development | ✅ Set | JWT signing key |
| FRONTEND_URL | Production, Preview, Development | ✅ Set | CORS configuration |
| **GEMINI_API_KEY** | **Production only** | ✅ Set | **Updated 1h ago** |

**Critical Finding**: GEMINI_API_KEY is only set for **Production** environment, not Preview or Development.

---

## Deployment History

| Time | URL | Status | Notes |
|------|-----|--------|-------|
| 3m ago | `backend-qtjuhe6fd-mathnjs-projects.vercel.app` | ● Ready | Current (fix #3) |
| 8m ago | `backend-d6syu72gx-mathnjs-projects.vercel.app` | ● Ready | Fix #2 |
| 10m ago | `backend-4qukxpc7h-mathnjs-projects.vercel.app` | ● Ready | Fix #1 |
| 13m ago | `backend-dajstr4g8-mathnjs-projects.vercel.app` | ● Ready | Initial redeploy |

All deployments show "Ready" status but return FUNCTION_INVOCATION_FAILED on requests.

---

## Recommended Next Steps

### Option 1: Check Actual Error (Immediate)
```bash
# View real-time logs with error details
vercel logs https://backend-qtjuhe6fd-mathnjs-projects.vercel.app --output raw

# Or inspect specific deployment
vercel inspect https://backend-qtjuhe6fd-mathnjs-projects.vercel.app --logs
```

### Option 2: Verify Environment Variables (Quick Test)
Add a debug endpoint to print loaded environment variables:

```python
# In backend/app/main.py
@app.get("/debug/env")
async def debug_env():
    return {
        "database_url_set": bool(settings.DATABASE_URL),
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "database_url_prefix": settings.DATABASE_URL[:20] if settings.DATABASE_URL else None
    }
```

Deploy and call this endpoint to verify variables are loading.

### Option 3: Simplify Deployment (Alternative)
Try deploying with a simpler configuration:

1. Remove `vercel.json` `builds` section temporarily
2. Let Vercel auto-detect Python project
3. Redeploy

### Option 4: Check Local Backend (Sanity Check)
Verify the backend works locally with the new API key:

```bash
cd backend

# Update local .env with new GEMINI_API_KEY
# Then run:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Test endpoints:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/signup ...
```

If local works but Vercel doesn't, the issue is Vercel-specific.

---

## Code Changes Made

### backend/app/config.py

**Before**:
```python
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)  # ❌ BAD
```

**After**:
```python
# Load .env file for local development, but never override system environment variables
# This ensures Vercel's environment variables are used in production
load_dotenv(override=False)  # ✅ GOOD
```

**Also Changed**:
- Added `from typing import Optional` for type hints
- Changed `GEMINI_API_KEY: str = ""` to `GEMINI_API_KEY: Optional[str] = None`

---

## Testing Commands

### Test Health Endpoint
```bash
curl -X GET https://backend-qtjuhe6fd-mathnjs-projects.vercel.app/health
```

**Expected**: `{"status":"ok","app":"TODO API","version":"0.1.0"}`
**Actual**: `FUNCTION_INVOCATION_FAILED`

### Test Chat Endpoint (once health works)
```bash
# First signup/login to get JWT token, then:
curl -X POST "https://backend-qtjuhe6fd-mathnjs-projects.vercel.app/api/{user_id}/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -d '{"message":"Hello, can you help me?"}'
```

**Expected**: AI response with tool calls
**Actual**: Untested (blocked by health endpoint failure)

---

## Possible Remaining Issues

1. **Environment Variable Not Loading**: Despite fixes, Pydantic might not be reading Vercel's env vars correctly
2. **Import Time Error**: Database connection or config validation failing during import
3. **Vercel Function Timeout**: Cold start taking too long (unlikely, health should be fast)
4. **Missing Dependency**: Some package not installing correctly on Vercel
5. **Python Version Mismatch**: Vercel using Python 3.12, local might be 3.13

---

## Files Modified

```
backend/app/config.py        ✅ Fixed env var loading
GEMINI_API_KEY_ISSUE.md      ✅ This document
```

---

## Git Commits

```bash
2a7c7ac - fix: environment variable loading for Vercel deployment
20bf267 - fix: let Pydantic handle env var loading automatically
6ba2825 - fix: add load_dotenv with override=False for proper env loading
```

All commits pushed to GitHub: `003-ai-chatbot` branch

---

## Contact/Support

- **Vercel Dashboard**: https://vercel.com/mathnjs-projects/backend
- **Vercel Logs**: Run `vercel logs <deployment-url>`
- **GitHub Branch**: https://github.com/MathNj/PIAIC_HACKATHON_2/tree/003-ai-chatbot

---

**Generated**: 2025-12-09
**Last Deployment**: https://backend-qtjuhe6fd-mathnjs-projects.vercel.app
**Status**: ⚠️ Deployed but not functional - needs error log analysis
