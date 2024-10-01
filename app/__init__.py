from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
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

    from .routes import app as routes_blueprint

    app.register_blueprint(routes_blueprint)

    return app


def init_db():
    from .models import init_db as db_init

    db_init()


def load_plugins():
    from .utils import load_plugins as load_plugins_func

    return load_plugins_func()


def init_websites(websites_data):
    from .models import init_websites as init_websites_func

    init_websites_func(websites_data)
