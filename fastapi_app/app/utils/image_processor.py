"""
Image processing and inference utility
"""
import io
import logging
import numpy as np
import tensorflow as tf
from PIL import Image
from typing import Tuple, List, Dict
from ultralytics import YOLO
import torch

logger = logging.getLogger(__name__)

# Auto-detect device availability
def get_device() -> str:
    """Auto-detect available device (GPU or CPU)"""
    if torch.cuda.is_available():
        return 0  # GPU available
    return 'cpu'  # Fallback to CPU


class ImageProcessor:
    """Handles image processing and two-stage inference"""
    
    IMG_SIZE_CLF = 300  # EfficientNetB3 input size
    PADDING = 0.05      # 5% padding around bounding box
    DEVICE = get_device()  # Auto-detect device
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """
        Load image from bytes
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            numpy array of image in RGB format
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            return np.array(image)
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            raise ValueError(f"Failed to load image: {str(e)}")
    
    @staticmethod
    def stage_1_yolo_detection(
        image_array: np.ndarray,
        yolo_model: YOLO,
        conf_threshold: float = 0.20
    ) -> Tuple[bool, Dict]:
        """
        Stage 1: Run YOLO detection on image
        
        Args:
            image_array: Input image as numpy array
            yolo_model: Loaded YOLO model
            conf_threshold: Confidence threshold for detection
            
        Returns:
            Tuple of (success, detection_dict)
            detection_dict contains: boxes, confidences, image_shape
        """
        try:
            logger.info("Running YOLO detection...")
            
            # Convert numpy array back to image for YOLO
            image_pil = Image.fromarray(image_array)
            
            # Run YOLO prediction
            predictions = yolo_model.predict(
                source=image_pil,
                conf=conf_threshold,
                device=ImageProcessor.DEVICE,
                verbose=False
            )
            
            if len(predictions[0].boxes) == 0:
                logger.warning("No fish detected by YOLO")
                return False, {
                    "detection_count": 0,
                    "message": "No fish detected in image"
                }
            
            # Get best detection (highest confidence)
            boxes = predictions[0].boxes
            best_idx = boxes.conf.argmax().item()
            
            x1, y1, x2, y2 = boxes.xyxy[best_idx].cpu().numpy().astype(int)
            yolo_conf = float(boxes.conf[best_idx].item())
            
            H, W = image_array.shape[:2]
            
            logger.info(f"YOLO detected fish with confidence: {yolo_conf:.4f}")
            logger.info(f"Bounding box: ({x1}, {y1}) to ({x2}, {y2})")
            
            return True, {
                "detection_count": len(boxes),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "yolo_confidence": yolo_conf,
                "image_shape": (H, W)
            }
            
        except Exception as e:
            logger.error(f"YOLO detection error: {str(e)}")
            return False, {"message": f"YOLO detection failed: {str(e)}"}
    
    @staticmethod
    def stage_2_efficientnet_classification(
        image_array: np.ndarray,
        detection_info: Dict,
        efficientnet_model: tf.keras.Model,
        class_names: List[str]
    ) -> Tuple[str, float, List[Dict]]:
        """
        Stage 2: Classify cropped fish region with EfficientNet
        
        Args:
            image_array: Original image as numpy array
            detection_info: YOLO detection info from stage 1
            efficientnet_model: Loaded EfficientNet model
            class_names: List of class names
            
        Returns:
            Tuple of (predicted_species, confidence, all_probabilities)
        """
        try:
            logger.info("Running EfficientNet classification...")
            
            # Extract bounding box coordinates
            x1 = detection_info["x1"]
            y1 = detection_info["y1"]
            x2 = detection_info["x2"]
            y2 = detection_info["y2"]
            H, W = detection_info["image_shape"]
            
            # Add padding to crop
            pad_x = int(ImageProcessor.PADDING * W)
            pad_y = int(ImageProcessor.PADDING * H)
            
            px1 = max(0, x1 - pad_x)
            py1 = max(0, y1 - pad_y)
            px2 = min(W, x2 + pad_x)
            py2 = min(H, y2 + pad_y)
            
            # Crop the fish region
            crop = image_array[py1:py2, px1:px2]
            logger.info(f"Cropped region shape: {crop.shape}")
            
            # Prepare for EfficientNet
            crop_pil = Image.fromarray(crop).resize(
                (ImageProcessor.IMG_SIZE_CLF, ImageProcessor.IMG_SIZE_CLF)
            )
            crop_arr = np.array(crop_pil, dtype=np.float32)
            
            # Preprocess using EfficientNet preprocessing
            crop_arr = tf.keras.applications.efficientnet.preprocess_input(crop_arr)
            crop_arr = np.expand_dims(crop_arr, 0)
            
            # Get predictions
            clf_probs = efficientnet_model.predict(crop_arr, verbose=0)[0]
            top_idx = int(np.argmax(clf_probs))
            species = class_names[top_idx]
            species_conf = float(clf_probs[top_idx])
            
            logger.info(f"Predicted species: {species} (confidence: {species_conf:.4f})")
            
            # Build all class probabilities
            all_probs = [
                {
                    "class_name": class_names[i],
                    "probability": float(clf_probs[i]),
                    "confidence_percent": f"{clf_probs[i] * 100:.2f}%"
                }
                for i in np.argsort(clf_probs)[::-1]  # Sorted by confidence
            ]
            
            return species, species_conf, all_probs
            
        except Exception as e:
            logger.error(f"EfficientNet classification error: {str(e)}")
            raise
    
    @staticmethod
    def stage_3_disease_detection(
        image_array: np.ndarray,
        detection_info: Dict,
        disease_model,
        threshold: float = 0.40
    ) -> Tuple[str, float]:
        """
        Stage 3: Detect fish disease using SavedModel
        
        Args:
            image_array: Original image as numpy array
            detection_info: YOLO detection info from stage 1
            disease_model: Loaded SavedModel disease detection model (or None)
            threshold: Classification threshold (>=threshold = healthy)
            
        Returns:
            Tuple of (disease_status, confidence)
        """
        try:
            if disease_model is None:
                logger.warning("Disease model not loaded - returning UNKNOWN status")
                return "UNKNOWN", 0.0
            
            logger.info("Running Disease Detection (SavedModel)...")
            
            # Extract bounding box coordinates
            x1 = detection_info["x1"]
            y1 = detection_info["y1"]
            x2 = detection_info["x2"]
            y2 = detection_info["y2"]
            H, W = detection_info["image_shape"]
            
            # Add padding to crop
            pad_x = int(ImageProcessor.PADDING * W)
            pad_y = int(ImageProcessor.PADDING * H)
            
            px1 = max(0, x1 - pad_x)
            py1 = max(0, y1 - pad_y)
            px2 = min(W, x2 + pad_x)
            py2 = min(H, y2 + pad_y)
            
            # Crop the fish region
            crop = image_array[py1:py2, px1:px2]
            
            # Resize to 224x224 (disease model input size from predict.py)
            crop_pil = Image.fromarray(crop).resize((224, 224))
            crop_arr = np.array(crop_pil, dtype=np.float32)
            
            # IMPORTANT: DO NOT normalize outside!
            # The SavedModel has preprocess_input as FIRST LAYER
            # It expects raw pixel values [0-255] and converts to [-1, 1] internally
            # This was causing AUC=0.50 when normalized outside
            crop_batch = np.expand_dims(crop_arr, 0)
            
            logger.info(f"Disease detection input range: [{crop_batch.min():.1f}, {crop_batch.max():.1f}] (raw pixels)")
            
            # Run inference using SavedModel
            # Use the serving_default signature and handle dictionary output
            concrete_func = disease_model.signatures['serving_default']
            result = concrete_func(tf.constant(crop_batch))
            
            # Extract the output from the dictionary
            # Output format is {'output_0': [[value]]}
            disease_prob = float(result['output_0'][0][0].numpy())
            
            logger.info(f"Raw disease probability: {disease_prob:.4f}")
            
            # Determine health status (>= threshold = healthy)
            # Confidence calculation matches predict.py:
            # confidence = prob if healthy else (1.0 - prob)
            if disease_prob >= threshold:
                status = "HEALTHY"
                confidence = disease_prob
            else:
                status = "DISEASED"
                confidence = 1.0 - disease_prob
            
            logger.info(f"Disease detection: {status} (confidence: {confidence:.4f})")
            return status, confidence
            
        except Exception as e:
            logger.error(f"Disease detection error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return "UNKNOWN", 0.0
    
    @staticmethod
    def run_inference(
        image_bytes: bytes,
        yolo_model: YOLO,
        efficientnet_model: tf.keras.Model,
        disease_model: tf.lite.Interpreter,
        class_names: List[str],
        yolo_conf: float = 0.20,
        disease_threshold: float = 0.40
    ) -> Dict:
        """
        Run complete three-stage inference pipeline
        
        Args:
            image_bytes: Image data as bytes
            yolo_model: Loaded YOLO model
            efficientnet_model: Loaded EfficientNet model
            class_names: List of class names
            yolo_conf: YOLO confidence threshold
            
        Returns:
            Dictionary with complete prediction results
        """
        try:
            logger.info("Starting three-stage inference pipeline...")
            
            # Load image
            image_array = ImageProcessor.load_image_from_bytes(image_bytes)
            logger.info(f"Image loaded, shape: {image_array.shape}")
            
            # Stage 1: YOLO Detection
            detection_success, detection_info = ImageProcessor.stage_1_yolo_detection(
                image_array, yolo_model, yolo_conf
            )
            
            if not detection_success:
                return {
                    "success": False,
                    "species": "Unknown",
                    "species_confidence": 0.0,
                    "species_confidence_percent": "0.00%",
                    "yolo_confidence": 0.0,
                    "yolo_confidence_percent": "0.00%",
                    "is_valid_detection": False,
                    "all_class_probabilities": [],
                    "disease_status": "UNKNOWN",
                    "disease_confidence": 0.0,
                    "disease_confidence_percent": "0.00%",
                    "message": detection_info.get("message", "Detection failed"),
                    "detection_count": detection_info.get("detection_count", 0)
                }
            
            # Stage 2: EfficientNet Classification
            species, species_conf, all_probs = ImageProcessor.stage_2_efficientnet_classification(
                image_array, detection_info, efficientnet_model, class_names
            )
            
            # Stage 3: Disease Detection
            disease_status, disease_conf = ImageProcessor.stage_3_disease_detection(
                image_array, detection_info, disease_model, disease_threshold
            )
            
            yolo_conf_val = detection_info.get("yolo_confidence", 0.0)
            
            logger.info("✅ Three-stage inference complete!")
            
            return {
                "success": True,
                "species": species,
                "species_confidence": species_conf,
                "species_confidence_percent": f"{species_conf * 100:.2f}%",
                "yolo_confidence": yolo_conf_val,
                "yolo_confidence_percent": f"{yolo_conf_val * 100:.2f}%",
                "is_valid_detection": True,
                "all_class_probabilities": all_probs,
                "disease_status": disease_status,
                "disease_confidence": disease_conf,
                "disease_confidence_percent": f"{disease_conf * 100:.2f}%",
                "message": f"Species: {species} | Health: {disease_status}",
                "detection_count": detection_info.get("detection_count", 1)
            }
            
        except Exception as e:
            logger.error(f"Inference pipeline error: {str(e)}")
            return {
                "success": False,
                "species": "Unknown",
                "species_confidence": 0.0,
                "species_confidence_percent": "0.00%",
                "yolo_confidence": 0.0,
                "yolo_confidence_percent": "0.00%",
                "is_valid_detection": False,
                "all_class_probabilities": [],
                "disease_status": "UNKNOWN",
                "disease_confidence": 0.0,
                "disease_confidence_percent": "0.00%",
                "message": f"Inference failed: {str(e)}",
                "detection_count": 0
            }
