import logging
from datetime import datetime

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout, LeakyReLU
from tensorflow.keras.optimizers import Adam
from keras.models import load_model

# Best models parameters in compliance with DS Project
# Refer MLP12 (acc=90,05%), MLP9 (acc=89,70%) and MLP11 (acc=89,67%)
from dsdc import CONFIG
INITIAL_BEST_KNWON_PARAMS = {
    "MLP12": {
        "layers": [
            {"units": 512, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.4},
            {"units": 128, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.3},
            {"units": 32, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.2},
        ],
        "learning_rate": 1e-4
    },
    "MLP9": {
        "layers": [
            {"units": 256, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.4},
            {"units": 128, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.2},
            {"units": 128, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.2},
            {"units": 64, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.1},
            {"units": 64, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.1},
        ],
        "learning_rate": 1e-4
    },
    "MLP11": {
        "layers": [
            {"units": 512, "activation": "relu", "dropout": 0.4},
            {"units": 128, "activation": "relu", "dropout": 0.3},
            {"units": 32, "activation": "relu", "dropout": 0.2},
        ],
        "learning_rate": 1e-4
    },
} 

class MLP(Sequential):
    def __init__(self, params: dict):
        super().__init__()
        layers = params.get("layers", [])
        input_dim = 1024                # Fixed (post-CLIP-embeddings)
        output_units = 16               # Fixed (16 categories) 
        output_activation = "softmax"   # Fixed (choice)
        learning_rate = params.get("learning_rate", 1e-4)

        # Première couche
        self.add(Input(shape=(input_dim,)))

        # Construction des couches cachées
        for i, layer_cfg in enumerate(layers):
            units = layer_cfg["units"]
            activation = layer_cfg.get("activation", "relu")
            dropout_rate = layer_cfg.get("dropout", 0.0)
            self.add(Dense(units))

            # Gestion des activations
            if activation == "leaky_relu":
                negative_slope = layer_cfg.get("negative_slope", 0.3)
                self.add(LeakyReLU(negative_slope=negative_slope))
            else:
                self.add(Dense(0, activation=activation))  # Hack: ignore layer, just add activation
                self.pop()  # Remove dummy Dense
                self.add(Dense(units, activation=activation))

            # Dropout optionnel
            if dropout_rate > 0.0:
                self.add(Dropout(dropout_rate))

        # Couche de sortie
        self.add(Dense(output_units, activation=output_activation))

        # Compilation
        optimizer = Adam(learning_rate=learning_rate)
        self.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        # Pour tracking avec MLflow
        self._params = params

    def get_config(self):
        # Keras appelle ça pour sauvegarder la config
        config = super().get_config()
        config.update({
            "params": self._params
        })
        return config

    @classmethod
    def from_config(cls, config):
        params = config.pop("params")
        # Appelle le constructeur avec params
        model = cls(params)
        # Optionnel: charger les autres configs Keras (comme layers)
        # Normalement super().from_config n’est pas compatible avec Sequential
        return model
    
    def save(self, name=""):
        if name == "":
            dense_layers = [l for l in self.layers if getattr(l, "name", "").startswith("dense")]
            layers_text = [str(l.units) for l in dense_layers]
            timestamp = datetime.now().strftime("%y%m%d-%H:%M:%S")
            name = f"MLP_{layers_text}_{timestamp}.keras"
        if not name.endswith(".keras"):
            name += ".keras"
        save_path = CONFIG.paths.models/"mlps"/name
        save_path.parent.mkdir(exist_ok=True, parents=True)
        super().save(str(save_path))
        logging.info(f"Successfully saved model at {str(save_path)}")
    
    @classmethod
    def load(cls, filename):
        path = CONFIG.paths.models/"mlps"/filename
        return load_model(str(path), custom_objects={"MLP": MLP})

# EXEMPLE AVEC MLFLOW
# import mlflow

# params = {
#     "layers": [
#         {"units": 512, "activation": "leaky_relu", "negative_slope": 0.1, "dropout": 0.4},
#         {"units": 128, "activation": "relu", "dropout": 0.3},
#         {"units": 32, "activation": "relu"},
#     ],
#     "learning_rate": 1e-4
# }

# with mlflow.start_run():
#     mlflow.log_params(params)

#     model = MLP(input_dim=1024, params=params)
#     history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50)

#     val_acc = history.history["val_accuracy"][-1]
#     mlflow.log_metric("val_accuracy", val_acc)

#     model.save("path/to/save/model.keras")
#     mlflow.tensorflow.log_model(tf_model=model, artifact_path="model")