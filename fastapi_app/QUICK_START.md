# 🚀 FastAPI Backend - Getting Started in 3 Steps

## ✅ Step 1: Install Dependencies (5 minutes)

```bash
cd e:\fish model backend\fastapi_app\
pip install -r requirements.txt
```

**What this does:**
- Downloads and installs all required packages
- Includes: FastAPI, TensorFlow, PyTorch, Ultralytics, OpenCV, etc.
- Creates Python environment with all dependencies

---

## ✅ Step 2: Prepare Models (30 seconds)

Make sure your trained models are in the **root directory**:
```
e:\fish model backend\
├── best.pt                                ← YOLO detection model
├── efficientnet_fish.h5                   ← EfficientNet species model  
├── clf_class_names.json                   ← Class names (optional)
├── model/Disease_model/saved_model/       ← Disease detection model (SavedModel format)
└── fastapi_app\
```

**Or in `best_pt_folder/`:**
```
e:\fish model backend\best_pt_folder\
├── best.pt
├── efficientnet_fish.h5
└── clf_class_names.json
```

The app automatically checks both locations. The disease detection model uses SavedModel format for optimal performance.

---

## ✅ Step 3: Run the Server (1 minute)

```bash
# From the fastapi_app directory:
python run.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     ✅ YOLO model loaded successfully
INFO:     ✅ EfficientNet model loaded successfully
INFO:     ✅ Disease Detection model loaded successfully (SavedModel)
INFO:     ✅ All models loaded successfully!
```

**Server is ready!** 🎉

---

## 🧪 Test the API (Choose One)

### Option 1️⃣: Browser (Easiest)
Open: **http://localhost:8000/docs**

You'll see:
- Interactive Swagger UI
- All API endpoints listed
- Test requests directly in browser
- Live API documentation

Click "Try it out" on any endpoint to test!

### Option 2️⃣: Postman
1. Open Postman
2. Click "Import"
3. Select: `Fish_Detection_API.postman_collection.json`
4. All test requests are pre-configured!
5. Upload a fish image and click "Send"

### Option 3️⃣: curl (Command Line)
```bash
# Test health
curl http://localhost:8000/health

# Test prediction
curl -X POST "http://localhost:8000/predict" \
  -F "file=@your_fish_image.jpg"
```

---

## 📊 What You Get

### Three API Endpoints:

#### 1. **POST /predict** - Single Fish Image
- Upload: 1 fish image (JPG, PNG, BMP, WEBP)
- Get: Species prediction + confidence scores
- Time: ~200-300ms per image

```
Request:
- Method: POST
- URL: http://localhost:8000/predict
- Body: multipart/form-data with "file" field

Response (Example):
{
  "success": true,
  "species": "Catla",
  "species_confidence": 0.95,
  "species_confidence_percent": "95.00%",
  "disease_status": "HEALTHY",
  "disease_confidence": 0.87,
  "disease_confidence_percent": "87.00%",
  "yolo_confidence": 0.87,
  "yolo_confidence_percent": "87.00%",
  "all_class_probabilities": [
    {"class_name": "Catla", "probability": 0.95, "confidence_percent": "95.00%"},
    {"class_name": "Rohu", "probability": 0.03, "confidence_percent": "3.00%"},
    ...
  ],
  "message": "Species: Catla | Health: HEALTHY",
  "detection_count": 1
}
```

#### 2. **POST /predict-batch** - Multiple Fish Images
- Upload: 1-10 fish images
- Get: Predictions for all images
- Time: Sequential (per-image time × number of images)

```
Request:
- Method: POST
- URL: http://localhost:8000/predict-batch
- Body: multipart/form-data with "files" field (multiple)

Response:
{
  "batch_size": 3,
  "results": [
    {"filename": "fish1.jpg", "prediction": {...}},
    {"filename": "fish2.jpg", "prediction": {...}},
    {"filename": "fish3.jpg", "prediction": {...}}
  ]
}
```

#### 3. **GET /health** - Health Check
- Get: API status and model status

```
Request:
- Method: GET
- URL: http://localhost:8000/health

Response:
{
  "status": "✅ Healthy",
  "yolo_model_loaded": true,
  "efficientnet_model_loaded": true,
  "message": "All models loaded and ready"
}
```

