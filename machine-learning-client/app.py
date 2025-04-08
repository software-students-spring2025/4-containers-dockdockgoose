from flask import Flask, request, jsonify
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import os

from io import BytesIO

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

# Define input prompt
INSTRUCTION_PROMPT = """
tell me how many cal is in this no yapping just a number if you need to guess it then guess it but give just ONE number in response
"""

# Process uploaded image
def input_image_setup(file_bytes, mime_type):
    return [{
        "mime_type": mime_type,
        "data": file_bytes
    }]

# Query Gemini model
def get_gemini_response(image_data, user_prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([INSTRUCTION_PROMPT, image_data[0], user_prompt])
    return response.text

# Main route
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    user_prompt = request.form.get("prompt", "")

    try:
        # Read file content
        file_bytes = file.read()
        image_data = input_image_setup(file_bytes, file.mimetype)
        
        # Run inference
        result = get_gemini_response(image_data, user_prompt)
        return jsonify({"calories": result.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check
@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "ML client is running"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)