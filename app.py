# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, abort
import flask_login
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
import os, hashlib, secrets, datetime
from bson.objectid import ObjectId

from db import db_connect

load_dotenv()

PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

app = Flask(__name__)
app.secret_key = SECRET_KEY

db = db_connect()
users_col = db["users"]
restaurants_col = db["restaurants"]

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, _id, username):
        self.id = str(_id)
        self.username = username

def _user_from_doc(doc):
    if not doc: return None
    return User(doc["_id"], doc["username"])

@login_manager.user_loader
def load_user(user_id):
    doc = users_col.find_one({"_id": ObjectId(user_id)})
    return _user_from_doc(doc)

# simple pw hash
def hash_password(plain: str, salt_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(salt_hex) + plain.encode("utf-8")).hexdigest()

def make_password_record(plain: str):
    salt_hex = secrets.token_hex(16)
    return {"salt": salt_hex, "hash": hash_password(plain, salt_hex)}

# ---------------------- ROUTES ----------------------

@app.route("/")
def home():
    """Home page: show latest restaurants (DB display #1)."""
    latest = list(restaurants_col.find().sort("created_at", -1).limit(10))
    return render_template("home.html", restaurants=latest, user=current_user if current_user.is_authenticated else None)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Create user (Add)."""
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not username or not password:
            flash("Username and password required.", "error")
            return redirect(url_for("register"))
        if users_col.find_one({"username": username}):
            flash("Username already taken.", "error")
            return redirect(url_for("register"))

        pwd = make_password_record(password)
        doc = {
            "username": username,
            "password": pwd,
            "display_name": username,
            "created_at": datetime.datetime.utcnow(),
        }
        res = users_col.insert_one(doc)
        login_user(User(res.inserted_id, username))
        flash("Registered and logged in!", "success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    """Login with username/password."""
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        doc = users_col.find_one({"username": username})
        if not doc:
            flash("Invalid credentials.", "error")
            return redirect(url_for("login"))
        salt = doc["password"]["salt"]
        if hash_password(password, salt) == doc["password"]["hash"]:
            login_user(_user_from_doc(doc))
            flash("Welcome back!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/profile", methods=["GET","POST"])
@login_required
def profile():
    """Profile (Edit data)."""
    if request.method == "POST":
        new_display = request.form.get("display_name","").strip()
        if new_display:
            users_col.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"display_name": new_display}})
            flash("Profile updated.", "success")
        new_pw = request.form.get("new_password","")
        if new_pw:
            users_col.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$set": {"password": make_password_record(new_pw)}}
            )
            flash("Password changed.", "success")
        return redirect(url_for("profile"))

    doc = users_col.find_one({"_id": ObjectId(current_user.id)})
    return render_template("profile.html", userdoc=doc)

@app.route("/restaurants", methods=["GET","POST"])
@login_required
def restaurants():
    """
    Restaurants page combines:
    - Display list (DB display #2)
    - Add new restaurant (Add)
    - Search (?q=) (Search)
    - Delete via POST to /restaurants/<id>/delete (Delete)
    """
    if request.method == "POST":
        # Add a new restaurant
        name = request.form.get("name","").strip()
        cuisine = request.form.get("cuisine","").strip()
        if name:
            restaurants_col.insert_one({
                "name": name,
                "cuisine": cuisine,
                "created_by": ObjectId(current_user.id),
                "created_at": datetime.datetime.utcnow()
            })
            flash("Restaurant added.", "success")
        else:
            flash("Name is required.", "error")
        return redirect(url_for("restaurants"))

    q = request.args.get("q","").strip()
    query = {}
    if q:
        query = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"cuisine": {"$regex": q, "$options": "i"}}
        ]}
    items = list(restaurants_col.find(query).sort("created_at", -1))
    return render_template("restaurants.html", items=items, q=q)

@app.route("/restaurants/<rid>/delete", methods=["POST"])
@login_required
def delete_restaurant(rid):
    """Only allow the creator to delete (Delete)."""
    try:
        oid = ObjectId(rid)
    except Exception:
        abort(400)
    doc = restaurants_col.find_one({"_id": oid})
    if not doc:
        abort(404)
    if str(doc.get("created_by")) != current_user.id:
        abort(403)
    restaurants_col.delete_one({"_id": oid})
    flash("Deleted.", "info")
    return redirect(url_for("restaurants"))

@app.route("/chat")
@login_required
def chat():
    """Placeholder screen to satisfy 'six screens'—can be extended later."""
    return render_template("chat.html"
    )

@app.route("/match")
@login_required
def match():
    return render_template("match.html")

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
