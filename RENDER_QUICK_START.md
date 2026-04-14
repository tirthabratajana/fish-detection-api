# Quick Render Deployment Checklist

## Pre-Deployment ✅

- [ ] All code committed to GitHub
- [ ] `requirements.txt` updated with all dependencies
- [ ] `Dockerfile` tested locally
- [ ] All model files ready:
  - [ ] `best.pt` - YOLO model
  - [ ] `efficientnet_fish.h5` - Classification model
  - [ ] `model/Disease_model/fish.tflite` - Disease model
  - [ ] `clf_class_names.json` - Class names
- [ ] Git LFS installed on your machine

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

### 3️⃣ Create Render Web Service

1. Go to **https://dashboard.render.com**
2. Click **New** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Authorize GitHub
5. Select your `fish-detection-api` repository

### 4️⃣ Configure Service

- **Name**: `fish-detection-api`
- **Branch**: `main`
- **Runtime**: `Docker`
- **Region**: Choose closest to your users

### 5️⃣ Add Environment Variables

```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
LOG_LEVEL=info
WORKERS=4
```

### 6️⃣ Create Persistent Disk

In Render Dashboard → **Disks**:
- **Name**: `model-storage`
- **Size**: 20 GB
- **Mount Path**: `/app/model`

### 7️⃣ Create Service

Click **Create Web Service**

Wait 5-15 minutes for deployment...

### 8️⃣ Verify Deployment

Once deployed:

```bash
# Get your service URL from Render dashboard
RENDER_URL=https://fish-detection-api-xxxxx.onrender.com

# Health check
curl $RENDER_URL/health

# View API docs
open $RENDER_URL/docs

# Test prediction
curl -X POST "$RENDER_URL/predict" \
  -H "accept: application/json" \
  -F "file=@test_image.jpg"
```

## During Development - Auto-Deploy

Push to main branch → Automatic redeploy:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

## Troubleshooting

### Check Logs
```
Render Dashboard → Logs tab → View real-time logs
```

### Clear Cache & Rebuild
```
Render Dashboard → Settings → Clear Build Cache
Then trigger manual deploy
```

### Model Files Missing
Check persistent disk is attached:
```
Render Dashboard → Disks → Verify model-storage attached
```

### Out of Memory
Upgrade plan:
```
Render Dashboard → Settings → Change Plan from Standard to Pro
```

### Port Issues
✅ Already fixed! Using dynamic PORT env var

## Monitoring

- **Logs**: Render Dashboard → Logs
- **Metrics**: Render Dashboard → Metrics
- **Status**: https://status.render.com

## Important URLs

- **API Endpoint**: `https://fish-detection-api-xxxxx.onrender.com`
- **API Docs**: `https://fish-detection-api-xxxxx.onrender.com/docs`
- **Health Check**: `https://fish-detection-api-xxxxx.onrender.com/health`
- **Render Dashboard**: https://dashboard.render.com

## Files Reference

| File | Purpose |
|------|---------|
| `render.yaml` | Render infrastructure config |
| `Dockerfile.render` | Render-optimized Docker image |
| `.gitattributes` | Git LFS configuration |
| `setup-render.bat` | Windows setup script |
| `setup-render.sh` | macOS/Linux setup script |
| `RENDER_DEPLOYMENT.md` | Detailed deployment guide |

## Post-Deployment

1. Monitor logs for errors
2. Test all endpoints
3. Set up monitoring alerts (optional)
4. Customize domain (optional)
5. Configure auto-scaling (Pro plan only)

## Cost Estimate

| Component | Cost |
|-----------|------|
| Web Service (Standard) | $7/month |
| Model Storage (20GB) | $4/month |
| **Total** | **~$11/month** |

Upgrade to Pro ($28/month) for better performance.

## Support

- **Render Docs**: https://render.com/docs
- **Support Portal**: https://support.render.com
- **Status Page**: https://status.render.com

---

✅ **Ready to deploy!** Follow the checklist above and you'll be live in 15 minutes.
