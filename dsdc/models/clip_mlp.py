from dsdc.models.clip import CLIPSingleton
from pathlib import Path
from dsdc.models.mlp import MLP
from dsdc.models.clip import CLIPSingleton

class CLIPBasedMLP:
    def __init__(self, mlp:str|MLP=None):
        self.clip = CLIPSingleton()
        if isinstance(mlp, str):
            self.mlp = MLP.load(mlp)
        elif isinstance(mlp, MLP): 
            self.mlp = mlp
        else:
            msg = f"Unexpected type for mlp: expecting str or MLP, received {type(mlp)}"
            logging.error(msg)
            raise ValueError(msg)
    
    def predict(self, images):
        raise NotImplementedError() # TODO
        # process_image
        # process_text
        # embeddings = ...
        # predict
