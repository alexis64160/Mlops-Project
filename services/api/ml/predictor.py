from PIL.Image import Image
import random

# Liste de classes
_CLASSES = ["letter", "form", "e-mail", "handwritten", "advertisement", "scientific report", "scientific publication", "specification", "file folder", "news article", "budget", "invoice", "presentation", "questionnaire", "resume", "memo"]

def predict(image: Image) -> dict:
    """
    Reçoit une PIL.Image et renvoie un dict JSON.
    ICI: on simule une prédiction (au hasard).

    """
    label = random.choice(_CLASSES)
    confidence = round(random.uniform(0.5, 0.99), 2)
    return {
        "label": label,
        "confidence": confidence,
        "width": image.width,
        "height": image.height,
    }
