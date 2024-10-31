import os
import importlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app

def adapt_datetime(dt):
    return dt.isoformat()


def convert_datetime(dt_str):
    return datetime.fromisoformat(dt_str.decode())


def load_plugins():
    plugins = {}
    websites_data = []
    plugins_dir = os.path.join(os.path.dirname(__file__), '..', "plugins")
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            plugin_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(plugin_name, os.path.join(plugins_dir, filename))
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            
            plugins[plugin_name] = plugin
            websites_data.append((plugin.WEBSITE_NAME, plugin.WEBSITE_URL, plugin_name))
    
    return plugins, websites_data


def scrape_website(url, plugin_name):
    plugins, _ = load_plugins()
    if plugin_name in plugins:
        return plugins[plugin_name].scrape(url)
    else:
        print(f"No plugin found for {plugin_name}")
        return None


def send_email(subject, body):
    with current_app.app_context():
        msg = MIMEMultipart()
        msg["From"] = current_app.config["EMAIL_ADDRESS"]
        msg["To"] = current_app.config["RECIPIENT_EMAIL"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(current_app.config["EMAIL_ADDRESS"], current_app.config["EMAIL_PASSWORD"])
                server.send_message(msg)
            print("Email sent successfully")
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {e}")
        except smtplib.SMTPException as e:
            print(f"SMTP Exception: {e}")
        except Exception as e:
            print(f"Error sending email: {e}")
