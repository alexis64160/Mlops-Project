import json
import torch
import logging
import numpy as np
import pandas as pd

from PIL import Image
from typing import List
from pathlib import Path
from transformers import CLIPProcessor, CLIPModel


from dsdc import CONFIG
config_file = CONFIG.paths.clip_model / "config.json"
with open(config_file, 'r') as f:
    config = json.load(f)
CLIP_VERSION = config.get("name_or_path", "unknown")


class CLIPSingleton:
    """A CLIP model, dealt as a singleton to limit memory impact"""
    _instance = None

    # Singleton class to save memory (CLIP + embeddings pre-computing)
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CLIPSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name="openai/clip-vit-base-patch32", device=None):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        model_path = CONFIG.paths.clip_model
        try:
            self.processor = CLIPProcessor.from_pretrained(model_path, use_fast=False)
            self.model = CLIPModel.from_pretrained(model_path).to(self.device)
            self.model.eval()
            logging.info("Successfully loaded CLIP")
        except OSError as e:
            logging.warning("CLIP not found locally - downloading it from internet")
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model = CLIPModel.from_pretrained(model_name)
            # Sauvegarde pour la prochaine fois
            model_path.mkdir(parents=True, exist_ok=True)
            self.model.save_pretrained(model_path)
            self.processor.save_pretrained(model_path)                
            logging.info(f"Saving CLIP parameters for next time ({str(model_path)})")
        self.version = CLIP_VERSION if CLIP_VERSION != "unknown" else self.model.name_or_path

    def get_embeddings(self, image_paths:List[str|Path], texts:List[str]):
        """Return clip embeddings
        """
        images = [Image.open(x).convert("RGB") for x in image_paths]
        clip_processed = self.processor(
                    text=texts,
                    images=images,
                    return_tensors="pt", padding=True,
                    truncation=True,  # tronque automatiquement à la taille max supportée
                )
        clip_processed = {k: v.to(self.device) for k, v in clip_processed.items()}
        with torch.no_grad():
            outputs = self.model(**clip_processed)
            image_emb = outputs.image_embeds.cpu().numpy()
            text_emb = outputs.text_embeds.cpu().numpy()
        embeddings = np.concatenate((image_emb, text_emb), axis=1).astype(float).tolist()
        return embeddings