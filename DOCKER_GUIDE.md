# Docker Deployment Guide

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM available
- 10GB+ disk space for models and images

## Quick Start

### 1. Build and Run with Docker Compose
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f fish-detection-api

# Check status
docker-compose ps
```

### 2. Access the API
- **API Endpoint**: http://localhost:8000
- **API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/health

# Predict with image
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -F "file=@/path/to/image.jpg"
```

## Docker Compose Configuration

### Service Details
- **Container Name**: fish-detection-api
- **Port**: 8000
- **Image**: Built from Dockerfile

### Volumes Mounted
- `./model/` → Read-only access to models (RO)
- `./best.pt` → YOLO model (RO)
- `./best_pt_folder/` → Classification models (RO)
- `./efficientnet_fish.h5` → EfficientNet model (RO)
- `./clf_class_names.json` → Class names (RO)
- `./logs/` → Application logs (RW)
- `./uploads/` → Uploaded images (RW)

### Resource Limits
- **CPU Limit**: 2 cores
- **Memory Limit**: 8GB
- **CPU Reservation**: 1 core
- **Memory Reservation**: 4GB

*Adjust these in docker-compose.yml based on your system capacity*

### Health Check
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start Period: 40 seconds

## Build Manually (Without Compose)

### Build Image
```bash
docker build -t fish-detection-api:latest .
```

### Run Container
```bash
docker run -d \
  --name fish-detection-api \
  -p 8000:8000 \
  -v $(pwd)/model:/app/model:ro \
  -v $(pwd)/best.pt:/app/best.pt:ro \
  -v $(pwd)/best_pt_folder:/app/best_pt_folder:ro \
  -v $(pwd)/efficientnet_fish.h5:/app/efficientnet_fish.h5:ro \
  -v $(pwd)/clf_class_names.json:/app/clf_class_names.json:ro \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/uploads:/app/uploads \
  --restart unless-stopped \
  fish-detection-api:latest
```

## Common Commands

### View Logs
```bash
# Real-time logs
docker-compose logs -f fish-detection-api

# Last 100 lines
docker-compose logs --tail=100 fish-detection-api
```

### Stop Services
```bash
docker-compose down
```

### Remove Images and Volumes
```bash
docker-compose down -v
```

### Rebuild Image
```bash
docker-compose build --no-cache
```

### Shell Access
```bash
docker-compose exec fish-detection-api bash
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs fish-detection-api

# Restart service
docker-compose restart fish-detection-api
```

### Out of Memory
- Increase memory limit in `docker-compose.yml`
- Reduce batch size in API requests
- Ensure sufficient host memory is available

### Model Files Not Found
```bash
# Verify volume mounts
docker-compose exec fish-detection-api ls -la /app/model/

# Check if files exist on host
ls -la ./model/
ls -la ./best.pt
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
# Change: "8000:8000" to "9000:8000"
docker-compose up -d
# Access at http://localhost:9000
```

## Performance Optimization

### GPU Support (NVIDIA)
To enable GPU support, add to `docker-compose.yml`:
```yaml
services:
  fish-detection-api:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

### Multi-worker Setup
Edit `docker-compose.yml` environment:
```yaml
environment:
  - WORKERS=8  # Increase based on CPU cores
```

## Security Notes
- Models are mounted as read-only (`:ro`)
- Remove exposed ports in production, use reverse proxy
- Set environment variables in `.env` file
- Use secrets for sensitive data
- Implement API authentication/rate limiting

## File Structure
```
fish model backend/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── fastapi_app/
│   ├── app/
│   ├── requirements.txt
│   └── run.py
├── model/
│   └── Disease_model/
│       └── fish.tflite
├── best.pt
├── best_pt_folder/
├── efficientnet_fish.h5
├── clf_class_names.json
├── logs/               (created at runtime)
└── uploads/           (created at runtime)
```
