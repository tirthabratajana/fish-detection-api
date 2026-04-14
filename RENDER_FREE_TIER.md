# Render Free Tier Deployment Guide

## What You Get (Free Tier)

✅ **FREE:**
- Unlimited free tier services
- Auto-deploy from GitHub
- SSL/HTTPS certificate
- Custom domain (subdomain: `.onrender.com`)
- Logs and basic monitoring
- Health checks
- 25 free instance hours per month

⚠️ **LIMITATIONS:**
- Service automatically spins down after 15 minutes of inactivity
- 0.5 CPU cores (shared)
- 512 MB RAM
- No persistent disks
- No background workers
- No auto-scaling
- First request after spin-down takes 30-50 seconds

## Step-by-Step FREE TIER Deployment

### Step 1: Prepare Your Repository

```powershell
cd f:\fish model backend

# Setup Git LFS for large model files
.\setup-render.bat

# Verify models are tracked
git lfs ls-files

# Should show:
# best.pt
# efficientnet_fish.h5
# model/Disease_model/fish.tflite
```

### Step 2: Commit and Push to GitHub

```powershell
# Add all files
git add .

# Commit
git commit -m "Fish detection API ready for Render deployment"

# Push to GitHub (requires GitHub repo created first)
git remote add origin https://github.com/YOUR_USERNAME/fish-detection-api.git
git branch -M main
git push -u origin main

# Verify Git LFS files pushed correctly
git lfs ls-files
```

### Step 3: Create Render Account

1. Go to https://render.com
2. Click **Sign up** (or **Sign in**)
3. Authorize with GitHub
   - Grant access to your fish-detection-api repo
   - This allows automatic deployment

### Step 4: Create Web Service

1. Go to **https://dashboard.render.com**
2. Click **New +** in top-right
3. Select **Web Service**
4. Choose **Build and deploy from a Git repository**
5. Find and select `fish-detection-api`
6. Click **Connect**

### Step 5: Configure Service

Fill in these settings:

| Field | Value |
|-------|-------|
| **Name** | `fish-detection-api` |
| **Environment** | `Docker` |
| **Region** | Choose nearest (US: Virginia/Oregon) |
| **Branch** | `main` |
| **Dockerfile Path** | `Dockerfile` |
| **Docker Build Context** | `.` (leave as is) |

### Step 6: Add Environment Variables

Click **Advanced** → **Add Environment Variable**

Add these one by one:
```
PYTHONUNBUFFERED = 1
PYTHONDONTWRITEBYTECODE = 1
LOG_LEVEL = info
WORKERS = 2
```

**Why WORKERS = 2?**
- Free tier has 512MB RAM
- Each worker needs memory
- 2 workers = good balance

### Step 7: Select Plan

⚠️ **CRITICAL**: Select **FREE** plan
- Default is often Standard ($7/month)
- Scroll to bottom
- Choose **FREE**

### Step 8: Create

Click **Create Web Service**

⏳ **Wait 10-15 minutes** for first deployment

### Step 9: Check Deployment

1. Go to Render Dashboard
2. Click on `fish-detection-api`
3. Watch the **Build** log
4. Once "Deploy Successful", get your URL:
   ```
   https://fish-detection-api-xxxxx.onrender.com
   ```

### Step 10: Test Your API

```powershell
$URL = "https://fish-detection-api-xxxxx.onrender.com"

# Health check
curl "$URL/health"

# Should return:
# {"status":"✅ Healthy","yolo_model_loaded":true,"efficientnet_model_loaded":true,"message":"All models loaded and ready"}

# View API documentation
Start-Process "$URL/docs"

# Test prediction (may take 30+ seconds on first request due to cold start)
curl -X POST "$URL/predict" `
  -H "accept: application/json" `
  -F "file=@path/to/your/test_image.jpg"
```

## Understanding Cold Starts

Every 15 minutes with zero traffic, your service spins down to save resources.

### What Happens:
1. **No requests for 15 minutes** → Service pauses
2. **First request arrives** → Service wakes up (cold start)
3. **Takes 30-50 seconds** → Loading models, starting server
4. **Response sent** → Service now responsive (~1-2 sec per request)
5. **Idle again for 15 min** → Cycle repeats

### Behavior During Cold Start:
```powershell
# This might timeout or return 503 Service Unavailable
curl "$URL/predict" -F "file=@image.jpg"

# Wait 30-40 seconds, then try again
# This should work now (2-5 second response)
curl "$URL/predict" -F "file=@image.jpg"
```

## Updating Your API

Every time you push to main branch, Render auto-deploys:

```powershell
# Make changes to your code
# Edit app/main.py, image_processor.py, etc.

# Commit and push
git add .
git commit -m "Fix prediction bug"
git push origin main

# Render automatically:
# 1. Pulls code from GitHub
# 2. Rebuilds Docker image (5-10 min)
# 3. Deploys new version
# 4. Your API updates automatically
```

