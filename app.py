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

    # routes here
    # need to add login section and home page first

    @app.route("/")
    def root():
        """
        Route for the root page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        response = make_response("hellow world")
        response.mimetype = "text/plain"
        return response


    return app

app = create_app()

if __name__ == "__main__":
    PORT = int(os.getenv("FLASK_PORT"))
    app.run(port=PORT, debug=True)
    print("Flask App running on port", PORT)