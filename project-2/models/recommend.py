from sklearn.neighbors import KDTree
import pickle
import os
import numpy as np
import cv2
import re
from scipy.stats import pearsonr

furnitures = ["table", "sofa", "lamp", "chair", "dresser", "bed"]


def get_image_and_resize(img_path):
    img_arr = cv2.imread(img_path)

    # Downsize image for faster model training. BB
    # Normalize the image to scale 0-1 for faster training time and better performance
    return cv2.resize(img_arr, (100, 100)) / 255.0


def unnest_feature_vector_mapping(mapped_tuples):
    feature_vectors, paths = zip(*mapped_tuples)
    return list(feature_vectors), list(paths)


def load_category_data(category):
    vector_file = os.path.join("../vectors", f"{category}_vector.pkl")

    with open(vector_file, "rb") as file:
        data = pickle.load(file)

    feature_vectors_list, paths_list = unnest_feature_vector_mapping(data)

    # Build KDTree index
    kdtree_index = KDTree(feature_vectors_list)
    return kdtree_index, paths_list


def get_histogram(image: np.ndarray):
    # Convert to gray scale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate histograms
    histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

    return cv2.normalize(histogram, None).flatten()


def get_correlation_coeff(input_path, neighbor_path) -> float:
    input_img_arr = cv2.imread(input_path)
    neighbor_img_arr = cv2.imread(neighbor_path)

    input_hist = get_histogram(input_img_arr)
    neighbor_hist = get_histogram(neighbor_img_arr)

    # Get correlation
    correlation_coefficient, _ = pearsonr(input_hist, neighbor_hist)
    return correlation_coefficient


def correct_path(filepath: str) -> str:
    """Replace the image directory, cd back to parent dir, and remove '-' sign after the image number index.
    E.g.
        - Before: 'task1-2-furnitures/tables/Asian/29-contemporary-side-tables-and-end-tables.jpg'
        - After:  '../Furniture_Data/tables/Asian/29contemporary-side-tables-and-end-tables.jpg'
    """

    filepath = f"../{filepath.replace('task1-2-furnitures', 'Furniture_Data')}"
    return re.sub(r"(\d)-", r"\1", filepath)


# Function to find similar images for a given query image
def find_similar_images(model, encoder, query_image_path, top_k=10):
    # Preprocess query image
    query_img = get_image_and_resize(query_image_path)

    # get the image cat
    predicted_category_index = model.predict(np.expand_dims(query_img, axis=0)).argmax()
    predicted_category = furnitures[predicted_category_index - 1]

    # Load corresponding vectors from the vectors folder
    kdtree_index, img_paths = load_category_data(predicted_category)

    # Encode input image to feature vector
    query_features = encoder.predict(np.expand_dims(query_img, axis=0)).flatten()

    # Perform nearest neighbor search using KDTree index
    distances, indices = kdtree_index.query(query_features.reshape(1, -1), k=top_k)

    # Return paths of similar images
    similar_image_paths = [img_paths[idx] for idx in indices[0]]

    # Adhocly correct img path for Triet's device
    similar_image_paths = [correct_path(path) for path in similar_image_paths]
    print(similar_image_paths)

    # Get correlation scores
    corr_coeffs = [
        get_correlation_coeff(query_image_path, neighbor_path)
        for neighbor_path in similar_image_paths
    ]

    return similar_image_paths, distances, corr_coeffs
