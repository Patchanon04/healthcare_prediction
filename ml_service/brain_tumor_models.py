"""
Brain Tumor Detection Models
Support for multiple model architectures
"""
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import model_from_json, load_model
from pathlib import Path
from typing import Tuple, Dict
import logging
import json

logger = logging.getLogger(__name__)


class BrainTumorModelBase:
    """Base class for brain tumor detection models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_loaded = False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for model input"""
        raise NotImplementedError
    
    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        """
        Predict brain tumor from image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (confidence, metadata)
        """
        raise NotImplementedError
    
    def load_model(self, model_path: Path):
        """Load model from file"""
        raise NotImplementedError


class BrainTumorModel1(BrainTumorModelBase):
    """
    Brain Tumor Detection Model 1
    Architecture: Custom CNN with JSON + H5 weights
    Input: 224x224 RGB image
    Output: Binary classification (tumor/no tumor)
    """
    
    def __init__(self):
        super().__init__("BrainTumorModel1")
        self.input_size = (224, 224)
    
    def load_model(self, model_json_path: Path, model_weights_path: Path):
        """
        Load model from JSON architecture and H5 weights
        
        Args:
            model_json_path: Path to model.json
            model_weights_path: Path to model.h5
        """
        try:
            # Load model architecture
            with open(model_json_path, 'r') as json_file:
                loaded_model_json = json_file.read()
            
            self.model = model_from_json(loaded_model_json)
            
            # Load weights
            self.model.load_weights(str(model_weights_path))
            
            self.is_loaded = True
            logger.info(f"{self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading {self.model_name}: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for Model 1
        
        Args:
            image: Input image (BGR or RGB)
            
        Returns:
            Preprocessed image ready for prediction
        """
        # Resize to 224x224
        if image.shape[:2] != self.input_size:
            image = cv2.resize(image, self.input_size)
        
        # Ensure RGB format (if BGR, convert)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        """
        Predict brain tumor probability
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (tumor_probability, metadata)
        """
        if not self.is_loaded:
            raise RuntimeError(f"{self.model_name} is not loaded")
        
        # Preprocess
        processed_image = self.preprocess_image(image)
        
        # Predict
        prediction = self.model.predict(processed_image, verbose=0)
        
        # Extract tumor probability (assuming binary classification)
        # prediction shape: (1, 2) for [no_tumor, tumor]
        tumor_prob = float(prediction[0, 1])
        
        metadata = {
            "model_name": self.model_name,
            "input_shape": self.input_size,
            "raw_prediction": prediction[0].tolist(),
            "tumor_probability": tumor_prob,
            "no_tumor_probability": float(prediction[0, 0])
        }
        
        return tumor_prob, metadata


class BrainTumorModel2(BrainTumorModelBase):
    """
    Brain Tumor Detection Model 2
    Architecture: CNN with checkpoint-based weights
    Input: 150x150 RGB image (typical for this architecture)
    Output: Binary classification (tumor/no tumor)
    """
    
    def __init__(self):
        super().__init__("BrainTumorModel2")
        self.input_size = (150, 150)  # Common size for this model type
    
    def load_model(self, model_path: Path):
        """
        Load model from checkpoint file (.model or .h5)
        
        Args:
            model_path: Path to model checkpoint
        """
        try:
            self.model = load_model(str(model_path))
            self.is_loaded = True
            logger.info(f"{self.model_name} loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Error loading {self.model_name}: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for Model 2
        
        Args:
            image: Input image (BGR or RGB)
            
        Returns:
            Preprocessed image ready for prediction
        """
        # Resize to 150x150
        if image.shape[:2] != self.input_size:
            image = cv2.resize(image, self.input_size)
        
        # Ensure RGB format
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        """
        Predict brain tumor probability
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (tumor_probability, metadata)
        """
        if not self.is_loaded:
            raise RuntimeError(f"{self.model_name} is not loaded")
        
        # Preprocess
        processed_image = self.preprocess_image(image)
        
        # Predict
        prediction = self.model.predict(processed_image, verbose=0)
        
        # Extract tumor probability
        # Assuming binary classification output
        if prediction.shape[-1] == 1:
            # Single output neuron (sigmoid)
            tumor_prob = float(prediction[0, 0])
        else:
            # Two output neurons (softmax)
            tumor_prob = float(prediction[0, 1])
        
        metadata = {
            "model_name": self.model_name,
            "input_shape": self.input_size,
            "raw_prediction": prediction[0].tolist(),
            "tumor_probability": tumor_prob
        }
        
        return tumor_prob, metadata
