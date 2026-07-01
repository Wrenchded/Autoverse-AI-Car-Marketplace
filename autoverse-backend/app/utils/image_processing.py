from PIL import Image
import numpy as np
import io


def preprocess_image(image_bytes: bytes, target_size=(224, 224)) -> np.ndarray:
    """
    Convert uploaded image bytes into model-ready tensor.
    Output shape: (1, 224, 224, 3)
    """

    # Load image from bytes
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Resize
    img = img.resize(target_size)

    # Convert to numpy
    arr = np.array(img, dtype=np.float32)

    # Normalize (0–1)
    arr = arr / 255.0

    # Add batch dimension
    arr = np.expand_dims(arr, axis=0)

    return arr