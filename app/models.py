import os
import sqlite3
from datetime import datetime
import textwrap
from sqlalchemy.exc import SQLAlchemyError

from .utils import adapt_datetime, convert_datetime, scrape_website, send_email
from . import db

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


class Website(db.Model):
    __tablename__ = 'websites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    plugin_name = db.Column(db.String, nullable=False)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)
    last_link_count = db.Column(db.Integer)
    last_checked = db.Column(db.DateTime)
    scrape_interval = db.Column(db.String, default='daily')
    links = db.relationship('Link', backref='website', lazy=True)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    link = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

class CustomWebsite(db.Model):
    __tablename__ = 'custom_websites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    last_hash = db.Column(db.String)
    last_checked = db.Column(db.DateTime)
    scrape_interval = db.Column(db.String, default='daily')
    is_ui_generated = db.Column(db.Boolean, default=False)

def init_db():
    db.create_all()


def get_websites():
    regular_websites = Website.query.all()
    custom_websites = CustomWebsite.query.all()
    
    websites = [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "plugin_name": w.plugin_name,
            "is_enabled": w.is_enabled,
            "last_link_count": w.last_link_count,
            "last_checked": w.last_checked,
            "scrape_interval": w.scrape_interval,
            "is_ui_generated": False,
        }
        for w in regular_websites
    ] + [
        {
            "id": f"custom_{w.id}",
            "name": w.name,
            "url": w.url,
            "plugin_name": None,
            "is_enabled": None,
            "last_link_count": None,
            "last_checked": w.last_checked,
            "scrape_interval": w.scrape_interval,
            "is_ui_generated": w.is_ui_generated,
        }
        for w in custom_websites
    ]
    
    return websites

def toggle_website(id):
    website = Website.query.get(id)
    if website:
        website.is_enabled = not website.is_enabled
        db.session.commit()


def manual_scrape(id):
    try:
        if id.startswith("custom_"):
            website = CustomWebsite.query.get(id.split("_")[1])
            if website:
                url = website.url
                plugin_name = f"custom_{website.name.replace(' ', '_')}"
        else:
            website = Website.query.get(id)
            if website:
                url = website.url
                plugin_name = website.plugin_name

        if not website:
            return "Website not found"

        scrape_result = scrape_website(url, plugin_name)

        if scrape_result:
            current_link_count = scrape_result["link_count"]
            current_links_with_descriptions = scrape_result["links_with_descriptions"]

            if isinstance(website, CustomWebsite):
                html_hash = scrape_result["html_hash"]
                existing_links = set()  # CustomWebsite doesn't have links
            else:
                existing_links = set(link.link for link in website.links)

            new_links_with_descriptions = [
                link for link in current_links_with_descriptions
                if link[0] not in existing_links
            ]

            if new_links_with_descriptions:
                for link, description in new_links_with_descriptions:
                    new_link = Link(website_id=website.id, link=link, description=description)
                    db.session.add(new_link)

                subject = f"New links detected on {url}"
                body = "The following new links were found:\n\n" + "\n".join(
                    [f"{link[0]} - {link[1]}" for link in new_links_with_descriptions]
                )
                send_email(subject, body)

                result = f"Update detected: {len(new_links_with_descriptions)} new links found"
            else:
                result = "No new links found"

            if isinstance(website, CustomWebsite):
                website.last_hash = html_hash
            else:
                website.last_link_count = current_link_count

            website.last_checked = db.func.now()
            db.session.commit()
        else:
            result = "Scraping failed"

    except SQLAlchemyError as e:
        db.session.rollback()
        result = f"Database error: {str(e)}"

    return result


def update_interval(id, interval):
    if id.startswith("custom_"):
        website = CustomWebsite.query.get(id.split("_")[1])
    else:
        website = Website.query.get(id)
    
    if website:
        website.scrape_interval = interval
        db.session.commit()
        return f"Scrape interval updated to {interval}"
    return "Website not found"


def init_websites(websites_data):
    if Website.query.count() == 0:
        for data in websites_data:
            website = Website(**data)
            db.session.add(website)
        db.session.commit()


def check_updates(current_app):
    websites = Website.query.filter_by(is_enabled=True).all()
    for website in websites:
        scrape_result = scrape_website(website.url, website.plugin_name)
        if scrape_result:
            current_link_count = scrape_result["link_count"]
            current_links_with_descriptions = scrape_result["links_with_descriptions"]

            existing_links = set(link.link for link in website.links)
            new_links_with_descriptions = [
                link for link in current_links_with_descriptions
                if link[0] not in existing_links
            ]

            if new_links_with_descriptions:
                for link, description in new_links_with_descriptions:
                    new_link = Link(website_id=website.id, link=link, description=description)
                    db.session.add(new_link)

                subject = f"New links detected on {website.url}"
                body = "The following new links were found:\n\n" + "\n".join(
                    [f"{link[0]} - {link[1]}" for link in new_links_with_descriptions]
                )
                send_email(subject, body)

            website.last_link_count = current_link_count
            website.last_checked = datetime.now()

    db.session.commit()


def add_custom_website(name, url):
    custom_website = CustomWebsite(name=name, url=url, scrape_interval="never", is_ui_generated=True)
    db.session.add(custom_website)
    db.session.commit()
    
# Create a plugin file for the custom website
    plugin_name = f"custom_{name.replace(' ', '_')}"
    plugin_content = f"""
        import requests
        import hashlib

        WEBSITE_NAME = "{name}"
        WEBSITE_URL = "{url}"


        def scrape(url):
            headers = {{"User-Agent": "Mozilla/5.0"}}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return {{
                    "link_count": 0,
                    "links_with_descriptions": [],
                    "html_hash": hashlib.sha256(response.content).hexdigest()
                }}
            else:
                return None
    """

    with open(f"plugins/{plugin_name}.py", "w") as f:
        f.write(textwrap.dedent(plugin_content))
    
    return f"Custom website {name} added successfully"


def check_custom_updates():
    custom_websites = CustomWebsite.query.all()

    for website in custom_websites:
        plugin_name = f"custom_{website.url.replace(' ', '_')}"
        scrape_result = scrape_website(website.url, plugin_name)
        if scrape_result:
            current_hash = scrape_result["html_hash"]
            if current_hash != website.last_hash:
                subject = f"Update detected on {website.url}"
                body = "The website content has changed."
                send_email(subject, body)

                website.last_hash = current_hash
                website.last_checked = datetime.now()

    db.session.commit()


def delete_custom_website(id):
    if id.startswith("custom_"):
        custom_website = CustomWebsite.query.get(id.split("_")[1])
        if custom_website and custom_website.is_ui_generated:
            db.session.delete(custom_website)
            db.session.commit()
            
            # Delete the corresponding plugin file
            plugin_name = f"custom_{custom_website.name.replace(' ', '_')}"
            if os.path.exists(f"plugins/{plugin_name}.py"):
                os.remove(f"plugins/{plugin_name}.py")
                
                return f"Custom website {custom_website.name} deleted successfully"
        elif custom_website:
            return "Cannot delete manually created plugin"
    return "Website not found"
