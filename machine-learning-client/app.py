"""ML client API for estimating calories from food images using Gemini."""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)

INSTRUCTION_PROMPT = os.getenv("INSTRUCTION_PROMPT")


def input_image_setup(file_bytes, mime_type):
    """Prepare image input for Gemini."""
    return [{"mime_type": mime_type, "data": file_bytes}]


def get_gemini_response(image_data, user_prompt):
    """Send image and prompt to Gemini API and return response."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([INSTRUCTION_PROMPT, image_data[0], user_prompt])
    return response.text


@app.route("/predict", methods=["POST"])
def predict():
    """API endpoint to receive an image and return estimated calories."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    user_prompt = request.form.get("prompt", "")

    try:
        file_bytes = file.read()
        image_data = input_image_setup(file_bytes, file.mimetype)
        result = get_gemini_response(image_data, user_prompt)
        return jsonify({"calories": result.strip()})
    except Exception as e:  # pylint: disable=broad-exception-caught
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    return jsonify({"message": "ML client is running"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
