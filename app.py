from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import flask_login
from dotenv import load_dotenv, dotenv_values
import pymongo
from bson.objectid import ObjectId
import datetime
import os
import db as database

load_dotenv()

def create_app():
    """
    Create and configure Flash app
    returns app
    """

    db = database.db_connect()


    
    SECRET_KEY = os.getenv('SECRET_KEY')

    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    config = dotenv_values()
    app.config.from_mapping(config)

    login_manager = flask_login.LoginManager()
    login_manager.login_view = "login" 
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None

    # routes here
    # need to add login section and home page first

    @app.route("/")
    def index():
        """
        Route for the root page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        response = make_response(render_template('index.html'), 200)
        return response
    
    @app.route("/test")
    def testDB():
        print("dbname",db.name, flush=True)
        print("Collections:",db.list_collection_names())
        users = list(db.Users.find({}))
        print("users",users)
        return make_response(render_template("root.html", profiles=users), 200)


    return app

app = create_app()

if __name__ == "__main__":
    PORT = int(os.getenv("FLASK_PORT"))
    print("Flask App running on port", PORT)
    app.run(port=PORT, debug=True)