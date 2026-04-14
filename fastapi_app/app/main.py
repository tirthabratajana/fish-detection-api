"""
FastAPI application for Fish Species Detection
Three-stage pipeline: YOLOv8s (detection) → EfficientNetB3 (classification) → SavedModel Disease Detection (health)
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.utils.model_loader import ModelLoader
from app.utils.image_processor import ImageProcessor
from app.schemas.models import (
    PredictionResult,
    HealthCheckResponse,
    ErrorResponse,
    ClassProbability
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for models
YOLO_MODEL = None
EFFICIENTNET_MODEL = None
DISEASE_MODEL = None
CLASS_NAMES = None

# Configuration
MODEL_BASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
YOLO_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'best.pt')
EFFICIENTNET_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'best_pt_folder')  # or best.h5
CLASS_MAP_PATH = os.path.join(MODEL_BASE_PATH, 'clf_class_names.json')
DISEASE_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'model', 'Disease_model', 'saved_model')

# Check if using local models or from best_pt_folder
if not os.path.exists(YOLO_MODEL_PATH):
    YOLO_MODEL_PATH = os.path.join(MODEL_BASE_PATH, 'best_pt_folder', 'best.pt')

EFFICIENTNET_H5_PATH = os.path.join(MODEL_BASE_PATH, 'efficientnet_fish.h5')
if not os.path.exists(CLASS_MAP_PATH):
    CLASS_MAP_PATH = os.path.join(MODEL_BASE_PATH, 'best_pt_folder', 'clf_class_names.json')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown event handler
    """
    logger.info("=" * 60)
    logger.info("🚀 Fish Detection API Starting Up")
    logger.info("=" * 60)
    
    try:
        global YOLO_MODEL, EFFICIENTNET_MODEL, DISEASE_MODEL, CLASS_NAMES
        
        logger.info(f"YOLO Model Path: {YOLO_MODEL_PATH}")
        logger.info(f"EfficientNet Model Path: {EFFICIENTNET_H5_PATH}")
        logger.info(f"Disease Model Path: {DISEASE_MODEL_PATH}")
        logger.info(f"Class Map Path: {CLASS_MAP_PATH}")
        
        # Load models
        YOLO_MODEL, EFFICIENTNET_MODEL, DISEASE_MODEL, CLASS_NAMES = ModelLoader.setup_models(
            yolo_model_path=YOLO_MODEL_PATH,
            efficientnet_model_path=EFFICIENTNET_H5_PATH,
            disease_model_path=DISEASE_MODEL_PATH,
            class_map_path=CLASS_MAP_PATH
        )
        logger.info("✅ All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load models: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 Fish Detection API Shutting Down")
    logger.info("=" * 60)


