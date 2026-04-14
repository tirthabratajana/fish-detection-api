# Quick Render Deployment Checklist - FREE TIER

⚠️ **FREE TIER LIMITATIONS**:
- Service **spins down** after 15 minutes of inactivity
- **No persistent disks** available
- Limited resources: 0.5 CPU, 512MB RAM
- First request after spindown takes ~30 seconds
- Not suitable for production heavy-use

## Pre-Deployment ✅

- [ ] All code committed to GitHub
- [ ] `requirements.txt` updated with all dependencies
- [ ] `Dockerfile` tested locally
- [ ] All model files ready:
  - [ ] `best.pt` - YOLO model (~100 MB)
  - [ ] `efficientnet_fish.h5` - Classification model (~100 MB)
  - [ ] `model/Disease_model/fish.tflite` - Disease model (~50 MB)
  - [ ] `clf_class_names.json` - Class names
- [ ] Git LFS installed on your machine
- [ ] **Choose model storage solution** (see below)

## Setup Steps

### 1️⃣ Prepare Git Repository
```bash
# Windows
setup-render.bat

# macOS/Linux
bash setup-render.sh
```

OR manually:
```bash
git lfs install
git lfs track "*.pt" "*.h5" "*.tflite"
git add .gitattributes
git commit -m "Setup Git LFS"
git add .
git commit -m "Initial commit"
```

### 2️⃣ Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/fish-detection-api.git
git branch -M main
git push -u origin main
```

### 4️⃣ Configure Service

- **Name**: `fish-detection-api`
- **Branch**: `main`
- **Runtime**: `Docker`
- **Region**: Choose closest to your users
- **Plan**: **FREE**

### 5️⃣ Add Environment Variables

```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
LOG_LEVEL=info
WORKERS=2
```

### 6️⃣ Choose Model Storage Solution (⚠️ IMPORTANT)

**Option A: Include Models in Git (Recommended for Free Tier)**
- ✅ Simple setup
- ✅ No external dependencies
- ⚠️ Larger repo (250-300 MB)
- ⚠️ Git cloning takes longer

```bash
# Already done with setup-render.bat
# Models track with Git LFS, uploaded with git push
```

**Option B: Download from External Storage (Advanced)**
- ✅ Smaller repo
- ✅ Faster deployment
- ⚠️ Download delay on first startup
- Requires AWS S3 / Google Cloud Storage / etc.

Set environment variable:
```
MODEL_DOWNLOAD_URL=https://your-bucket.s3.amazonaws.com/models/
```

**For this guide, we'll use Option A (models in Git)**

### 7️⃣ Create Service

Click **Create Web Service**

Wait 10-15 minutes for deployment...

### 8️⃣ Verify Deployment

Once deployed:

```powershell
# Get your service URL from Render dashboard
$RENDER_URL = "https://fish-detection-api-xxxxx.onrender.com"

# Health check
curl "$RENDER_URL/health"

# View API docs
Start-Process "$RENDER_URL/docs"

# Test prediction
curl -X POST "$RENDER_URL/predict" `
  -H "accept: application/json" `
  -F "file=@test_image.jpg"
```

## During Development - Auto-Deploy

Push to main branch → Automatic redeploy:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

⚠️ **Note**: First deployment after code push takes 10-15 minutes

## ⚠️ FREE TIER SPECIFICS

### Service Spin-Down
- Service **automatically stops** after 15 minutes of no traffic
- **Not killed** - just paused
- **First request after spin-down** takes 30-50 seconds (cold start)
- All subsequent requests are fast (sub-second)

### Memory & CPU Limits
- **CPU**: 0.5 cores (shared)
- **RAM**: 512 MB
- May timeout on very large images
- Consider resizing images to 1024x768 or smaller

### Recommended Limits
In `image_processor.py`, add max file size check:
```python
MAX_FILE_SIZE_MB = 10  # Reduce from default
```

### Free Tier Not Suitable For
- ❌ High-traffic production apps
- ❌ Real-time processing requirements
- ❌ Continuous availability needs
- ✅ Development & testing
- ✅ Demos
- ✅ Low-traffic hobby projects

## Troubleshooting

### Service Not Responding
1. Check if it's in **spin-down** (wait 30 seconds for cold start)
2. Check logs in Render Dashboard

### Out of Memory
1. Reduce WORKERS to 1-2
2. Use lighter models
3. Upgrade to paid tier if needed

### Model Files Missing
1. Verify Git LFS tracked files: `git lfs ls-files`
2. Check repo size: `git count-objects -vH`
3. Re-push with: `git push -u origin main`

### Build Fails
```
Render Dashboard → Logs → Check build errors
Common: Missing dependencies in requirements.txt
```

### Port Issues
✅ Already fixed! Using dynamic PORT env var

## Monitoring

- **Logs**: Render Dashboard → Logs (free tier included)
- **Metrics**: Limited in free tier
- **Status**: https://status.render.com

## Important URLs

- **API Endpoint**: `https://fish-detection-api-xxxxx.onrender.com`
- **API Docs**: `https://fish-detection-api-xxxxx.onrender.com/docs`
- **Health Check**: `https://fish-detection-api-xxxxx.onrender.com/health`
- **Render Dashboard**: https://dashboard.render.com

## Files Reference

| File | Purpose |
|------|---------|
| `render.yaml` | Render config (FREE tier) |
| `Dockerfile.render` | Render-optimized Docker |
| `.gitattributes` | Git LFS config |
| `setup-render.bat` | Windows setup |
| `setup-render.sh` | macOS/Linux setup |
| `RENDER_DEPLOYMENT.md` | Detailed guide |

## Post-Deployment

1. ✅ Monitor logs for errors
2. ✅ Test all endpoints
3. ✅ Check cold-start behavior
4. ✅ Validate model predictions
5. 🔄 Keep code in GitHub updated

## Upgrade Path (When Needed)

| Plan | Cost | Features |
|------|------|----------|
| **Free** | $0 | Spindown, 512MB RAM |
| **Starter** | $2.50/mo | 0.5 vCPU, 512MB, no spindown |
| **Standard** | $7/mo | 0.5 vCPU, 512MB + persistent disk |
| **Pro** | $28/mo | 4 vCPU, 7GB, full features |

## Cost Estimate (Free Tier)

- Web Service: **FREE** ✅
- Storage: **FREE** ✅
- Bandwidth: **FREE** ✅  
- Domain: **FREE** (subdomain)
- **Total**: **$0/month** 🎉

*Paid plans available if you need guaranteed uptime and more resources*

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Free Tier Info**: https://render.com/pricing
- **Status Page**: https://status.render.com
- **Support Portal**: https://support.render.com
- **Community**: Discord/Forums

---

✅ **Ready to deploy!** Follow the checklist above and you'll be live in 15 minutes **for free**.

### Quick Deploy Summary:
1. ✅ Run `setup-render.bat`
2. ✅ Push to GitHub with `git push origin main`
3. ✅ Connect repo in Render dashboard
4. ✅ Choose **FREE** plan
5. ✅ Deploy!
6. ✅ Test at generated URL

No credit card required for free tier! 🚀
