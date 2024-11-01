import os
import sqlite3
import importlib.util
from datetime import datetime
import textwrap
from sqlalchemy.exc import SQLAlchemyError

from piston.utils import adapt_datetime, convert_datetime, scrape_website, send_email
from piston import db

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


class Website(db.Model):
    __tablename__ = 'websites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    plugin_name = db.Column(db.String, nullable=False)
    scraping_type = db.Column(db.String, default='links')
    last_checked = db.Column(db.DateTime)
    scrape_interval = db.Column(db.String, default='daily')

    def get_last_link_count(self):
        # Get the latest link counts entry for this website
        link_counts = LinkCounts.query.filter_by(website_id=self.id).order_by(LinkCounts.id.desc()).first()
        return link_counts.last_link_count if link_counts else None

class LinkCounts(db.Model):
    __tablename__ = 'link_history'
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    last_link_count = db.Column(db.Integer)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    link = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

class Hash(db.Model):
    __tablename__ = 'hash'
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    last_hash = db.Column(db.String, nullable=False)


def init_db():
    db.create_all()

def get_websites():
    websites = Website.query.all()

    websites = [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "plugin_name": w.plugin_name,
            "scraping_type": w.scraping_type,
            "last_checked": w.last_checked,
            "scrape_interval": w.scrape_interval,
            "last_link_count": w.get_last_link_count(),
        }
        for w in websites
    ]

    return websites

def update_website(id):
    try:
        website = db.session.get(Website, id)
        if website:
            url = website.url
            plugin_name = website.plugin_name

        if not website:
            return "Website not found"

        scrape_result = scrape_website(url, plugin_name)

        if scrape_result:
            if website.scraping_type == 'hash':

                if "html_hash" in scrape_result.keys():
                    before_hash = db.session.query(Hash).filter(Hash.id == website.id).first()
                    after_hash = scrape_result["html_hash"]

                    if before_hash is None:
                        result = f"New site: hash generated"
                        new_hash = Hash(website_id=website.id, last_hash=after_hash)
                        db.session.add(new_hash)

                    elif before_hash.last_hash != after_hash:
                        result = f"Update detected: site hash changed"
                        before_hash.last_hash = after_hash

                        subject = f"Update from site {url}"
                        body = f"{url} site was updated (new hash: {after_hash})"
                        send_email(subject, body)
                    else:
                        result = "Same hash as before: no site update"
                else:
                    result = "Wrong plugin type"

            elif website.scraping_type == 'links':
                current_link_count = scrape_result["link_count"]
                current_links_with_descriptions = scrape_result["links_with_descriptions"]

                db_links = db.session.query(Link).filter(Link.website_id == website.id).all()
                existing_links = set([db_link.link for db_link in db_links])

                new_links_with_descriptions = [
                    link for link in current_links_with_descriptions
                    if link[0] not in existing_links
                ]

                if new_links_with_descriptions:
                    result = f"Update detected: {len(new_links_with_descriptions)} new links found"

                    for link, description in new_links_with_descriptions:
                        new_link = Link(website_id=website.id, link=link, description=description)
                        db.session.add(new_link)

                    link_counts = db.session.query(LinkCounts).filter(LinkCounts.website_id == website.id).first()
                    if link_counts is None:
                        new_link_counts = LinkCounts(website_id=website.id, last_link_count=current_link_count)
                        db.session.add(new_link_counts)
                    else:
                        link_counts.last_link_count = current_link_count

                    subject = f"New links detected on {url}"
                    body = "The following new links were found:\n\n" + "\n".join(
                        [f"{link[0]} - {link[1]}" for link in new_links_with_descriptions]
                    )
                    send_email(subject, body)

                else:
                    result = "No new links found"

            website.last_checked = db.func.now()
            db.session.commit()

        else:
            result = "Scraping failed"

    except SQLAlchemyError as e:
        db.session.rollback()
        result = f"Database error: {str(e)}"

    return result


def update_interval(id, interval):
    website = db.session.get(Website, id)
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


def add_custom_website(name, url):

    plugin_name = f"hash_{name.replace(' ', '_').lower()}"
    new_website = Website(
        name=name,
        url=url,
        plugin_name=plugin_name,
        scraping_type="hash",
        scrape_interval="never",
    )
    db.session.add(new_website)
    db.session.commit()
    
# Create a plugin file for the custom website
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


def delete_custom_website(id):
    website = db.session.get(Website, id)
    if website:
        db.session.delete(website)
        db.session.commit()
        
        # Delete the corresponding plugin file
        plugin_name = website.plugin_name
        if os.path.exists(f"plugins/{plugin_name}.py"):
            os.remove(f"plugins/{plugin_name}.py")
            
            return f"Custom website {website.name} deleted successfully"
    return "Website not found"

def add_uploaded_scraper(filename):
    try:
        # Load the module
        module_name = filename[:-3]  # Remove .py extension
        spec = importlib.util.spec_from_file_location(module_name, os.path.join('plugins', filename))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if the required attributes exist
        if not all(hasattr(module, attr) for attr in ['WEBSITE_NAME', 'WEBSITE_URL', 'scrape']):
            raise AttributeError("The uploaded scraper is missing required attributes")
        
        # Add the website to the database
        new_website = Website(
            name=module.WEBSITE_NAME,
            url=module.WEBSITE_URL,
            plugin_name=module_name,
            scrape_interval='never'
        )
        db.session.add(new_website)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error adding uploaded scraper: {e}")
        db.session.rollback()
        return False

def update_last_checked(id):
    try:
        website = db.session.get(Website, id)
        if website:
            website.last_checked = datetime.now()
            db.session.commit()
            return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating last checked time: {e}")
    return False
