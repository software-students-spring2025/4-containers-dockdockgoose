#!/usr/bin/env python3

"""
Main web application for the intelligent calorie tracker.
Handles registration, login, data capture from webcam,
and interfaces with the machine learning client.
"""

import os
from datetime import datetime
from datetime import date
from bson.objectid import ObjectId
import requests
import pymongo
import flask_login
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from dotenv import load_dotenv, dotenv_values
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
config = dotenv_values()
app.config.from_mapping(config)

# Initialize MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]

# Flask-Login setup
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(flask_login.UserMixin):
    """User model for authentication"""

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.username = user_data["username"]
        self.password = user_data["password"]

    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        user_data = db.calcountInfo.find_one({"username": username})
        return User(user_data) if user_data else None

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        user_data = db.calcountInfo.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(email, username, password):
        """Register new user"""
        if db.calcountInfo.find_one({"username": username}) or db.calcountInfo.find_one(
            {"email": email}
        ):
            return False

        hashed_password = generate_password_hash(password)
        db.calcountInfo.insert_one(
            {
                "email": email,
                "username": username,
                "password": hashed_password,
            }
        )
        return True


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader"""
    return User.find_by_id(user_id)


@app.route("/")
def index():
    """Redirect to registration"""
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if User.create_user(email, username, password):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        flash("Username or email already exists.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.find_by_username(username)

        if user and check_password_hash(user.password, password):
            flask_login.login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/home")
@flask_login.login_required
def home():
    """Homepage"""
    logs = (
        db.calorieData.find({"user_id": current_user.username})
        .sort("date", -1)  # Sort by most recent date
        .limit(5)  # Show last 5 entries
    )
    return render_template("home.html", logs=logs, username=current_user.username)


@app.route("/logout")
@flask_login.login_required
def logout():
    """Logout user"""
    flask_login.logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/capture", methods=["POST"])
@flask_login.login_required
def capture():
    """Capture image from webcam, send to ML, log calories"""
    file = request.files.get("file")
    prompt = request.form.get("prompt", "")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        ml_url = "http://machine_learning_client:5000/predict"
        response = requests.post(
            ml_url,
            files={"file": (file.filename, file.stream, file.mimetype)},
            data={"prompt": prompt},
            timeout=5,
        )

        data = response.json()
        num = data.get("calories")

        if isinstance(num, (int, float)) or (isinstance(num, str) and num.isdigit()):
            num = int(num)

            query = {"user_id": current_user.username, "date": str(date.today())}
            existing = db.calorieData.find_one(query)

            if existing:
                num += existing.get("calories", 0)
                db.calorieData.update_one(query, {"$set": {"calories": num}})
            else:
                db.calorieData.insert_one(
                    {
                        "user_id": current_user.username,
                        "calories": num,
                        "date": str(date.today()),
                    }
                )
        else:
            return jsonify({"error": f"Invalid calorie value: {num}"}), 400

        return jsonify(data)

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.template_filter("pretty_date")
def pretty_date(value):
    """Formatting the date"""
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%B %-d, %Y")  # Mac/Linux
    except ValueError:
        return value


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
