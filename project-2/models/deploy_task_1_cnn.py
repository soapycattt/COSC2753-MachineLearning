from mlserver.codecs import decode_args
from mlserver import MLModel
from typing import List
import numpy as np
import cv2
from tensorflow.keras.models import load_model

_FURNITURES = ['table', 'sofa', 'lamp', 'chair', 'dresser', 'bed']

class ImgClassificationModel(MLModel):

    async def load(self):
        model_dir = "./models"
        model_h5_file = os.path.join(model_dir, "model_task_1_cnn_classification.h5")
        
        self.model = load_model(model_h5_file)

    
    @decode_args
    async def predict(self, img_path: str) -> str:
        img = _get_image(img_path)
        # Resize the image to match your model's input size
        img_resized = cv2.resize(img, (50, 50))  # Update img_width and img_height with your image size

        # Expand dimensions to create a batch dimension
        img_array = np.expand_dims(img_resized, axis=0)

        # Make predictions
        predictions = model.predict(img_array, verbose = 0)
        predicted_class_index = np.argmax(predictions)

        return _FURNITURES[predicted_class_index-1]

    def _get_image(img_path):
        image = cv2.imread(img_path)
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
