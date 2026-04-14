# 🐟 Fish Detection API - Project Structure

## Directory Tree

```
fish model backend/
│
├── fastapi_app/                          # FastAPI Application Root
│   ├── app/                              # Application Package
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app definition & endpoints
│   │   │
│   │   ├── utils/                        # Utility modules
│   │   │   ├── __init__.py
│   │   │   ├── model_loader.py           # Model loading utilities
│   │   │   └── image_processor.py        # Image processing & inference pipeline
│   │   │
│   │   └── schemas/                      # Pydantic response models
│   │       ├── __init__.py
│   │       └── models.py                 # Response schemas
│   │
│   ├── run.py                            # Application entry point
│   ├── requirements.txt                  # Python dependencies
│   ├── .env.example                      # Environment variables template
│   │
│   ├── Documentation/
│   │   ├── README.md                     # Main documentation
│   │   ├── QUICK_START.md                # Quick start guide
│   │   ├── SETUP_GUIDE.md                # Detailed setup instructions
│   │   ├── PROJECT_SUMMARY.md            # Project overview
│   │   ├── INDEX.md                      # Documentation index
│   │   ├── FILE_REFERENCE.md             # File reference guide
│   │   └── PROJECT_STRUCTURE.md          # This file
│   │
│   ├── Debug Scripts/
│   │   └── debug_disease_model.py        # Disease model debugging script
│   │
│   ├── API Documentation/
│   │   └── Fish_Detection_API.postman_collection.json  # Postman collection
│   │
│   └── __pycache__/                      # Python cache (auto-generated)
│
├── best.pt                               # YOLOv8s detection model
├── efficientnet_fish.h5                  # EfficientNetB3 species classifier
├── clf_class_names.json                  # Species class names mapping
│
├── model/
│   ├── Disease_model/
│   │   ├── fish_model.tflite            # TFLite model (legacy)
│   │   └── saved_model/                 # SavedModel format (current)
│   │       ├── saved_model.pb
│   │       ├── fingerprint.pb
│   │       ├── variables/
│   │       │   ├── variables.index
│   │       │   └── variables.data-00000-of-00001
│   │       └── assets/
│   │
│   └── efficientnet/                    # Species classification models
│   └── yolov8s/                         # Detection models
│
├── best_pt_folder/                      # Alternative model folder
│   ├── data/
│   │   ├── 0, 1, 2, ... 358            # Fish image dataset indices
│   │   └── ...
│   ├── byteorder
│   └── version
│
├── runs/                                 # Training/detection outputs
│   └── detect/
│
├── sample test pics/                    # Test images
│   ├── WhatsApp Image 2026-03-21 at 4.25.05 PM (1).jpeg
│   ├── WhatsApp Image 2026-03-21 at 4.25.42 PM.jpeg
│   ├── WhatsApp Image 2026-03-23 at 7.43.31 PM.jpeg
│   └── ... (10 total images)
│
├── Saved model file/
│   └── predict.py                       # Reference disease detection implementation
│
├── Fish_Species_Detection_Updated (1).ipynb  # Species detection notebook
├── Fishlatest.ipynb                     # Latest training notebook
│
└── debug scripts/
    ├── test_api.py
    ├── test_batch_api.py
    ├── final_test_all_images.py
    └── ... (other test scripts)
```

## File Descriptions

### Core Application Files

| File | Purpose |
|------|---------|
| `run.py` | Entry point - starts FastAPI server on port 8000 |
| `app/main.py` | FastAPI app definition, endpoint routes (/predict, /predict-batch, /health) |
| `app/utils/model_loader.py` | Loads YOLO, EfficientNet, and SavedModel disease detector |
| `app/utils/image_processor.py` | 3-stage inference pipeline (detection → classification → disease detection) |
| `app/schemas/models.py` | Pydantic response models (PredictionResult, HealthCheck, etc.) |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables |

### Model Files

| File | Size | Purpose |
|------|------|---------|
| `best.pt` | ~45MB | YOLOv8 Small - Fish detection |
| `efficientnet_fish.h5` | ~34MB | EfficientNetB3 - Species classification (5 classes) |
| `saved_model/` | ~20MB | SavedModel format - Disease detection (EfficientNetB0) |
| `clf_class_names.json` | ~1KB | Species mapping: {0: Catla, 1: CommonCarp, ...} |

### Documentation Files

| File | Content |
|------|---------|
| `README.md` | Main documentation overview |
| `QUICK_START.md` | 5-minute quick start guide |
| `SETUP_GUIDE.md` | Detailed installation & setup |
| `PROJECT_SUMMARY.md` | Technical project summary |
| `INDEX.md` | Documentation index |
| `FILE_REFERENCE.md` | Detailed file reference |
| `PROJECT_STRUCTURE.md` | This file - directory structure |

### Test & Debug Files

