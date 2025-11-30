"""
Ensemble Predictor for Brain Tumor Detection
Combines predictions from multiple models and selects the best result
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from brain_tumor_models import BrainTumorModelBase

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Ensemble predictor that combines multiple brain tumor detection models
    and selects the best prediction based on confidence
    """
    
    def __init__(self, models: List[BrainTumorModelBase], strategy: str = "max_confidence"):
        """
        Initialize ensemble predictor
        
        Args:
            models: List of loaded brain tumor models
            strategy: Selection strategy ('max_confidence', 'average', 'voting')
        """
        self.models = models
        self.strategy = strategy
        
        if not models:
            raise ValueError("At least one model must be provided")
        
        logger.info(f"EnsemblePredictor initialized with {len(models)} models, strategy: {strategy}")
    
    def predict(self, image: np.ndarray) -> Dict:
        """
        Predict brain tumor using ensemble of models
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary containing:
                - selected_model: Name of the model with best prediction
                - tumor_probability: Probability of tumor (0-1)
                - confidence: Confidence score
                - has_tumor: Boolean prediction
                - all_predictions: List of all model predictions
                - strategy: Strategy used for selection
        """
        if not self.models:
            raise RuntimeError("No models loaded in ensemble")
        
        all_predictions = []
        
        # Get predictions from all models
        for model in self.models:
            try:
                tumor_prob, metadata = model.predict(image)
                
                prediction_info = {
                    "model_name": model.model_name,
                    "tumor_probability": tumor_prob,
                    "confidence": tumor_prob if tumor_prob > 0.5 else (1 - tumor_prob),
                    "predicted_class": metadata.get("predicted_class"),
                    "class_probabilities": metadata.get("class_probabilities"),
                    "metadata": metadata,
                }
                
                all_predictions.append(prediction_info)
                logger.info(f"{model.model_name}: tumor_prob={tumor_prob:.4f}, confidence={prediction_info['confidence']:.4f}")
                
            except Exception as e:
                logger.error(f"Error predicting with {model.model_name}: {e}")
                continue
        
        if not all_predictions:
            raise RuntimeError("All models failed to predict")
        
        ensemble_class_probabilities = self._average_class_probabilities(all_predictions)

        # Select best prediction based on strategy
        if self.strategy == "max_confidence":
            best_prediction = self._select_max_confidence(all_predictions)
        elif self.strategy == "average":
            best_prediction = self._select_average(all_predictions)
        elif self.strategy == "voting":
            best_prediction = self._select_voting(all_predictions)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Add all predictions to result
        best_prediction["all_predictions"] = all_predictions
        best_prediction["strategy"] = self.strategy
        best_prediction["num_models"] = len(all_predictions)

        if ensemble_class_probabilities:
            binary_labels = {"tumor", "no_tumor", "no-tumor", "no tumor", "positive", "negative"}
            detailed_probs = {
                class_name: prob
                for class_name, prob in ensemble_class_probabilities.items()
                if class_name.lower() not in binary_labels
            }

            if detailed_probs:
                predicted_class = max(detailed_probs, key=detailed_probs.get)
            else:
                predicted_class = max(
                    ensemble_class_probabilities, key=ensemble_class_probabilities.get
                )

            best_prediction["class_probabilities"] = ensemble_class_probabilities
            best_prediction["predicted_class"] = predicted_class
            best_prediction["diagnosis"] = self._format_diagnosis(
                predicted_class, best_prediction.get("has_tumor", False)
            )

        return best_prediction

    def _format_diagnosis(self, predicted_class: Optional[str], has_tumor: bool) -> str:
        """Generate human-readable diagnosis string from predicted class."""
        if predicted_class:
            normalized = predicted_class.replace('_', ' ').replace('-', ' ').strip()
            normalized_lower = normalized.lower()

            if normalized_lower in {"tumor", "positive"}:
                return "Tumor Detected"

            if normalized_lower in {"no tumor", "no", "none", "notumor", "negative"}:
                return "No Tumor"

            return normalized.title()

        return "Tumor Detected" if has_tumor else "No Tumor"

    def _select_max_confidence(self, predictions: List[Dict]) -> Dict:
        """
        Select prediction with maximum confidence
        
        Args:
            
        Returns:
            Best prediction dictionary
        """
        # Find prediction with highest confidence
        best_pred = max(predictions, key=lambda x: x["confidence"])
        
        tumor_prob = best_pred["tumor_probability"]
        has_tumor = tumor_prob > 0.5
        
        diagnosis = self._format_diagnosis(best_pred.get("predicted_class"), has_tumor)

        return {
            "selected_model": best_pred["model_name"],
            "tumor_probability": tumor_prob,
            "confidence": best_pred["confidence"],
            "has_tumor": has_tumor,
            "diagnosis": diagnosis,
            "predicted_class": best_pred.get("predicted_class"),
            "class_probabilities": best_pred.get("class_probabilities"),
            "selection_reason": f"Highest confidence: {best_pred['confidence']:.4f}"
        }
    
    def _select_average(self, predictions: List[Dict]) -> Dict:
        """
        Average predictions from all models
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Averaged prediction dictionary
        """
        # Calculate average tumor probability
        avg_tumor_prob = np.mean([p["tumor_probability"] for p in predictions])
        avg_confidence = np.mean([p["confidence"] for p in predictions])
        has_tumor = avg_tumor_prob > 0.5

        model_names = [p["model_name"] for p in predictions]

        averaged_class_probabilities = self._average_class_probabilities(predictions)
        predicted_class = None
        if averaged_class_probabilities:
            predicted_class = max(averaged_class_probabilities, key=averaged_class_probabilities.get)
        else:
            predicted_class = "tumor" if has_tumor else "no_tumor"

        diagnosis = self._format_diagnosis(predicted_class, has_tumor)

        return {
            "selected_model": f"Ensemble({', '.join(model_names)})",
            "tumor_probability": float(avg_tumor_prob),
            "confidence": float(avg_confidence),
            "has_tumor": has_tumor,
            "diagnosis": diagnosis,
            "predicted_class": predicted_class,
            "class_probabilities": averaged_class_probabilities,
            "selection_reason": f"Average of {len(predictions)} models"
        }
    
    def _select_voting(self, predictions: List[Dict]) -> Dict:
        """
        Majority voting from all models
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Voted prediction dictionary
        """
        # Count votes for tumor/no tumor
        tumor_votes = sum(1 for p in predictions if p["tumor_probability"] > 0.5)
        total_votes = len(predictions)

        has_tumor = tumor_votes > (total_votes / 2)

        # Use average probability from models that voted for the winning class
        if has_tumor:
            relevant_probs = [
                p["tumor_probability"] for p in predictions if p["tumor_probability"] > 0.5
            ]
        else:
            relevant_probs = [
                p["tumor_probability"] for p in predictions if p["tumor_probability"] <= 0.5
            ]

        avg_prob = np.mean(relevant_probs) if relevant_probs else 0.5
        confidence = abs(tumor_votes - (total_votes - tumor_votes)) / total_votes

        averaged_class_probabilities = self._average_class_probabilities(predictions)
        predicted_class = None
        if averaged_class_probabilities:
            predicted_class = max(
                averaged_class_probabilities, key=averaged_class_probabilities.get
            )
        else:
            predicted_class = "tumor" if has_tumor else "no_tumor"

        diagnosis = self._format_diagnosis(predicted_class, has_tumor)

        return {
            "selected_model": f"Voting({tumor_votes}/{total_votes})",
            "tumor_probability": float(avg_prob),
            "confidence": float(confidence),
            "has_tumor": has_tumor,
            "diagnosis": diagnosis,
            "predicted_class": predicted_class,
            "class_probabilities": averaged_class_probabilities,
            "selection_reason": f"Majority vote: {tumor_votes}/{total_votes} for tumor"
        }

    def _average_class_probabilities(self, predictions: List[Dict]) -> Dict:
        """Average class probabilities across predictions when available."""
        class_prob_dicts = [p.get("class_probabilities") for p in predictions if p.get("class_probabilities")]
        if not class_prob_dicts:
            return {}

        combined: Dict[str, float] = {}
        for prob_dict in class_prob_dicts:
            for class_name, prob in prob_dict.items():
                combined[class_name] = combined.get(class_name, 0.0) + prob

        num_dicts = len(class_prob_dicts)
        return {class_name: total / num_dicts for class_name, total in combined.items()}
    
    def get_model_info(self) -> List[Dict]:
        """
        Get information about all models in ensemble
        
{{ ... }}
            List of model information dictionaries
        """
        return [
            {
                "model_name": model.model_name,
                "is_loaded": model.is_loaded,
                "input_size": getattr(model, 'input_size', None)
            }
            for model in self.models
        ]
