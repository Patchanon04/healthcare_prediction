import time
import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from parent directory's .env file
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger_temp = logging.getLogger(__name__)
    logger_temp.info(f"Loaded .env from: {env_path}")
else:
    # Fallback to local .env if exists
    load_dotenv()

# Import custom modules
from s3_model_loader import S3ModelLoader
from brain_tumor_models import BrainTumorModel1, BrainTumorModel2
from ensemble_predictor import EnsemblePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Brain Tumor Detection ML Service", version="2.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MODEL_VERSION = "v2.0"
S3_BUCKET = os.getenv("AWS_STORAGE_BUCKET_NAME", "your-bucket-name")
AWS_REGION = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

# Model paths in S3
MODEL1_PRIMARY_KEY = os.getenv(
    "MODEL1_PRIMARY_KEY",
    "models/brain_tumor/model1/img_clf.keras",
)
MODEL1_FALLBACK_KEY = os.getenv(
    "MODEL1_FALLBACK_KEY",
    "models/brain_tumor/model1/img_clf.h5",
)
MODEL2_KEY = os.getenv(
    "MODEL2_KEY",
    "models/brain_tumor/model2/best_model_test6.pth",
)

# Global variables for models
s3_loader = None
ensemble_predictor = None


class PredictionRequest(BaseModel):
    image_url: Optional[HttpUrl] = None


class BrainTumorPredictionResponse(BaseModel):
    diagnosis: str
    has_tumor: bool
    tumor_probability: float
    confidence: float
    selected_model: str
    model_version: str
    processing_time: float
    all_predictions: list
    strategy: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: int
    version: str
    models_info: list


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global s3_loader, ensemble_predictor
    
    logger.info("Starting Brain Tumor Detection ML Service...")
    
    try:
        # Initialize S3 loader
        s3_loader = S3ModelLoader(
            bucket_name=S3_BUCKET,
            region_name=AWS_REGION
        )
        logger.info("S3 Model Loader initialized")
        
        # Download and load Model 1
        logger.info("Loading Brain Tumor Model 1...")
        model1 = BrainTumorModel1()
        
        model1_primary_path = s3_loader.download_model(MODEL1_PRIMARY_KEY)

        model1_fallback_path = None
        if MODEL1_FALLBACK_KEY:
            try:
                model1_fallback_path = s3_loader.download_model(MODEL1_FALLBACK_KEY)
            except Exception as fallback_error:
                logger.warning(
                    "Fallback model download failed (%s): %s",
                    MODEL1_FALLBACK_KEY,
                    fallback_error,
                )

        model1.load_model(model1_primary_path, model1_fallback_path)
        
        # Download and load Model 2
        logger.info("Loading Brain Tumor Model 2...")
        model2 = BrainTumorModel2()
        
        model2_path = s3_loader.download_model(MODEL2_KEY)
        model2.load_model(model2_path)
        
        # Create ensemble predictor
        ensemble_predictor = EnsemblePredictor(
            models=[model1, model2],
            strategy="max_confidence"  # Can be changed to "average" or "voting"
        )
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        logger.warning("Service will start but predictions may fail")


@app.get("/health/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for the ML service.
    """
    global ensemble_predictor
    
    if ensemble_predictor is None:
        return {
            "status": "models_not_loaded",
            "models_loaded": 0,
            "version": MODEL_VERSION,
            "models_info": []
        }
    
    models_info = ensemble_predictor.get_model_info()
    
    return {
        "status": "ready",
        "models_loaded": len(models_info),
        "version": MODEL_VERSION,
        "models_info": models_info
    }


@app.post("/predict/brain-tumor/", response_model=BrainTumorPredictionResponse)
async def predict_brain_tumor(file: UploadFile = File(...)):
    """
    Predict brain tumor from uploaded image using ensemble of models.
    
    The service will:
    1. Load the uploaded image
    2. Run predictions using both models
    3. Select the best prediction based on confidence
    4. Return comprehensive results
    
    Args:
        file: Uploaded image file (JPEG, PNG, etc.)
        
    Returns:
        Prediction results with diagnosis, confidence, and model information
    """
    start_time = time.time()
    
    if ensemble_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please check service health."
        )
    
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )
        
        # Run ensemble prediction
        result = ensemble_predictor.predict(image)
        
        processing_time = round(time.time() - start_time, 2)
        
        return BrainTumorPredictionResponse(
            diagnosis=result["diagnosis"],
            has_tumor=result["has_tumor"],
            tumor_probability=result["tumor_probability"],
            confidence=result["confidence"],
            selected_model=result["selected_model"],
            model_version=MODEL_VERSION,
            processing_time=processing_time,
            all_predictions=result["all_predictions"],
            strategy=result["strategy"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict/brain-tumor-url/", response_model=BrainTumorPredictionResponse)
async def predict_brain_tumor_url(request: PredictionRequest):
    """
    Predict brain tumor from image URL using ensemble of models.
    
    Args:
        request: Request containing image_url
        
    Returns:
        Prediction results with diagnosis, confidence, and model information
    """
    start_time = time.time()
    
    if ensemble_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please check service health."
        )
    
    if not request.image_url:
        raise HTTPException(
            status_code=400,
            detail="image_url is required"
        )
    
    try:
        # Download image from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.image_url))
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to download image: HTTP {response.status_code}"
                )
            
            # Convert to numpy array
            image_bytes = BytesIO(response.content)
            pil_image = Image.open(image_bytes)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Run ensemble prediction
        result = ensemble_predictor.predict(image)
        
        processing_time = round(time.time() - start_time, 2)
        
        return BrainTumorPredictionResponse(
            diagnosis=result["diagnosis"],
            has_tumor=result["has_tumor"],
            tumor_probability=result["tumor_probability"],
            confidence=result["confidence"],
            selected_model=result["selected_model"],
            model_version=MODEL_VERSION,
            processing_time=processing_time,
            all_predictions=result["all_predictions"],
            strategy=result["strategy"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict/")
async def predict_legacy(request: PredictionRequest):
    """
    Legacy prediction endpoint for backward compatibility with backend.
    
    This endpoint maintains the same interface as the old ML service
    but uses the new brain tumor ensemble prediction internally.
    
    Args:
        request: Request containing image_url
        
    Returns:
        Simplified prediction response matching old format
    """
    if not request.image_url:
        raise HTTPException(
            status_code=400,
            detail="image_url is required"
        )
    
    # Call the new brain tumor prediction endpoint
    try:
        full_result = await predict_brain_tumor_url(request)
        
        # Convert to legacy format
        return {
            "diagnosis": full_result.diagnosis,
            "confidence": full_result.confidence,
            "model_version": full_result.model_version,
            "processing_time": full_result.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Legacy prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Brain Tumor Detection ML Service",
        "version": MODEL_VERSION,
        "description": "Ensemble prediction using multiple brain tumor detection models",
        "endpoints": [
            "/health/",
            "/predict/",  # Legacy endpoint for backward compatibility
            "/predict/brain-tumor/",
            "/predict/brain-tumor-url/",
            "/docs"
        ],
        "features": [
            "Multi-model ensemble prediction",
            "Automatic model selection based on confidence",
            "S3-based model storage",
            "Support for both file upload and URL-based prediction",
            "Backward compatible with existing backend"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