---

## 📁 What's in Each Folder

### `app/` - Application Code
```
main.py          ← Main FastAPI app (read this to understand endpoints)
utils/
  model_loader.py   ← Loads YOLO and EfficientNet
  image_processor.py ← Two-stage inference pipeline
schemas/
  models.py      ← Request/response validation
```

### `docs/` - Documentation (Read These!)
```
README.md         ← Complete API documentation
SETUP_GUIDE.md    ← Detailed setup & troubleshooting
DOCKER.md         ← Deploy with Docker
PROJECT_SUMMARY.md ← Quick overview
FILE_REFERENCE.md ← Complete file inventory
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Models not found** | Copy `best.pt` and `efficientnet_fish.h5` to root or `best_pt_folder/` |
| **Port 8000 already in use** | Change port: `uvicorn app.main:app --port 8001` |
| **Out of memory** | Close other apps, restart server, or use smaller images |
| **GPU/CUDA errors** | Automatically falls back to CPU, no action needed |
| **Installation fails** | Try installing TensorFlow separately: `pip install tensorflow` |

**Still stuck?** → Read `SETUP_GUIDE.md` (Troubleshooting section)

---

## 🎯 Common Tasks

### Change YOLO Detection Threshold
Edit `app/main.py`, find `yolo_conf=0.20` and change:
- Lower values = detect smaller fish
- Higher values = only confident detections

### Change API Port
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Run in Background
```bash
# Windows
start python run.py

# Linux/macOS
nohup python run.py > server.log 2>&1 &
```

---

## 📈 Performance Expectations

### Single Image Processing
- YOLO Detection: 50-100ms
- EfficientNet Classification: 100-200ms
- **Total: 150-300ms**

First request may be slower (model warmup).

### Batch Processing (10 images)
- Total time: ~1.5-3 seconds
- Sequential processing (one after another)

### Memory Usage
- Loaded models: ~500 MB - 1 GB
- Per-image: ~100 MB temporary
- Recommend: 4 GB RAM minimum, 8 GB+ recommended

### GPU Support
- Auto-detects NVIDIA GPU
- Falls back to CPU if not available
- No configuration needed!

---

## 📚 Documentation Quick Links

| Task | Read This |
|------|-----------|
| Understand the API | `README.md` |
| Set up the server | `SETUP_GUIDE.md` |
| Project overview | `PROJECT_SUMMARY.md` |
| File inventory | `FILE_REFERENCE.md` |
| All endpoints | http://localhost:8000/docs |

---

## 🔄 Architecture at a Glance

```
┌─────────────────────────────────────┐
│     Upload Fish Image (JPG/PNG)     │
└──────────────┬──────────────────────┘
               ▼
┌──────────────────────────────────────┐
│    STAGE 1: YOLOv8s Detection        │
│  Detects fish + bounding box         │
│  Output: Confidence score            │
└──────────────┬───────────────────────┘
               ▼
        ┌──────────────┐
        │ Crop Region  │
        └──────────────┘
               ▼
┌──────────────────────────────────────┐
│  STAGE 2: EfficientNetB3 Classification
│  Classifies fish species             │
│  Output: Species + 5-class scores    │
└──────────────┬───────────────────────┘
               ▼
    ┌─────────────────────────┐
    │  Prediction Result      │
    ├─────────────────────────┤
    │ Species: Catla          │
    │ Confidence: 95.00%      │
    │ YOLO Conf: 87.00%       │
    │ All class scores        │
    └─────────────────────────┘
```

---

## 🎊 You're All Set!

Your FastAPI backend is ready to:
✅ Accept image uploads  
✅ Detect fish with YOLOv8s  
✅ Classify species with EfficientNet  
✅ Return predictions via REST API  
✅ Serve multiple users concurrently  
✅ Scale to production  

### Next Actions:
1. **Run**: `python run.py`
2. **Test**: http://localhost:8000/docs
3. **Upload**: A fish image
4. **Get**: Species prediction + confidence!


### Want More Details?
→ See `README.md` for complete documentation

---

**Happy Fish Detecting! 🐟**

Made with ❤️ using FastAPI, YOLOv8, and EfficientNet
