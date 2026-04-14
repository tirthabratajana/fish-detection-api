# Render Deployment Guide

## Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Render Account** - Sign up at https://render.com
3. **Models Prepared** - All model files ready locally

## Deployment Steps

### Step 1: Push Code to GitHub

```bash
cd f:\fish model backend
git init
git add .
git commit -m "Initial commit - Fish detection API with TFLite"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fish-detection-api.git
git push -u origin main
```

### Step 2: Connect to Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select **Deploy an existing Docker image from a registry** OR **Build and deploy from a Git repository**

### Step 3: Option A - From GitHub Repository (Recommended)

1. Choose **GitHub** as the source
2. Authorize Render to access your GitHub repositories
3. Select `fish-detection-api` repository
4. Choose branch: `main`
5. Enable **Auto-deploy** (automatic redeploy on push)

### Step 4: Configuration in Render Dashboard

#### Basic Settings
- **Name**: `fish-detection-api`
- **Region**: Choose closest to your users (e.g., `Oregon`, `Virginia`)
- **Branch**: `main`
- **Root Directory**: `fastapi_app` (if applicable, leave empty otherwise)

#### Build Settings
- **Runtime**: `Docker`
- **Dockerfile Path**: `Dockerfile` (default)
- **Docker Build Context**: `.`

#### Port Configuration
- **Port**: `10000` (Render assigns dynamic port - don't use 8000)
- **Protocol**: `HTTP`

#### Environment Variables
Add these in the Render dashboard:
```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
LOG_LEVEL=info
WORKERS=4
```

#### Health Check
- **Path**: `/health`
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds

### Step 5: Disk Storage for Models

Models are large and exceed Render's default limits. Use **Persistent Disk**:

1. In Render dashboard, go to **Disks** tab
2. Click **Create Disk**
   - **Name**: `model-storage`
   - **Size**: 20 GB (adjust as needed)
   - **Mount Path**: `/app/model`

3. Attach disk to service

### Step 6: Upload Model Files

#### Option A: Upload via Git LFS (Recommended for < 100GB)
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.pt"
git lfs track "*.h5"
git lfs track "*.tflite"
git add .gitattributes

# Commit and push
git add best.pt efficientnet_fish.h5 model/
git commit -m "Add model files with Git LFS"
git push origin main
```

#### Option B: Upload Files Directly After Deployment
1. Deploy first with minimal files
2. Use Render Shell access to upload:
```bash
# SSH into running service (via Render dashboard)
curl -X POST -F "file=@best.pt" http://localhost:10000/upload/
```

#### Option C: Reference External Model Storage
Store models in AWS S3, Google Cloud Storage, or similar:
```bash
# Download from external storage on container startup
#!/bin/bash
if [ ! -f /app/model/fish.tflite ]; then
    aws s3 cp s3://your-bucket/models/ /app/model/ --recursive
fi
```

### Step 7: Deploy

1. In Render dashboard, click **Create Web Service**
2. Wait for deployment (5-15 minutes)
3. Once deployed, you'll get a URL: `https://fish-detection-api-xxxxx.onrender.com`

### Step 8: Test Deployment

```bash
# Health check
curl https://fish-detection-api-xxxxx.onrender.com/health

# API documentation
https://fish-detection-api-xxxxx.onrender.com/docs

# Test prediction
curl -X POST "https://fish-detection-api-xxxxx.onrender.com/predict" \
  -H "accept: application/json" \
  -F "file=@test_image.jpg"
```

## Important: Port Configuration

⚠️ **Render assigns a dynamic port** - Do NOT hardcode port 8000

The Dockerfile is already configured correctly:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

Render maps: Container Port 10000 → HTTPS Port 443 (auto-managed)

## Critical: Model File Size

### File Size Considerations
- `best.pt`: ~100 MB
- `efficientnet_fish.h5`: ~50-200 MB  
- `fish.tflite`: ~50-100 MB
- **Total**: ~200-400 MB

### Solutions for Large Models

**Option 1: Use Persistent Disk** (Recommended)
- Attach 20GB persistent disk at `/app/model`
- Models persist across deployments
- No need to re-upload

**Option 2: Use Model Streaming Service**
```python
# In model_loader.py
def download_models_if_needed():
    """Download models from S3 on startup"""
    import boto3
    import os
    
    if not os.path.exists('model/Disease_model/fish.tflite'):
        s3 = boto3.client('s3')
        s3.download_file(
            'your-bucket',
            'models/fish.tflite',
            'model/Disease_model/fish.tflite'
        )
```

**Option 3: Use .gitignore + External Storage**
```bash
# .gitignore
*.pt
*.h5  
*.tflite
model/Disease_model/

# Download at startup in Dockerfile
RUN apt-get install -y awscli
```

## Environment Variables in Render

Set in Render Dashboard under **Environment**:

```
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
LOG_LEVEL=info
WORKERS=4
MODEL_DOWNLOAD_URL=https://your-bucket.s3.aws.com/models/
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Troubleshooting

### Deployment Fails
```
Check logs in Render dashboard → Logs tab
Common issues:
- Missing requirements in requirements.txt
- Model files not found
- Disk not attached
```

### Model Files Not Found
```
Verify:
1. Persistent disk attached at /app/model
2. Models uploaded correctly
3. Path in code matches: model/Disease_model/fish.tflite
```

### Out of Memory
Render Standard plan has:
- **CPU**: 0.5 cores
- **RAM**: 512 MB
- **Upgrade to**: Pro plan (4 cores, 7GB RAM) if needed

### Timeout Issues
Increase timeout in Render settings:
- **HTTP Timeout**: 600 seconds (for large file uploads)
- **Health Check Timeout**: 10 seconds

### CORS Issues
In `fastapi_app/app/main.py`, verify CORS is enabled:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Cost Estimation

| Plan | CPU | Memory | Price/month |
|------|-----|--------|-------------|
| Free | Shared | 512 MB | $0 (limited) |
| Standard | 0.5 | 512 MB | $7 |
| Pro | 4 | 7 GB | $28 |
| Premium | 8 | 15 GB | $78 |

*Model storage disk: ~$0.20 per GB/month*

## Auto-Deployment

Edit `render.yaml` to automatically deploy on push:
```yaml
autoDeploy: true
```

The service will redeploy automatically when you push to GitHub.

## Custom Domain (Optional)

1. In Render dashboard, go to **Settings** → **Custom Domains**
2. Add your domain: `api.yourdomain.com`
3. Follow DNS configuration steps

## Monitoring

### View Logs
- Render Dashboard → **Logs** tab
- Real-time logs as service runs

### Metrics
- CPU usage
- Memory usage
- Request count
- Response times

Click **Metrics** in Render dashboard

## Database Setup (If Needed)

For future enhancements:

1. Create PostgreSQL database in Render
2. Add connection string to environment variables
3. Update FastAPI to use database

## Backup & Recovery

1. Enable automatic backups in Render
2. Export persistent disk data regularly
3. Keep code in GitHub for version control

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Connect GitHub to Render
3. ✅ Set up persistent disk
4. ✅ Upload model files
5. ✅ Deploy and test
6. ✅ Monitor logs and metrics
7. ✅ Set custom domain (optional)

## Support

- **Render Docs**: https://render.com/docs
- **Status Page**: https://status.render.com
- **Community**: https://render.com/community
