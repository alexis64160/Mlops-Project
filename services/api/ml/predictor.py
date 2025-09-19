from PIL.Image import Image
from pathlib import Path
from dsdc.models.mlp import MLP
from dsdc.models.clip_mlp import CLIPBasedMLP  # <-- ton fichier qui contient la classe

# Charge le modèle MLP (mets le vrai chemin de ton fichier entraîné .pkl/.joblib)
MLP_PATH = Path("artifacts/mlp.pkl")  

clip_mlp = CLIPBasedMLP(str(MLP_PATH))

def predict(image: Image) -> dict:
    """
    Prend une PIL.Image, renvoie le résultat du modèle CLIP + MLP.
    """
    results = clip_mlp.predict([image])   # on passe une liste (même si 1 image)
    return results[0]