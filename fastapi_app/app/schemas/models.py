"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel
from typing import List, Dict


class ClassProbability(BaseModel):
    """Individual class probability"""
    class_name: str
    probability: float
    confidence_percent: str


class PredictionResult(BaseModel):
    """Complete prediction result from all three stages"""
    success: bool
    species: str
    species_confidence: float
    species_confidence_percent: str
    yolo_confidence: float
    yolo_confidence_percent: str
    is_valid_detection: bool
    all_class_probabilities: List[ClassProbability]
    disease_status: str
    disease_confidence: float
    disease_confidence_percent: str
    message: str
    detection_count: int


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    yolo_model_loaded: bool
    efficientnet_model_loaded: bool
    message: str


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool
    error: str
    details: str = None
