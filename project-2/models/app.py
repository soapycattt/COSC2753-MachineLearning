import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
from tensorflow.keras import models
import os
from recommend import find_similar_images

app = FastAPI()
_FURNITURES = ["table", "sofa", "lamp", "chair", "dresser", "bed"]


def _load_model(model_name: str):
    return models.load_model(model_name)


def _get_image(img_path) -> np.ndarray:
    image = cv2.imread(img_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _classify(img_path: str) -> str:
    img = _get_image(img_path)
    # Resize the image to match your model's input size
    img_resized = cv2.resize(
        img, (50, 50)
    )  # Update img_width and img_height with your image size

    # Expand dimensions to create a batch dimension
    img_array = np.expand_dims(img_resized, axis=0)

    # Make predictions
    predictions = classification_model.predict(img_array, verbose=0)
    predicted_class_index = np.argmax(predictions)

    return _FURNITURES[predicted_class_index - 1]


def _get_img_path(img_idx: int) -> str:
    relative_path = "../Custom_Furniture_Data"
    file_name = f"custom-img-{img_idx}.png"
    return os.path.join(relative_path, file_name)


def _get_encoder(model):
    encoder = models.Sequential()
    for layer in model.layers[:-2]:  # Exclude the last two layers (flatten and dense)
        encoder.add(layer)
    return encoder


# Task 1 Model
classification_model_name = "model_task_1_cnn_classification.h5"
classification_model = _load_model(classification_model_name)

# Task 2 Model
recommendation_model_name = "model_task_2_cnn_classification.h5"
recommendation_model = _load_model(recommendation_model_name)
encoder = _get_encoder(recommendation_model)


@app.get("/", response_class=HTMLResponse)
def index():
    return "<h1>Welcome to the Furniture Machine Learning API</h1>"


@app.get("/classify")
def classify(img_idx: int) -> dict:
    # Get relative file path
    img_path = _get_img_path(img_idx)

    # Predict and return the result
    predicted_furniture = _classify(img_path)
    return {"result": predicted_furniture}


@app.get("/recommend")
def recommend(img_idx: int) -> dict:
    img_path = _get_img_path(img_idx)
    paths, distances = find_similar_images(recommendation_model, encoder, img_path)

    # TODO: Extract data from multi-dimension array `distances`
    #  [[27.37364001 28.79204727 29.02428353 29.03651842 29.2367386  29.3095765 29.63712217 29.74092537 29.81967957 29.8546811 ]]
    print(paths)
    print(distances)

    return {"paths": "haha", "distances": "haha"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
