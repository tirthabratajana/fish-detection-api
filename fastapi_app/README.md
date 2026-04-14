# 🐟 Fish Species Detection API

FastAPI backend for three-stage fish species detection, classification, and disease detection.

## 📋 Architecture

### Three-Stage Pipeline:
```
Input Image (JPG/PNG)
         ↓
   Stage 1: YOLOv8s
   (Fish Detection)
         ↓
   Crops Fish Region
         ↓
   Stage 2: EfficientNetB3
   (Species Classification: 5 classes)
         ↓
   Stage 3: EfficientNetB0 (SavedModel)
   (Disease Detection: Healthy/Diseased)
         ↓
   Predicted Species + Confidence + Health Status
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd fastapi_app
pip install -r requirements.txt
```

### 2. Prepare Models

Make sure your trained models are in the root directory:
- `best.pt` - YOLOv8s detection model
- `efficientnet_fish.h5` - EfficientNetB3 species classification model
- `model/Disease_model/saved_model/` - EfficientNetB0 disease detection model (SavedModel format)
- `clf_class_names.json` - Class names mapping (optional)

You can also place them in the `best_pt_folder` directory.

### 3. Run the Server

```bash
# Using the run script
python run.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## 📚 API Endpoints

### Health Check
- **GET** `/health`
  - Returns API and models status

### Single Image Prediction
- **POST** `/predict`
  - Upload a single fish image
  - Returns species prediction with confidence
  - Request: multipart/form-data with file field
  - Response: PredictionResult JSON

### Batch Prediction
- **POST** `/predict-batch`
  - Upload multiple fish images (max 10)
  - Returns predictions for all images
  - Request: multipart/form-data with files field
  - Response: Array of predictions

### API Info
- **GET** `/`
  - Returns API information and available endpoints

## 🧪 Testing with Postman

### 1. Start the Server
```bash
python run.py
```

### 2. Test Health Endpoint
- **Method**: GET
- **URL**: `http://localhost:8000/health`
- **Expected Response**:
```json
{
  "status": "✅ Healthy",
  "yolo_model_loaded": true,
  "efficientnet_model_loaded": true,
  "message": "All models loaded and ready"
}
```

### 3. Test Single Prediction
- **Method**: POST
- **URL**: `http://localhost:8000/predict`
- **Headers**: 
  - Content-Type: multipart/form-data
- **Body**: 
  - Select "file" (form-data key)
  - Upload a fish image file
- **Expected Response**:
```json
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
  "is_valid_detection": true,
  "all_class_probabilities": [
    {
      "class_name": "Catla",
      "probability": 0.95,
      "confidence_percent": "95.00%"
    },
    {
      "class_name": "CommonCarp",
      "probability": 0.03,
      "confidence_percent": "3.00%"
    },
    ...
  ],
  "message": "Species: Catla | Health: HEALTHY",
  "detection_count": 1
}
```

### 4. Test Batch Prediction
- **Method**: POST
- **URL**: `http://localhost:8000/predict-batch`
- **Headers**: 
  - Content-Type: multipart/form-data
- **Body**: 
  - Select "files" (form-data key)
  - Upload multiple fish image files
- **Expected Response**:
```json
{
  "batch_size": 3,
  "results": [
    {
      "filename": "fish1.jpg",
      "prediction": { ... }
    },
    {
      "filename": "fish2.png",
      "prediction": { ... }
    },
    ...
  ]
}
```

## 🌐 Interactive API Documentation

Once the server is running:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

You can test all endpoints directly from the browser!

## 📁 Project Structure

```
fastapi_app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application & endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── model_loader.py     # Model loading & management
│   │   └── image_processor.py  # Two-stage inference pipeline
│   └── schemas/
│       ├── __init__.py
│       └── models.py           # Pydantic request/response models
├── requirements.txt            # Python dependencies
├── run.py                      # Startup script
└── README.md                   # This file
```

## 🔌 Response Formats

