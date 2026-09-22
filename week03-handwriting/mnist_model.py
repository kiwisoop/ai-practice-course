"""Shared MNIST training, preprocessing, and prediction utilities.

Created with Codex on 2026-09-10.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "mnist_model.keras"


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Convert a drawn digit to a centered 28x28 MNIST-style tensor."""
    grayscale = image.convert("L")
    array = np.asarray(grayscale)
    points = np.argwhere(array > 20)
    if points.size == 0:
        raise ValueError("Draw a digit before recognizing it.")

    top, left = points.min(axis=0)
    bottom, right = points.max(axis=0) + 1
    cropped = grayscale.crop((left, top, right, bottom))

    scale = min(20 / cropped.width, 20 / cropped.height)
    size = (
        max(1, round(cropped.width * scale)),
        max(1, round(cropped.height * scale)),
    )
    resized = cropped.resize(size, Image.Resampling.LANCZOS)
    centered = Image.new("L", (28, 28), 0)
    centered.paste(resized, ((28 - size[0]) // 2, (28 - size[1]) // 2))

    normalized = np.asarray(centered, dtype=np.float32) / 255.0
    return normalized.reshape(1, 28, 28, 1)


def load_or_train_model():
    """Load the saved model, or train and save it on the first run."""
    import tensorflow as tf

    if MODEL_PATH.exists():
        print(f"Loading model from {MODEL_PATH.name}...")
        return tf.keras.models.load_model(MODEL_PATH)

    print("Downloading MNIST and training the model. This happens only once...")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    x_train = x_train[..., np.newaxis]
    x_test = x_test[..., np.newaxis]

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(28, 28, 1)),
            tf.keras.layers.Conv2D(16, 3, activation="relu"),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(x_train, y_train, epochs=3, batch_size=128, validation_split=0.1)
    _, accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"MNIST test accuracy: {accuracy:.2%}")
    model.save(MODEL_PATH)
    return model


def predict_digit(model, image: Image.Image) -> tuple[int, float]:
    """Return the predicted digit and confidence for a Pillow image."""
    probabilities = model.predict(preprocess_image(image), verbose=0)[0]
    digit = int(np.argmax(probabilities))
    return digit, float(probabilities[digit])
