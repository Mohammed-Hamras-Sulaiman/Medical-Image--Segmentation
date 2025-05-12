from django.shortcuts import render
from django.conf import settings
import tensorflow as tf
from tensorflow import keras
from keras import models
from segmentation.models import load_model
import tensorflow as tf
import cv2
import numpy as np
import os



def segment_image(image_path):
    # Read and preprocess the image
    image = cv2.imread(image_path)
    resized_image = cv2.resize(image, (128, 128)) / 255.0
    input_array = np.expand_dims(resized_image, axis=0)

    # Predict the segmentation mask
    mask = model.predict(input_array)[0]
    mask = (mask > 0.5).astype(np.uint8)  # Thresholding

    # Resize mask to original dimensions
    mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
    result_path = os.path.join('media/results', os.path.basename(image_path))
    cv2.imwrite(result_path, mask_resized * 255)  # Save the mask as an image

    return result_path

import os
import cv2
import numpy as np
import tensorflow as tf
import keras
from keras.models import load_model
from keras.saving import register_keras_serializable

@register_keras_serializable(package="Custom")
# Jaccard Index Metric
def jaccard_index(y_true, y_pred, smooth=100):
    y_true_f = tf.reshape(tf.cast(y_true, tf.float32), [-1])
    y_pred_f = tf.reshape(tf.cast(y_pred, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    total = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) - intersection
    return (intersection + smooth) / (total + smooth)


# Dice Coefficient Metric
@register_keras_serializable(package="Custom")
def dice_coefficient(y_true, y_pred, smooth=1):
    y_true_f = tf.reshape(tf.cast(y_true, tf.float32), [-1])
    y_pred_f = tf.reshape(tf.cast(y_pred, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

# Load the pre-trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/unet_mri_xray_trained_model.h5.keras')
model = load_model(MODEL_PATH, custom_objects={'dice_coefficient': dice_coefficient, 'jaccard_index': jaccard_index})

def predict_image(image_path):
    """
    Predict segmentation mask for the given image path.
    :param image_path: Path to the input image.
    :return: Predicted mask as a NumPy array.
    """
    img = cv2.imread(image_path, 0)  # Load as grayscale
    img_resized = cv2.resize(img, (512, 512))
    img_normalized = img_resized / 255.0
    img_input = np.expand_dims(img_normalized, axis=-1)
    img_input = np.expand_dims(img_input, axis=0)

    # Predict the segmentation mask
    pred_mask = model.predict(img_input)
    pred_mask = np.squeeze(pred_mask)  # Remove batch dimension
    pred_mask = (pred_mask > 0.5).astype(np.uint8)  # Binarize the mask

    return pred_mask