"""
Model loader utility for YOLO, EfficientNet (classification), and Disease Detection models
Optimized for memory-constrained environments (Free tier: 512MB RAM)
"""
import os
import json
import logging
from typing import Optional, Tuple
import tensorflow as tf
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton class to load and manage AI models with graceful error handling"""
    
    _instance = None
    _yolo_model: Optional[YOLO] = None
    _efficientnet_model: Optional[tf.keras.Model] = None
    _disease_model: Optional[tf.lite.Interpreter] = None
    _class_names: Optional[list] = None
    _models_loaded: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    def setup_models(
        yolo_model_path: str,
        efficientnet_model_path: str,
        disease_model_path: str,
        class_map_path: str
    ) -> Tuple[YOLO, tf.keras.Model, tf.lite.Interpreter, list]:
        """
        Load YOLO, EfficientNet, and Disease Detection models from disk
        Gracefully handles missing models - won't crash app if a model fails
        
        Args:
            yolo_model_path: Path to best.pt YOLO model
            efficientnet_model_path: Path to efficientnet_fish.h5 model
            disease_model_path: Path to fish.tflite disease model
            class_map_path: Path to clf_class_names.json
            
        Returns:
            Tuple of (yolo_model, efficientnet_model, disease_model, class_names)
        """
        loader = ModelLoader()
        
        try:
            logger.info("=" * 60)
            logger.info("Starting Model Loading Sequence")
            logger.info("=" * 60)
            
            # Load class names FIRST (required)
            if not os.path.exists(class_map_path):
                logger.error(f"Class map not found: {class_map_path}")
                raise FileNotFoundError(f"Class map not found: {class_map_path}")
            
            logger.info(f"Loading class names from {class_map_path}...")
            with open(class_map_path, 'r') as f:
                loader._class_names = json.load(f)
            logger.info(f"✅ Loaded {len(loader._class_names)} species: {loader._class_names}")
            
            # Load YOLO model (graceful - optional)
            if not os.path.exists(yolo_model_path):
                logger.warning(f"⚠️  YOLO model not found: {yolo_model_path}")
                loader._yolo_model = None
            else:
                try:
                    logger.info(f"Loading YOLO model from {yolo_model_path}...")
                    loader._yolo_model = YOLO(yolo_model_path)
                    logger.info("✅ YOLO model loaded successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to load YOLO: {str(e)}")
                    loader._yolo_model = None
            
            # Load EfficientNet model (graceful - optional)
            if not os.path.exists(efficientnet_model_path):
                logger.warning(f"⚠️  EfficientNet model not found: {efficientnet_model_path}")
                loader._efficientnet_model = None
            else:
                try:
                    logger.info(f"Loading EfficientNet model from {efficientnet_model_path}...")
                    loader._efficientnet_model = tf.keras.models.load_model(efficientnet_model_path)
                    logger.info("✅ EfficientNet model loaded successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to load EfficientNet: {str(e)}")
                    loader._efficientnet_model = None
            
            # Load Disease Detection model (TFLite - graceful - optional)
            if not os.path.exists(disease_model_path):
                logger.warning(f"⚠️  Disease model not found: {disease_model_path}")
                loader._disease_model = None
            else:
                try:
                    logger.info(f"Loading Disease Detection model (TFLite) from {disease_model_path}...")
                    loader._disease_model = tf.lite.Interpreter(model_path=disease_model_path)
                    loader._disease_model.allocate_tensors()
                    logger.info("✅ Disease Detection model loaded successfully")
                except Exception as e:
                    logger.error(f"❌ Failed to load disease model: {str(e)}")
                    loader._disease_model = None
            
            logger.info("=" * 60)
            logger.info(f"YOLO: {'✅' if loader._yolo_model else '⚠️'}")
            logger.info(f"EfficientNet: {'✅' if loader._efficientnet_model else '⚠️'}")
            logger.info(f"Disease Model: {'✅' if loader._disease_model else '⚠️'}")
            logger.info(f"Species: ✅ ({len(loader._class_names) if loader._class_names else 0})")
            logger.info("=" * 60)
            
            loader._models_loaded = True
            return loader._yolo_model, loader._efficientnet_model, loader._disease_model, loader._class_names
            
        except Exception as e:
            logger.error(f"Fatal: {str(e)}")
            loader._models_loaded = False
            raise
    
    @staticmethod
    def get_models() -> Tuple[YOLO, tf.keras.Model, tf.lite.Interpreter, list]:
        """Get loaded models"""
        loader = ModelLoader()
        if not loader._models_loaded:
            raise RuntimeError("Models not loaded. Call setup_models() first.")
        return loader._yolo_model, loader._efficientnet_model, loader._disease_model, loader._class_names
    
    @staticmethod
    def is_loaded() -> bool:
        """Check if models are loaded"""
        loader = ModelLoader()
        return loader._models_loaded
