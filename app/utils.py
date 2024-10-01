import os
import importlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def adapt_datetime(dt):
    return dt.isoformat()


def convert_datetime(dt_str):
    return datetime.fromisoformat(dt_str.decode())


def load_plugins():
    plugins = {}
    websites_data = []
    for filename in os.listdir("plugins"):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module = importlib.import_module(f"plugins.{module_name}")
            if (
                hasattr(module, "scrape")
                and hasattr(module, "WEBSITE_NAME")
                and hasattr(module, "WEBSITE_URL")
            ):
                plugins[module_name] = {
                    "scrape": module.scrape,
                    "name": module.WEBSITE_NAME,
                    "url": module.WEBSITE_URL,
                }
                websites_data.append(
                    (module.WEBSITE_NAME, module.WEBSITE_URL, module_name, 1, "never")
                )
    return plugins, websites_data


def scrape_website(url, plugin_name):
    plugins, _ = load_plugins()
    if plugin_name in plugins:
        return plugins[plugin_name]["scrape"](url)
    else:
        print(f"No plugin found for {plugin_name}")
        return None


def send_email(subject, body, app):
    msg = MIMEMultipart()
    msg["From"] = app.config["EMAIL_ADDRESS"]
    msg["To"] = app.config["RECIPIENT_EMAIL"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(app.config["EMAIL_ADDRESS"], app.config["EMAIL_PASSWORD"])
            server.send_message(msg)
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except smtplib.SMTPException as e:
        print(f"SMTP Exception: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")
