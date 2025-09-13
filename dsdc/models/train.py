import numpy as np
import logging
from sklearn.model_selection import train_test_split

from dsdc.models.mlp import MLP, INITIAL_BEST_KNWON_PARAMS
from dsdc.db.crud.embeddings import get_embedding_label_pairs

def train(model, embeddings, labels):
    X = np.array(embeddings, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)  # sparse categorical = int labels

    # Split train / validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Entraînement
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=20,
        batch_size=32,
        verbose=1
    )
    logging.info(f"Successfully trained model - latest_accuracy = {history.history["accuracy"][-1]}")
    return history


if __name__ == "__main__":
    model = MLP(params=INITIAL_BEST_KNWON_PARAMS['MLP12'])
    embeddings, labels = get_embedding_label_pairs()
    train(model, embeddings, labels)
    model.save("test.keras")