| File | Purpose |
|------|---------|
| `debug_disease_model.py` | Debug disease detection SavedModel |
| `test_api.py` | Test single image prediction |
| `test_batch_api.py` | Test batch prediction endpoint |
| `final_test_all_images.py` | Comprehensive test of all samples |

---

## Key Directories Explained

### `fastapi_app/app/`
Main application package containing FastAPI setup, utilities, and schemas.

### `fastapi_app/model/Disease_model/`
Contains disease detection models:
- `fish_model.tflite` - TFLite format (legacy, not used)
- `saved_model/` - **Current format** (224×224 input, threshold: 0.40)

### `sample test pics/`
10 test fish images for validation and testing:
- 7 images classified as HEALTHY
- 2 images classified as DISEASED
- 1 image with detection failure (UNKNOWN)

### `best_pt_folder/`
Contains dataset indices and metadata for YOLO training

---

## Architecture Overview

```
User Uploads Image
     ↓
[1] YOLO Detection (best.pt)
     ↓
[2] EfficientNet Classification (efficientnet_fish.h5)
     ↓
[3] SavedModel Disease Detection (saved_model/)
     ↓
Response: {species, confidence, disease_status, disease_confidence}
```

### Stage 1: Detection (YOLO)
- Input: Raw image (any size)
- Output: Fish bounding box + confidence
- Model: YOLOv8 Small (best.pt)

### Stage 2: Classification (EfficientNet)
- Input: Cropped fish region (300×300)
- Output: Species + confidence (5 classes)
- Model: EfficientNetB3 (efficientnet_fish.h5)
- Classes: Catla, CommonCarp, Mori, Rohu, SilverCarp

### Stage 3: Disease Detection (SavedModel)
- Input: Cropped fish region (224×224) - **raw pixels [0-255]**
- Output: Health status (HEALTHY/DISEASED) + confidence
- Model: EfficientNetB0 SavedModel
- Threshold: 0.40 (prob ≥ 0.40 = HEALTHY)

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root endpoint (returns welcome message) |
| `/health` | GET | Health check (returns model status) |
| `/predict` | POST | Single image prediction |
| `/predict-batch` | POST | Multiple images prediction |
| `/docs` | GET | Swagger UI documentation |
| `/openapi.json` | GET | OpenAPI schema |

---

## Environment Setup

```
Python 3.13
├── TensorFlow 2.14.0+
├── FastAPI 0.104.1
├── Uvicorn 0.24+
├── Pydantic 2.5.0
├── torch 2.7.1
├── ultralytics 8.4.23
├── opencv-python
├── Pillow
├── protobuf==6.31.1  (IMPORTANT: Must match TensorFlow gencode)
└── ... (see requirements.txt)
```

---

## Data Flow

```
HTTP POST /predict
  ↓
FastAPI receives file (multipart/form-data)
  ↓
ImageProcessor.run_inference()
  ├─ Stage 1: YOLO Detection
  │  ├─ Load image from bytes
  │  ├─ Run YOLO inference
  │  └─ Extract bounding box
  │
  ├─ Stage 2: EfficientNet Classification
  │  ├─ Crop detected region
  │  ├─ Resize to 300×300
  │  ├─ Normalize ([0,1] range)
  │  └─ Get top-5 class probabilities
  │
  └─ Stage 3: SavedModel Disease Detection
     ├─ Crop detected region
     ├─ Resize to 224×224
     ├─ Use raw pixels [0-255]
     ├─ Inference via SavedModel signature
     └─ Apply threshold (0.40) for HEALTHY/DISEASED
  ↓
Pydantic validates response
  ↓
JSON response returned to client
```

---

## Important Notes

1. **SavedModel Image Size**: Must use **224×224**, not 160×160
2. **SavedModel Input**: Expects **raw pixels [0-255]**, not normalized [0-1]
3. **Disease Threshold**: **0.40** (from predict.py reference implementation)
4. **Protobuf Version**: Must be **6.31.1** to match TensorFlow gencode
5. **Preprocessing**: SavedModel has `preprocess_input` as first layer (handles normalization internally)

---

## Quick File Reference

| Need to ... | Look at ... |
|-------------|-------------|
| Start server | `run.py` |
| Add new endpoint | `app/main.py` |
| Fix image processing | `app/utils/image_processor.py` |
| Load/switch models | `app/utils/model_loader.py` |
| Change response format | `app/schemas/models.py` |
| Debug models | `debug_disease_model.py` or `Saved model file/predict.py` |
| Test API | `test_*.py` scripts |
| Install packages | `requirements.txt` |

---

## Generated Files (Auto-created)

- `__pycache__/` - Python bytecode cache
- `runs/` - YOLO training/detection outputs
- `best_pt_folder/data/` - Dataset indices

---

## Version Information

- **Created**: April 9, 2026
- **Python**: 3.13
- **TensorFlow**: 2.14.0+
- **FastAPI**: 0.104.1
- **Project**: Fish Species Detection with Disease Classification