**Check status:** Render Dashboard → Events log

## Optimizing for Free Tier

### 1. Reduce Memory Usage

In `fastapi_app/app/main.py`:
```python
environment:
  WORKERS: 2  # Not 4
  MODEL_BATCH_SIZE: 1
```

### 2. Compress Models (Optional)

Convert to FP16 precision to reduce size:
```python
# In model_loader.py
import quantization_lite
quantize_model(model_path, output_path)
```

### 3. Add Response Timeout

In `app/main.py`:
```python
@app.post("/predict")
async def predict_fish(file: UploadFile = File(...)):
    # Add timeout for free tier
    try:
        result = await asyncio.wait_for(
            process_prediction(file),
            timeout=120  # 2 minutes max
        )
    except asyncio.TimeoutError:
        return {"error": "Processing took too long"}
```

### 4. Limit File Sizes

In `image_processor.py`:
```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB max
if len(image_bytes) > MAX_FILE_SIZE:
    raise ValueError("Image too large")
```

## Monitoring Free Tier Service

### View Real-Time Logs
```
Render Dashboard → Your Service → Logs tab
Scroll to see what's happening
```

### Common Log Patterns

✅ **Healthy:**
```
INFO: Application startup complete
INFO: Started server process
Running inference...
```

❌ **Memory Issues:**
```
MemoryError: Unable to allocate
signal: killed
```

❌ **Startup Failures:**
```
ModuleNotFoundError: No module named 'tensorflow'
ImportError: cannot import name 'xyz'
```

### Check Service Status
```
https://status.render.com
Monitor for outages/maintenance
```

## Upgrade When Ready

If you need better performance:

### Starter Plan ($2.50/month)
- Same resources
- **NO SPINDOWN** ← Main benefit
- Best value for hobby projects

### Standard Plan ($7/month)
- 0.5 CPU, 512MB RAM
- Health checks
- Auto-deploy

### Pro Plan ($28/month)
- 4 CPU, 7GB RAM
- Persistent disks (models stored permanently)
- Priority support

## Free Tier FAQ

**Q: How do I keep the service awake?**
A: You can't prevent spindown on free tier. Upgrade to Starter for always-on.

**Q: Why is my first request slow?**
A: Cold start - models are loaded into RAM (takes 30-50 sec)

**Q: Can I use a database?**
A: Yes! Create PostgreSQL database (also has free tier)

**Q: How do I add a custom domain?**
A: Free tier supports *.onrender.com subdomains. Paid plans support custom domains.

**Q: Will my code be deleted?**
A: No. GitHub always has backup. Render links to your repo.

**Q: Can I use GPU?**
A: No. GPUs only on paid plans ($70+/month)

## Troubleshooting Free Tier Issues

### Build Fails
```
Check: Render Dashboard → Logs
Common issue: requirements.txt missing dependency

Solution:
1. Update requirements.txt locally
2. Test: pip install -r requirements.txt
3. Commit and push
4. Render auto-rebuilds
```

### Models Not Included
```
Check: git lfs ls-files
Should show your models

If empty:
1. Run: setup-render.bat again
2. Run: git push --force origin main (force re-push Git LFS)
```

### Out of Memory (OOM)
```
Error: Killed (exit code 137)

Solution:
1. Reduce WORKERS to 1
2. Remove batch processing
3. Optimize model loading
4. Upgrade to Starter plan ($2.50/mo)
```

### Timeout on Large Images
```
Error: 504 Gateway Timeout

Solution:
1. Resize images before upload
2. Reduce MAX_FILE_SIZE
3. Use Pro plan with more RAM
```

### Cold Start Taking Too Long
```
First request takes >60 seconds

Causes:
- Models exceed memory during load
- Network bottleneck pulling from GitHub
- Docker layer caching issues

Solutions:
1. Clear build cache: Dashboard → Settings → Clear Cache
2. Commit smaller code changes
3. Upgrade to Starter plan (no spindown)
```

## Success Tips

1. ✅ **Start small** - Test locally first
2. ✅ **Monitor logs** - Check Render dashboard frequently  
3. ✅ **Push frequently** - Find issues early
4. ✅ **Test cold starts** - Wait 15 min, reload page
5. ✅ **Use Starter plan** when you're ready (only $2.50/mo!)

## Getting Help

- **Render Docs**: https://render.com/docs
- **Free Tier Info**: https://render.com/pricing
- **Status**: https://status.render.com
- **Support**: https://support.render.com
- **Community**: Render Discord

## Next Steps

1. ✅ Setup Git LFS (`setup-render.bat`)
2. ✅ Push to GitHub
3. ✅ Create Render web service
4. ✅ Select **FREE** plan
5. ✅ Wait for deployment
6. ✅ Test your API
7. ✅ Monitor logs for issues
8. ✅ Celebrate! 🎉

Your Fish Detection API is now live on the internet, absolutely **FREE**! 🚀

---

**Questions?** Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for more details.
