import uvicorn
from fastapi import FastAPI
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os

app = FastAPI()
_FURNITURES = ['table', 'sofa', 'lamp', 'chair', 'dresser', 'bed']

def _load_model(model_name: str):
    # model_dir = "./models"
    # model_h5_file_path = os.path.join(model_dir, model_name)
    return load_model(model_name)

def _get_image(img_path) -> np.ndarray:
    image = cv2.imread(img_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def _classify(img_path: str) -> str:
    img = _get_image(img_path)
    # Resize the image to match your model's input size
    img_resized = cv2.resize(img, (50, 50))  # Update img_width and img_height with your image size
    
    # Expand dimensions to create a batch dimension
    img_array = np.expand_dims(img_resized, axis=0)
    
    # Make predictions
    predictions = classification_model.predict(img_array, verbose = 0)
    predicted_class_index = np.argmax(predictions)
    
    return _FURNITURES[predicted_class_index-1]

classification_model_name = "model_task_1_cnn_classification.h5"
classification_model = _load_model(classification_model_name)

@app.get('/')
def index():
    return {'message': 'Cars Recommender ML API'}

@app.get('/classify')
def classify(img_idx: int) -> dict:
    # Get relative file path
    relative_path = "../Custom_Furniture_Data"
    file_name = f"custom-img-{img_idx}.png"
    img_path = os.path.join(relative_path, file_name)

    # Predict and return the result
    predicted_furniture = _classify(img_path)
    return {'result': predicted_furniture}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
