from flask import Flask, request, jsonify
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import onnxruntime as ort
import os
import cv2
from scipy.special import softmax

app = Flask(__name__)
caption_model = MobileNetV2(weights="imagenet")


@app.route("/caption", methods=["POST"])
def caption():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    file.save("temp.jpg")

    img = image.load_img("temp.jpg", target_size=(224, 224))
    x = np.expand_dims(image.img_to_array(img), axis=0)
    x = preprocess_input(x)

    preds = caption_model.predict(x)
    label = decode_predictions(preds, top=1)[0][0][1]

    return jsonify({"caption": f"This looks like a {label.lower()}."})


# Load emotion model
model_best = load_model("face_model.h5")
class_names = ['Angry', 'Disgusted', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

@app.route("/emotion", methods=["POST"])
def detect_emotion():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    file_path = "temp_emotion.jpg"
    file.save(file_path)

    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        return jsonify({"emotion": "no_face_detected"})

    x, y, w, h = faces[0]
    face_roi = gray[y:y + h, x:x + w]
    face_image = cv2.resize(face_roi, (48, 48))
    face_image = image.img_to_array(face_image)
    face_image = np.expand_dims(face_image, axis=0)

    preds = model_best.predict(face_image)
    emotion_label = class_names[np.argmax(preds)]

    print("Predictions:", preds)
    return jsonify({
        "emotion": emotion_label,
        "raw": preds[0].tolist()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)