# Create FastAPI app
app = FastAPI(
    title="🐟 Fish Species Detection API",
    description="Three-stage pipeline: YOLOv8s detection → EfficientNetB3 species classification → SavedModel disease detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check() -> HealthCheckResponse:
    """
    Check if API and models are ready
    """
    models_ready = ModelLoader.is_loaded()
    
    return HealthCheckResponse(
        status="✅ Healthy" if models_ready else "❌ Not Ready",
        yolo_model_loaded=YOLO_MODEL is not None,
        efficientnet_model_loaded=EFFICIENTNET_MODEL is not None,
        message="All models loaded and ready" if models_ready else "Models not yet loaded"
    )


# ═══════════════════════════════════════════════════════════════
# PREDICTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post(
    "/predict",
    response_model=PredictionResult,
    tags=["Prediction"],
    summary="Predict fish species from image"
)
async def predict_fish(
    file: UploadFile = File(
        ...,
        description="Image file (JPG, PNG, etc.)"
    )
) -> PredictionResult:
    """
    Upload fish image and get species + disease predictions
    
    **Three-Stage Pipeline:**
    1. **YOLO Detection**: Locates fish in image
    2. **EfficientNet Classification**: Classifies the detected fish species
    3. **Disease Detection(EfficientNetB0)**: Determines if fish is healthy or diseased
    
    **Request:**
    - Content-Type: multipart/form-data
    - file: Image binary data
    
    **Response includes:**
    - species: Predicted fish species (Catla, CommonCarp, Mori, Rohu, SilverCarp)
    - species_confidence: EfficientNet confidence (0-1)
    - disease_status: Health status (HEALTHY or DISEASED)
    - disease_confidence: TFLite disease model confidence (0-1)
    - yolo_confidence: YOLO detection confidence (0-1)
    - all_class_probabilities: Probabilities for all 5 fish species
    
    **Example Species:**
    - Catla
    - CommonCarp
    - Mori
    - Rohu
    - SilverCarp
    """
    
    # Validate models are loaded
    if not ModelLoader.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please try again in a few seconds."
        )
    
    try:
        logger.info(f"📥 Received prediction request for file: {file.filename}")
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file type: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file bytes
        image_bytes = await file.read()
        
        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        logger.info(f"File size: {len(image_bytes) / 1024 / 1024:.2f} MB")
        
        # Run inference (three-stage pipeline: detection → species → disease)
        result_dict = ImageProcessor.run_inference(
            image_bytes=image_bytes,
            yolo_model=YOLO_MODEL,
            efficientnet_model=EFFICIENTNET_MODEL,
            disease_model=DISEASE_MODEL,
            class_names=CLASS_NAMES,
            yolo_conf=0.20
        )
        
        # Convert all_class_probabilities to ClassProbability objects
        class_probs = [
            ClassProbability(
                class_name=prob["class_name"],
                probability=prob["probability"],
                confidence_percent=prob["confidence_percent"]
            )
            for prob in result_dict["all_class_probabilities"]
        ]
        
        # Create response (includes disease status from stage 3)
        response = PredictionResult(
            success=result_dict["success"],
            species=result_dict["species"],
            species_confidence=result_dict["species_confidence"],
            species_confidence_percent=result_dict["species_confidence_percent"],
            disease_status=result_dict.get("disease_status", "UNKNOWN"),
            disease_confidence=result_dict.get("disease_confidence", 0.0),
            disease_confidence_percent=result_dict.get("disease_confidence_percent", "0%"),
            yolo_confidence=result_dict["yolo_confidence"],
            yolo_confidence_percent=result_dict["yolo_confidence_percent"],
            is_valid_detection=result_dict["is_valid_detection"],
            all_class_probabilities=class_probs,
            message=result_dict["message"],
            detection_count=result_dict["detection_count"]
        )
        
        logger.info(f"✅ Prediction complete: {response.species} ({response.species_confidence_percent})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post(
    "/predict-batch",
    tags=["Prediction"],
    summary="Batch prediction (multiple images)"
)
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    Upload multiple fish images and get species + disease predictions for all
    
    **Three-Stage Pipeline (applied to each image):**
    1. YOLO Detection
    2. EfficientNet Species Classification
    3. TFLite Disease Detection
    
    **Limitations:**
    - Max 10 images per request
    - Processing is sequential (one after another)
    
    **Response includes disease status for each image**
    """
    
    if not ModelLoader.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded"
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images per request"
        )
    
    results = []
    
    for file in files:
        try:
            image_bytes = await file.read()
            
            result_dict = ImageProcessor.run_inference(
                image_bytes=image_bytes,
                yolo_model=YOLO_MODEL,
                efficientnet_model=EFFICIENTNET_MODEL,
                disease_model=DISEASE_MODEL,
                class_names=CLASS_NAMES,
                yolo_conf=0.20
            )
            
            class_probs = [
                ClassProbability(
                    class_name=prob["class_name"],
                    probability=prob["probability"],
                    confidence_percent=prob["confidence_percent"]
                )
                for prob in result_dict["all_class_probabilities"]
            ]
            
            results.append({
                "filename": file.filename,
                "prediction": PredictionResult(
                    success=result_dict["success"],
                    species=result_dict["species"],
                    species_confidence=result_dict["species_confidence"],
                    species_confidence_percent=result_dict["species_confidence_percent"],
                    disease_status=result_dict.get("disease_status", "UNKNOWN"),
                    disease_confidence=result_dict.get("disease_confidence", 0.0),
                    disease_confidence_percent=result_dict.get("disease_confidence_percent", "0%"),
                    yolo_confidence=result_dict["yolo_confidence"],
                    yolo_confidence_percent=result_dict["yolo_confidence_percent"],
                    is_valid_detection=result_dict["is_valid_detection"],
                    all_class_probabilities=class_probs,
                    message=result_dict["message"],
                    detection_count=result_dict["detection_count"]
                )
            })
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"batch_size": len(files), "results": results}


# ═══════════════════════════════════════════════════════════════
# ROOT ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.get(
    "/",
    tags=["Info"],
    summary="API information"
)
async def root():
    """
    Root endpoint - returns API information
    """
    return {
        "api_name": "🐟 Fish Species Detection API",
        "version": "1.0.0",
        "description": "Three-stage fish detection pipeline: detection → species classification → disease detection",
        "endpoints": {
            "health": "/health",
            "predict_single": "/predict (POST)",
            "predict_batch": "/predict-batch (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "supported_species": CLASS_NAMES if CLASS_NAMES else ["Loading..."],
        "models": {
            "detection": "YOLOv8s",
            "species_classification": "EfficientNetB3",
            "disease_detection": "EfficientNetB0 (SavedModel)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
