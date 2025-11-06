"""
Brain Tumor Detection Models supporting TensorFlow/Keras and PyTorch formats.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch
import torch.nn as nn
from tensorflow.keras.models import load_model
from torchvision import models

logger = logging.getLogger(__name__)


class BrainTumorModelBase:
    """Base class for brain tumor detection models."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = None
        self.is_loaded = False

    def preprocess_image(self, image: np.ndarray) -> Union[np.ndarray, torch.Tensor]:
        raise NotImplementedError

    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        raise NotImplementedError

    def load_model(self, *args, **kwargs) -> None:  # pragma: no cover - interface definition
        raise NotImplementedError


class BrainTumorModel1(BrainTumorModelBase):
    """TensorFlow/Keras model loader (.keras primary with .h5 fallback)."""

    def __init__(self) -> None:
        super().__init__("BrainTumorModel1")
        self.input_size = (224, 224)

    def load_model(
        self,
        model_primary_path: Optional[Path],
        model_fallback_path: Optional[Path] = None,
    ) -> None:
        primary_exists = model_primary_path is not None and model_primary_path.exists()
        fallback_exists = model_fallback_path is not None and model_fallback_path.exists()

        if primary_exists:
            self.model = load_model(str(model_primary_path))
            logger.info("%s loaded from %s", self.model_name, model_primary_path)
        elif fallback_exists:
            self.model = load_model(str(model_fallback_path))
            logger.info("%s loaded from fallback %s", self.model_name, model_fallback_path)
        else:
            raise FileNotFoundError(
                "Neither primary model (%s) nor fallback (%s) found" %
                (model_primary_path, model_fallback_path)
            )

        self.is_loaded = True

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        if image.shape[:2] != self.input_size:
            image = cv2.resize(image, self.input_size)

        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = image.astype(np.float32) / 255.0
        image = np.expand_dims(image, axis=0)

        return image

    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        if not self.is_loaded:
            raise RuntimeError(f"{self.model_name} is not loaded")

        processed_image = self.preprocess_image(image)
        prediction = self.model.predict(processed_image, verbose=0)

        tumor_prob = float(prediction[0, 1])
        metadata = {
            "model_name": self.model_name,
            "input_shape": self.input_size,
            "raw_prediction": prediction[0].tolist(),
            "tumor_probability": tumor_prob,
            "no_tumor_probability": float(prediction[0, 0]),
        }

        return tumor_prob, metadata


class BrainTumorModel2(BrainTumorModelBase):
    """PyTorch ResNet18 model loader for `.pth` state_dict checkpoints."""

    def __init__(self, class_names: Optional[List[str]] = None) -> None:
        super().__init__("BrainTumorModel2")
        self.input_size = (224, 224)
        self.class_names = class_names or ["glioma", "meningioma", "notumor", "pituitary"]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model(len(self.class_names)).to(self.device)
        self.no_tumor_index = self._resolve_no_tumor_index()

    def _build_model(self, num_classes: int) -> nn.Module:
        model = models.resnet18(weights=None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(in_features, num_classes),
        )
        return model

    def _resolve_no_tumor_index(self) -> int:
        possible_names = {"notumor", "no_tumor", "no-tumor", "no", "none"}
        for idx, name in enumerate(self.class_names):
            if name.lower() in possible_names:
                return idx

        logger.warning(
            "No explicit 'no tumor' class found in class names %s. Using last class as non-tumor.",
            self.class_names,
        )
        return len(self.class_names) - 1

    def load_model(self, model_path: Path) -> None:
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.is_loaded = True
        logger.info("%s loaded from %s", self.model_name, model_path)

    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        if image.shape[:2] != self.input_size:
            image = cv2.resize(image, self.input_size)

        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = image.astype(np.float32) / 255.0
        tensor = torch.from_numpy(image).permute(2, 0, 1)

        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

        tensor = (tensor - mean) / std
        tensor = tensor.unsqueeze(0)

        return tensor

    def predict(self, image: np.ndarray) -> Tuple[float, Dict]:
        if not self.is_loaded:
            raise RuntimeError(f"{self.model_name} is not loaded")

        processed_tensor = self.preprocess_image(image).to(self.device)

        with torch.no_grad():
            logits = self.model(processed_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

        class_probabilities = {
            class_name: float(probs[idx])
            for idx, class_name in enumerate(self.class_names)
        }

        no_tumor_prob = probs[self.no_tumor_index]
        tumor_prob = float(1.0 - no_tumor_prob)
        predicted_index = int(np.argmax(probs))
        predicted_class = self.class_names[predicted_index]

        metadata = {
            "model_name": self.model_name,
            "input_shape": self.input_size,
            "class_probabilities": class_probabilities,
            "predicted_class": predicted_class,
            "no_tumor_probability": float(no_tumor_prob),
            "tumor_probability": tumor_prob,
        }

        return tumor_prob, metadata
