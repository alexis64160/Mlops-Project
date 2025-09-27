import math
import random
import json

# Best models parameters in compliance with DS Project
# Refer MLP12 (acc=90,05%), MLP9 (acc=89,70%) and MLP11 (acc=89,67%)
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

import random

def get_random_params(
        amount=1,
        min_layers=2,
        max_layers=5,
        min_units_per_layer=16,
        max_units_per_layer=1024,
        min_total_units=512,
        max_total_units=2048,
        dropout_frequency=0.7,
        min_dropout=0.0,
        max_dropout=0.5,
        activation_functions={"relu": {}, "leaky_relu": {"min_lr": 1e-5, "max_lr": 1e-3}},
):
    params = dict()
    min_power = math.ceil(math.log2(min_units_per_layer))
    max_power = math.floor(math.log2(max_units_per_layer))
    allowed_units = [2 ** i for i in range(min_power, max_power + 1)]

    for count in range(1, amount + 1):
        num_layers = random.randint(min_layers, max_layers)

        # Générer la configuration en boucle tant que la somme est dans les bornes
        while True:
            layer_units = [random.choice(allowed_units) for _ in range(num_layers)]
            total_units = sum(layer_units)
            if min_total_units <= total_units <= max_total_units:
                break

        layers = []
        for units in layer_units:
            layer = {"units": units}
            activation = random.choice(list(activation_functions.keys()))
            layer["activation"] = activation
            if activation == "leaky_relu":
                layer["negative_slope"] = round(random.uniform(0.01, 0.3), 2)
            if random.random() < dropout_frequency:
                layer["dropout"] = round(random.uniform(min_dropout, max_dropout), 1)
            layers.append(layer)

        exponent = random.randint(
            int(round(math.log10(1e-5))),
            int(round(math.log10(1e-3)))
        )
        leading_digit = random.choice([1, 2, 5])
        learning_rate = leading_digit * (10 ** exponent)
        learning_rate = min(max(learning_rate, 1e-5), 1e-3)

        param = {
            "layers": layers,
            "learning_rate": learning_rate
        }
        params[f"random_{count}"] = param

    return params

def get_param_summary(params):
    layers = params.get("layers", [])
    num_layers = len(layers)
    units_list = [layer.get("units", 0) for layer in layers]
    dropout_list = [layer.get("dropout", 0.0) for layer in layers]

    activations = set(layer.get("activation", "relu") for layer in layers)
    if len(activations) == 1:
        main_activation = activations.pop()
    else:
        main_activation = "mixed"

    num_dropout = sum(1 for d in dropout_list if d > 0)
    avg_dropout = round(sum(d for d in dropout_list if d > 0), 2) / num_dropout if num_dropout > 0 else 0

    summary = {
        "num_layers": num_layers,
        "total_units": sum(units_list),
        "avg_units": round(sum(units_list)/num_layers) if num_layers > 0 else 0,
        "max_units": max(units_list) if units_list else 0,
        "min_units": min(units_list) if units_list else 0,
        "num_dropout": num_dropout,
        "avg_dropout": avg_dropout,
        "learning_rate": params.get("learning_rate", 0),
        "activation": main_activation,
        "raw_params": json.dumps(params),

    }
    return summary