### Successful Prediction
```json
{
  "success": true,
  "species": "Rohu",
  "species_confidence": 0.92,
  "species_confidence_percent": "92.00%",
  "disease_status": "HEALTHY",
  "disease_confidence": 0.85,
  "disease_confidence_percent": "85.00%",
  "yolo_confidence": 0.85,
  "yolo_confidence_percent": "85.00%",
  "is_valid_detection": true,
  "all_class_probabilities": [
    {
      "class_name": "Rohu",
      "probability": 0.92,
      "confidence_percent": "92.00%"
    },
    ...
  ],
  "message": "Species: Rohu | Health: HEALTHY",
  "detection_count": 1
}
```

### No Fish Detected
```json
{
  "success": false,
  "species": "Unknown",
  "species_confidence": 0.0,
  "species_confidence_percent": "0.00%",
  "disease_status": "UNKNOWN",
  "disease_confidence": 0.0,
  "disease_confidence_percent": "0.00%",
  "yolo_confidence": 0.0,
  "yolo_confidence_percent": "0.00%",
  "is_valid_detection": false,
  "all_class_probabilities": [],
  "message": "No fish detected in image",
  "detection_count": 0
}
```

### Error Response
If the request fails, you'll get an HTTP error (400, 500, etc.) with details.

## 📊 Supported Fish Species

The model recognizes 5 fish species from the StockFish dataset:
1. **Catla** - Major Indian carp
2. **CommonCarp** - Common freshwater carp
3. **Mori** - Mrigal carp
4. **Rohu** - Indian major carp
5. **SilverCarp** - Asian carp

## ⚙️ Configuration

### Model Paths
Edit `app/main.py` to change model paths:
- `YOLO_MODEL_PATH` - Path to best.pt
- `EFFICIENTNET_MODEL_PATH` - Path to efficientnet_fish.h5
- `CLASS_MAP_PATH` - Path to clf_class_names.json

### YOLO Confidence Threshold
In `app/main.py`, modify the `yolo_conf` parameter (default: 0.20):
```python
ImageProcessor.run_inference(
    ...
    yolo_conf=0.20  # Lower = more detections, higher = more confident
)
```

## 🐛 Troubleshooting

### Models not loading
1. Verify model file paths are correct
2. Check if model files are corrupted
3. Ensure sufficient disk space and RAM

### Out of memory errors
1. Reduce image size in requests
2. Use CPU prediction (modify model_loader.py)
3. Restart the server

### Slow predictions
1. Wait for first inference (model warming up)
2. Subsequent requests are faster
3. Use batch processing for multiple images

## 📝 Logging

All activity is logged to console with timestamps:
```
INFO - 2024-03-17 10:30:45 - 🚀 Fish Detection API Starting Up
INFO - 2024-03-17 10:30:45 - Loading YOLO model...
INFO - 2024-03-17 10:30:48 - ✅ YOLO model loaded successfully
...
```

## 🔐 Security Notes

- Input validation for file types and sizes
- CORS enabled for all origins (modify for production)
- Error messages don't expose system paths in production
- All file uploads are validated before processing

## 📦 Dependencies

- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **TensorFlow/Keras**: Deep learning framework
- **PyTorch/Ultralytics**: YOLO model framework
- **Pillow**: Image processing
- **OpenCV**: Computer vision
- **NumPy**: Numerical computing

All dependencies are listed in `requirements.txt`

## 🎯 Performance Metrics

Expected inference times on GPU:
- YOLO Detection: ~50-100ms
- EfficientNet Classification: ~100-200ms
- Total: ~150-300ms per image

## 📄 License

This project uses trained models from your notebook. Please refer to original model licenses and dataset terms.

## 🤝 Support

For issues or improvements, refer to the main notebook documentation at:
`Fish_Species_Detection_Updated (1).ipynb`

---

**Built on**: FastAPI 0.104 | TensorFlow 2.14 | Ultralytics 8.0
