# 🚀 FastAPI Fish Detection Backend - Setup Guide

## Prerequisites

- Python 3.9+ installed
- GPU (NVIDIA CUDA) recommended but not required
- Trained models from the notebooks:
  - `best.pt` (YOLOv8s detection model)
  - `efficientnet_fish.h5` (EfficientNetB3 species classification model)
  - `model/Disease_model/saved_model/` (EfficientNetB0 disease detection model - SavedModel format)
  - `clf_class_names.json` (class names mapping)

## Step 1: Install Dependencies

```bash
# Navigate to the fastapi_app directory
cd fastapi_app

# Install all required packages
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes as it installs TensorFlow, PyTorch, and other large packages.

If you encounter issues, install in smaller batches:
```bash
pip install fastapi uvicorn python-multipart pydantic
pip install pillow opencv-python numpy
pip install tensorflow
pip install torch torchvision
pip install ultralytics
```

## Step 2: Prepare Model Files

### Option A: Models in Root Directory (Recommended)
Place your trained models in `e:\fish model backend\`:
```
e:\fish model backend\
├── best.pt                                ← YOLO detection model
├── efficientnet_fish.h5                   ← EfficientNet species model
├── clf_class_names.json                   ← Class names
├── model/
│   └── Disease_model/
│       └── saved_model/                   ← SavedModel format (with saved_model.pb, variables/, etc.)
│           ├── saved_model.pb
│           ├── variables/
│           └── assets/
├── fastapi_app/
│   ├── app/
│   ├── run.py
│   ├── requirements.txt
│   └── README.md
```

### Option B: Models in best_pt_folder
If models are in `best_pt_folder/`:
```
e:\fish model backend\
├── best_pt_folder/
│   ├── best.pt
│   ├── efficientnet_fish.h5
│   └── clf_class_names.json
├── fastapi_app/
│   ├── app/
│   │   └── main.py         ← Already configured to check both locations
```

The `app/main.py` automatically checks both locations.

## Step 3: Run the Server

### Method 1: Using the Run Script
```bash
cd fastapi_app
python run.py
```

### Method 2: Using Uvicorn Directly
```bash
cd fastapi_app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Expected Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     2024-03-17 10:30:45 - 🚀 Fish Detection API Starting Up
INFO:     2024-03-17 10:30:45 - Loading YOLO model...
INFO:     2024-03-17 10:30:48 - ✅ YOLO model loaded successfully
INFO:     2024-03-17 10:30:48 - Loading EfficientNet model...
INFO:     2024-03-17 10:30:52 - ✅ EfficientNet model loaded successfully
INFO:     2024-03-17 10:30:52 - ✅ All models loaded successfully!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

If you see `✅ All models loaded successfully!`, the server is ready!

## Step 4: Test the API

### Option A: Browser (Interactive Documentation)
Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

### Option B: Postman (Recommended)

1. **Import the Collection**:
   - Open Postman
   - Click "Import" → "Upload Files"
   - Select `Fish_Detection_API.postman_collection.json`

2. **Test Health Check**:
   - Select "Health Check" request
   - Click "Send"
   - You should get a 200 response with status "✅ Healthy"

3. **Test Prediction**:
   - Select "Predict Single Fish Image"
   - Click the file selector and choose a fish image
   - Click "Send"
   - View the prediction result

### Option C: curl (Command Line)

**Health Check:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Single Prediction (Replace path/to/fish.jpg with your image):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/fish.jpg"
```

**Batch Prediction:**
```bash
curl -X POST "http://localhost:8000/predict-batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@fish1.jpg" \
  -F "files=@fish2.jpg"
