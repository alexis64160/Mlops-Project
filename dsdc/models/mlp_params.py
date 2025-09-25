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
        min_units=512,
        max_units=2048,
        unit_multiple=16,
        min_learning_rate=1e-5,
        max_learning_rate=1e-3,
        activation_functions={"relu": {}, "leaky_relu": {"min_lr": 1e-5, "max_lr": 1e-3}},
        dropout_frequency=0.7,
        min_dropout=0.0,
        max_dropout=0.5,
):
    """
    Generate a list of random MLP model configurations.

    Each configuration includes a random number of layers, units per layer (multiple of `unit_multiple`),
    random activations (from `activation_functions`), optional dropout, and a learning rate with
    one significant digit between `min_learning_rate` and `max_learning_rate`.

    Args:
        amount (int): Number of configurations to generate.
        min_layers (int): Minimum number of layers.
        max_layers (int): Maximum number of layers.
        min_units (int): Minimum total units across all layers.
        max_units (int): Maximum total units across all layers.
        unit_multiple (int): Unit count will be a multiple of this.
        min_learning_rate (float): Minimum learning rate.
        max_learning_rate (float): Maximum learning rate.
        activation_functions (dict): Activation types with optional constraints (e.g., slope ranges).
        dropout_frequency (float): Probability of applying dropout to a layer.
        min_dropout (float): Minimum dropout rate.
        max_dropout (float): Maximum dropout rate.

    Returns:
        list[dict]: A list of random MLP configurations.
    """
    params = dict()

    for count in range(1, amount + 1):
        num_layers = random.randint(min_layers, max_layers)

        min_power = math.ceil(math.log2(max(unit_multiple, min_units)))
        max_power = math.floor(math.log2(max_units))
        allowed_units = [2 ** i for i in range(min_power, max_power + 1)]
        while True:
            layer_units = [random.choice(allowed_units) for _ in range(num_layers)]
            total = sum(layer_units)
            if min_units <= total <= max_units:
                break

        layers = []
        for units in layer_units:
            layer = {"units": units}
            activation = random.choice(list(activation_functions.keys()))
            layer["activation"] = activation
            if activation == "leaky_relu":
                # Optional: configure slope or learning rate constraints
                layer["negative_slope"] = round(random.uniform(0.01, 0.3), 2)
            if random.random() < dropout_frequency:
                layer["dropout"] = round(random.uniform(min_dropout, max_dropout), 1)
            layers.append(layer)

        # Generate learning rate with 1 significant digit
        exponent = random.randint(
            int(round(math.log10(min_learning_rate))),
            int(round(math.log10(max_learning_rate)))
        )
        leading_digit = random.choice([1, 2, 5])
        learning_rate = leading_digit * (10 ** exponent)
        learning_rate = min(max(learning_rate, min_learning_rate), max_learning_rate)
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