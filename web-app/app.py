#!/usr/bin/env python3

import os
import datetime
import flask_login
import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv, dotenv_values
from flask_login import login_required, current_user

load_dotenv()  # Load environment variables

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
config = dotenv_values()
app.config.from_mapping(config)

# Initialize MongoDB connection
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]

# Initialize Flask-Login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# User model for authentication
class User(flask_login.UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"]) 
        self.email = user_data["email"]
        self.username = user_data["username"]
        self.password = user_data["password"]

    @staticmethod
    def find_by_username(username):
        """Find user by username in MongoDB."""
        user_data = db.calcountInfo.find_one({"username": username})
        return User(user_data) if user_data else None

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID in MongoDB."""
        user_data = db.calcountInfo.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(email, username, password):
        """Create a new user in MongoDB."""
        if db.calcountInfo.find_one({"username": username}):
            return False  # Username already exists
        
        if db.calcountInfo.find_one({"email": email}):
            return False  # Email already exists
        
        hashed_password = generate_password_hash(password) 
        db.calcountInfo.insert_one({
            "email": email,
            "username": username,
            "password": hashed_password,
        })
        return True
    
# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)


@app.route("/")
def index():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if User.create_user(email, username, password):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists. Please try again.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
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
    user = flask_login.current_user.username
    docs = db.calorieData.find({'user_id':user})
    return render_template("home.html", user = user, data = docs)


@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/add", methods=["GET","POST"])
@flask_login.login_required
def add():
    if request.method == "POST":
        doc = {}
        for item in request.form:
            doc[item] = request.form[item]
        doc['user_id'] = flask_login.current_user.username
        db.calorieData.insert_one(doc)
        return redirect("/home")
    return render_template("add.html")

# Run the app
if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    FLASK_ENV = os.getenv("FLASK_ENV")
    print(f"FLASK_ENV: {FLASK_ENV}, FLASK_PORT: {FLASK_PORT}")

    app.run(port=int(FLASK_PORT), debug=(FLASK_ENV == "development"))