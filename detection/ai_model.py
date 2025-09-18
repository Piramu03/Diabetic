import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from PIL import Image,ImageOps
import io
import os
from django.conf import settings

class RetinopathyDetector:
    def __init__(self):
        self.input_size = (224, 224)
        self.model = None
        self.class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained model"""
        try:
            model_path = settings.MODEL_PATH
            if os.path.exists(model_path):
                self.model = load_model(model_path)
            else:
                # Load a placeholder model (in production, you would have a trained model)
                self.model = self.create_placeholder_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = self.create_placeholder_model()
    
    def create_placeholder_model(self):
        """Create a simple placeholder model for demonstration"""
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(224, 224, 3)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')
        ])
        return model
    
    def preprocess_image(self, img,enhance=True):
        if isinstance(img, bytes):
            img = Image.open(io.BytesIO(img))

        # Force RGB
        img = img.convert('RGB')

        img = img.resize(self.input_size)
        if enhance:
            img = ImageOps.autocontrast(img)
            img = ImageOps.equalize(img)

        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        return img_array


    
    def predict(self, image_data):
        """Make prediction on the image"""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_data)
            
            # Make prediction
            predictions = self.model.predict(processed_image)
            predicted_class = np.argmax(predictions[0])
            confidence = np.max(predictions[0])
            
            return self.class_names[predicted_class], float(confidence)
        except Exception as e:
            print(f"Error during prediction: {e}")
            return "Error", 0.0

# Global instance of the detector
detector = RetinopathyDetector()