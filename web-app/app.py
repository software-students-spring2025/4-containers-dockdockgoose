import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form["prompt"]
        file = request.files["file"]

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Send to ML service
            files = {"file": open(filepath, "rb")}
            data = {"prompt": prompt}
            ml_response = requests.post("http://localhost:8501/predict", files=files, data=data)

            result = ml_response.text
            return render_template("index.html", result=result, image_url=filepath)

    return render_template("index.html", result=None, image_url=None)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
