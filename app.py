from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import flask_login
from dotenv import load_dotenv
import pymongo
from bson.objectid import ObjectId
import datetime
import os

load_dotenv()

MONGO_DBNAME = os.getenv('MONGO_DBNAME')
MONGO_URI = os.getenv('MONGO_URI')
PORT = int(os.getenv("PORT"))
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY

connection = pymongo.MongoClient(MONGO_URI)
db = connection[MONGO_DBNAME]

login_manager = flask_login.LoginManager()
login_manager.login_view = "login" 
login_manager.init_app(app)

# routes here
# need to add login section and home page first

if __name__ == "__main__":
    app.run(port=PORT, debug=True)