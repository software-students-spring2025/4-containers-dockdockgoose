from flask import Flask, request, jsonify, redirect, url_for, render_template
from pymongo import MongoClient
import os
import requests
import base64
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb://mongodb:27017/")
db = client["gallery"]
collection = db["images"]

os.makedirs("static", exist_ok=True)

@app.route("/")
def home():
    return redirect(url_for("upload"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_files = request.files.getlist("images")
        collection.delete_many({})  # Clear previous entries
        for file in uploaded_files[:4]:
            filename = file.filename
            filepath = os.path.join("static", filename)
            file.save(filepath)

            with open(filepath, "rb") as img_file:
                response = requests.post("http://machine-learning-client:5000/caption", files={"image": img_file})
                caption = response.json().get("caption", "No caption")

            collection.insert_one({
                "filename": filename,
                "caption": caption,
                "timestamp": datetime.now().isoformat()
            })
        return redirect(url_for("gallery"))
    return render_template("upload.html")

@app.route("/gallery")
def gallery():
    images = list(collection.find())
    return render_template("gallery.html", images=images)

@app.route("/live")
def live():
    return render_template("live.html")

@app.route("/live-capture", methods=["POST"])
def live_capture():
    if "image" not in request.files:
        return jsonify({"caption": "No image uploaded"}), 400

    file = request.files["image"]
    filepath = os.path.join("static", "live_temp.jpg")
    file.save(filepath)

    try:
        with open(filepath, "rb") as img_file:
            response = requests.post(
                "http://machine-learning-client:5000/caption",
                files={"image": img_file}
            )
        caption = response.json().get("caption", "No caption")
        return jsonify({"caption": caption})
    except Exception as e:
        return jsonify({"caption": f"Error: {str(e)}"}), 500

@app.route("/emotions", methods=["GET"])
def emotions():
    return render_template("emotions.html")

@app.route("/emotions-capture", methods=["POST"])
def emotions_capture():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    f = request.files["image"]
    try:
        response = requests.post("http://machine-learning-client:5000/emotion", files={"image": f})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)