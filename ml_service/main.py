import time
import random
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import httpx

app = FastAPI(title="Medical Diagnosis ML Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock medical conditions database (brain-related conditions example)
MEDICAL_CONDITIONS = [
    "intracranial_hemorrhage",
    "subdural_hematoma",
    "epidural_hematoma",
    "subarachnoid_hemorrhage",
    "intraparenchymal_hemorrhage",
    "ischemic_stroke",
    "brain_tumor_meningioma",
    "brain_tumor_glioma",
    "brain_tumor_pituitary",
    "hydrocephalus",
    "midline_shift",
    "skull_fracture",
    "cerebral_edema",
    "normal"
]

MODEL_VERSION = "v1.0"


class PredictionRequest(BaseModel):
    image_url: HttpUrl


class PredictionResponse(BaseModel):
    diagnosis: str
    confidence: float
    model_version: str
    processing_time: float


class HealthResponse(BaseModel):
    model: str
    version: str


@app.get("/health/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for the ML service.
    """
    return {
        "model": "ready",
        "version": MODEL_VERSION
    }


@app.post("/predict/", response_model=PredictionResponse)
async def predict_diagnosis(request: PredictionRequest):
    """
    Predict brain-related medical condition from an image URL.
    
    In production, this would:
    1. Download the image from the URL
    2. Preprocess the image
    3. Run inference using a trained model (e.g., ResNet, EfficientNet)
    4. Return predictions
    
    For this demo, we simulate the prediction with mock data.
    """
    start_time = time.time()
    
    try:
        # Simulate image download and validation
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.head(str(request.image_url))
                if response.status_code not in [200, 302, 301]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unable to access image URL: {response.status_code}"
                    )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error accessing image URL: {str(e)}"
                )
        
        # Simulate model inference time (100-500ms)
        inference_time = random.uniform(0.1, 0.5)
        time.sleep(inference_time)
        
        # Generate mock prediction
        diagnosis = random.choice(MEDICAL_CONDITIONS)
        confidence = round(random.uniform(0.75, 0.99), 2)
        
        processing_time = round(time.time() - start_time, 2)
        
        return PredictionResponse(
            diagnosis=diagnosis,
            confidence=confidence,
            model_version=MODEL_VERSION,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Medical Diagnosis ML Service",
        "version": MODEL_VERSION,
        "endpoints": [
            "/health/",
            "/predict/",
            "/docs"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
