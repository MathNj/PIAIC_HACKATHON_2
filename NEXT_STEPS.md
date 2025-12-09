# Next Steps to Fix Gemini API Key & Environment Variables Issue

**Current Status**: Backend deployment failing - environment variables not loading on Vercel
**Latest Deployment**: https://backend-pd41fal5h-mathnjs-projects.vercel.app

---

## The Problem

Environment variables set in Vercel dashboard are **NOT** being read by the Python code. The error is:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
```

This means `settings.DATABASE_URL` is empty/None, even though DATABASE_URL is set correctly in Vercel dashboard.

---

## What We've Done So Far

### ✅ Completed
1. Generated new Gemini API key (confirmed working in other apps)
2. Updated GEMINI_API_KEY in Vercel dashboard (Production environment)
3. Fixed environment variable loading in `backend/app/config.py`:
   - Removed `override=True` from `load_dotenv()`
   - Added debug logging to see what env vars are available
4. Deployed 6 times with different fixes
5. All changes pushed to GitHub branch `003-ai-chatbot`
6. Created comprehensive documentation:
   - `GEMINI_API_KEY_ISSUE.md` - Full troubleshooting history
   - `PHASE_STATUS.md` - Complete project status

---

## Root Cause Hypothesis

Pydantic Settings is not reading Vercel's environment variables correctly. Possible reasons:

1. **Environment variable names mismatch**: Vercel might be setting them with different casing
2. **Timing issue**: Variables not available when config.py loads
3. **Vercel-specific behavior**: Vercel might inject env vars differently than expected
4. **Missing Vercel configuration**: Need to explicitly configure how Vercel provides env vars

---

## Immediate Next Step: Check Debug Logs

The latest deployment (backend-pd41fal5h) has debug logging that will show:
- Whether code detects it's running on Vercel
- Which environment variables are in `os.environ`
- What DATABASE_URL and GEMINI_API_KEY values are

### Run this command:
```bash
vercel logs https://backend-pd41fal5h-mathnjs-projects.vercel.app 2>&1 | grep -E "DEBUG|ERROR" | head -50
```

This will show the debug output from `backend/app/config.py` lines 64-76.

---

## Expected Debug Output

You should see lines like:
```
[DEBUG] Running on Vercel
[DEBUG] DATABASE_URL in env: True/False
[DEBUG] GEMINI_API_KEY in env: True/False
[DEBUG] All env vars: ['PATH', 'VERCEL', 'DATABASE_URL', ...]
[DEBUG] Settings loaded - DATABASE_URL: postgresql://neondb_owner...
```

OR an error like:
```
[ERROR] Failed to load settings: ValidationError...
```

---

## Solutions Based on Debug Output

### If DATABASE_URL is NOT in os.environ:

**Option A**: Vercel might need explicit environment variable declaration in `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {"src": "vercel_app.py", "use": "@vercel/python"}
  ],
  "routes": [
    {"src": "/(.*)", "dest": "vercel_app.py"}
  ],
  "env": {
    "DATABASE_URL": "@database-url",
    "GEMINI_API_KEY": "@gemini-api-key",
    "BETTER_AUTH_SECRET": "@better-auth-secret",
    "FRONTEND_URL": "@frontend-url"
  }
}
```

Then create Vercel secrets:
```bash
vercel secret add database-url "postgresql://..."
vercel secret add gemini-api-key "AIza..."
```

**Option B**: Read environment variables directly in Python without Pydantic:

```python
# In config.py
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BETTER_AUTH_SECRET = os.environ.get("BETTER_AUTH_SECRET")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
```

### If DATABASE_URL IS in os.environ but Settings() fails:

**Fix**: Pydantic validation issue. Change to:
```python
class Settings(BaseSettings):
    DATABASE_URL: str = ""  # Allow empty, validate manually

    model_config = SettingsConfigDict(
        env_prefix="",  # No prefix
        case_sensitive=False,  # Try case-insensitive
        validate_assignment=False  # Don't validate on assignment
    )
```

---

## Alternative Approach: Test Locally First

Before more Vercel deployments, test the fix locally:

```bash
cd backend

# Update .env with new GEMINI_API_KEY
nano .env  # or use any editor

# Run backend locally
uvicorn app.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/signup -H "Content-Type: application/json" -d '{"email":"test@example.com","name":"Test","password":"Test123"}'
```

If local works with the new API key, then the issue is **definitely** Vercel-specific environment variable loading.

---

## Quick Win: Temporary Hardcode Test

To verify the Gemini API key works, temporarily hardcode it in config.py:

```python
# TEMPORARY TEST ONLY - DO NOT COMMIT
GEMINI_API_KEY: Optional[str] = "AIza..."  # Your new API key
```

Deploy and test. If chat works, then we know:
1. ✅ New API key is valid
2. ✅ Code logic is correct
3. ❌ Only environment variable loading is broken

Then revert and fix the env var loading properly.

---

## Files to Check/Modify

### 1. backend/app/config.py
Current debug version - check if debug logs appear in Vercel logs

### 2. backend/vercel.json
May need to add explicit env var declarations

### 3. backend/app/database.py
Line 23 is where it crashes - creating engine with empty DATABASE_URL

### 4. Vercel Dashboard
https://vercel.com/mathnjs-projects/backend/settings/environment-variables
- Verify all 4 variables are set for Production environment
- Check spelling/casing matches exactly

---

## Verification Checklist

After applying fix:

- [ ] Health endpoint returns `{"status":"ok",...}`
- [ ] Signup endpoint creates user
- [ ] Login endpoint returns JWT token
- [ ] Chat endpoint accepts message and returns AI response
- [ ] No more `FUNCTION_INVOCATION_FAILED` errors
- [ ] Vercel logs show successful config loading
- [ ] Remove debug logging from config.py
- [ ] Commit and push final fix to GitHub

---

## Contact/Support Resources

- **Vercel Docs**: https://vercel.com/docs/environment-variables
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **GitHub Branch**: https://github.com/MathNj/PIAIC_HACKATHON_2/tree/003-ai-chatbot

---

**Last Updated**: 2025-12-09
**Current Deployment**: https://backend-pd41fal5h-mathnjs-projects.vercel.app
**Status**: ⏳ Waiting for debug log analysis