```

## Step 5: Verify It's Working

Check the server logs - you should see:
```
✅ YOLO model loaded successfully
✅ EfficientNet model loaded successfully
✅ All models loaded successfully!
```

If you see these messages, you're ready to test!

## Step 6: Interpret Results

### Success Response Example:
```json
{
  "success": true,
  "species": "Catla",
  "species_confidence": 0.9523,
  "species_confidence_percent": "95.23%",
  "yolo_confidence": 0.8742,
  "yolo_confidence_percent": "87.42%",
  "is_valid_detection": true,
  "all_class_probabilities": [
    {
      "class_name": "Catla",
      "probability": 0.9523,
      "confidence_percent": "95.23%"
    },
    {
      "class_name": "Rohu",
      "probability": 0.0312,
      "confidence_percent": "3.12%"
    },
    {
      "class_name": "CommonCarp",
      "probability": 0.0089,
      "confidence_percent": "0.89%"
    },
    {
      "class_name": "SilverCarp",
      "probability": 0.0054,
      "confidence_percent": "0.54%"
    },
    {
      "class_name": "Mori",
      "probability": 0.0022,
      "confidence_percent": "0.22%"
    }
  ],
  "message": "Successfully detected and classified as Catla",
  "detection_count": 1
}
```

### No Fish Detected:
```json
{
  "success": false,
  "species": "Unknown",
  "species_confidence": 0.0,
  "species_confidence_percent": "0.00%",
  "yolo_confidence": 0.0,
  "yolo_confidence_percent": "0.00%",
  "is_valid_detection": false,
  "all_class_probabilities": [],
  "message": "No fish detected in image",
  "detection_count": 0
}
```

## Troubleshooting

### ❌ "Models not found" Error

**Problem**: `FileNotFoundError: YOLO model not found`

**Solution**:
1. Verify model file paths are correct in `app/main.py`
2. Check models exist in the correct directory:
   ```bash
   # In PowerShell
   dir "e:\fish model backend\best.pt"
   dir "e:\fish model backend\efficientnet_fish.h5"
   ```
3. Update paths in `app/main.py` if needed

### ❌ Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Then access the API at `http://localhost:8001`

### ❌ Out of Memory Error

**Problem**: `tensorflow.python.framework.errors_impl.ResourceExhaustedError`

**Solution**:
1. Close other applications to free RAM
2. Reduce image size before uploading
3. Restart the server

### ❌ CUDA/GPU Error

**Problem**: `tensorflow.python.framework.errors_impl.InvalidArgumentError`

**Solution**:
1. CPU inference will be used automatically
2. Or explicitly disable GPU (modify app/main.py):
   ```python
   import os
   os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU
   ```

### ❌ 500 Internal Server Error

**Problem**: Error processing the image

**Solution**:
1. Check the server logs for detailed error messages
2. Verify the image format is JPG, PNG, BMP, or WEBP
3. Try a different image
4. Make sure the image is a valid fish image

## Advanced Configuration

### Change API Port
Command line:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Change Model Paths
Edit `app/main.py` (lines 35-45):
```python
YOLO_MODEL_PATH = "your/path/to/best.pt"
EFFICIENTNET_MODEL_PATH = "your/path/to/efficientnet_fish.h5"
CLASS_MAP_PATH = "your/path/to/clf_class_names.json"
```

### Adjust YOLO Confidence Threshold
In `app/main.py` at the `predict_fish` function:
```python
result_dict = ImageProcessor.run_inference(
    ...
    yolo_conf=0.15  # Lower = more detections (more false positives)
                     # Higher = fewer detections (more reliable)
)
```

### View Request Logs
All requests are logged. View logs in the terminal where you started the server.

## Performance Tips

1. **First request is slower** (model warming up) - subsequent requests are faster
2. **GPU usage** - ensure NVIDIA drivers are installed for faster inference
3. **Batch processing** - use `/predict-batch` for multiple images
4. **Image quality** - clearer images = better predictions

## Next Steps

### 1. Add Authentication
Protect your API with:
- API keys
- OAuth2
- JWT tokens

### 3. Add Database
Store predictions:
- SQLite
- PostgreSQL
- MongoDB

### 4. Monitor Performance
Use tools like:
- Prometheus metrics
- Application Performance Monitoring (APM)
- Error tracking (Sentry)

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Uvicorn Documentation**: https://www.uvicorn.org
- **Postman Learning**: https://learning.postman.com
- **TensorFlow Documentation**: https://www.tensorflow.org
- **Ultralytics YOLOv8**: https://docs.ultralytics.com

## Support

If you encounter issues:

1. **Check the logs** - server output usually has helpful error messages
2. **Review README.md** - for API endpoint documentation
3. **Test with Postman** - interactive testing is easier than curl
4. **Verify model files** - ensure they exist and are not corrupted
5. **Restart the server** - often fixes temporary issues

---

**Happy Fish Detecting! 🐟** 

For issues with the models themselves, refer back to the main notebook:
`Fish_Species_Detection_Updated (1).ipynb`
