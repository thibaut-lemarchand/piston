from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    
    # If config is provided, update the app config with it
    if config:
        app.config.update(config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///websites.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PORT"] = int(os.getenv("PORT", 5000))
    app.config["EMAIL_ADDRESS"] = os.getenv("EMAIL_ADDRESS")
    app.config["EMAIL_PASSWORD"] = os.getenv("EMAIL_PASSWORD")
    app.config["RECIPIENT_EMAIL"] = os.getenv("RECIPIENT_EMAIL")

    if app.config["EMAIL_ADDRESS"] is None:
        raise ValueError(
            "EMAIL_ADDRESS is not set. Please set it in your environment or .env file."
        )
    if app.config["EMAIL_PASSWORD"] is None:
        raise ValueError(
            "EMAIL_PASSWORD is not set. Please set it in your environment or .env file."
        )
    if app.config["RECIPIENT_EMAIL"] is None:
        raise ValueError(
            "RECIPIENT_EMAIL is not set. Please set it in your environment or .env file."
        )

    db.init_app(app)

    from .routes import app as routes_blueprint

    app.register_blueprint(routes_blueprint)

    return app

def init_db(app):
    with app.app_context():
        db.create_all()

def load_plugins():
    from .utils import load_plugins as load_plugins_func

    return load_plugins_func()

def init_websites(app, websites_data):
    from .models import Website
    
    with app.app_context():
        if Website.query.count() == 0:
            for data in websites_data:
                # Assuming data is a tuple of (name, url, plugin_name)
                website = Website(
                    name=data[0],
                    url=data[1],
                    plugin_name=data[2],
                    is_enabled=True,  # Set a default value
                    scrape_interval="never"  # Set a default value
                )
                db.session.add(website)
            db.session.commit()
