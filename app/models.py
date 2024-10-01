import os
import sqlite3
from datetime import datetime
from .utils import adapt_datetime, convert_datetime, scrape_website, send_email
from . import create_app

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


def init_db():
    with sqlite3.connect("websites.db", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS websites
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      url TEXT NOT NULL,
                      plugin_name TEXT NOT NULL,
                      is_enabled INTEGER NOT NULL,
                      last_link_count INTEGER,
                      last_checked DATETIME,
                      scrape_interval TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS links
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      website_id INTEGER,
                      link TEXT NOT NULL,
                      description TEXT,
                      FOREIGN KEY (website_id) REFERENCES websites (id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS custom_websites
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      url TEXT NOT NULL,
                      last_hash TEXT,
                      last_checked DATETIME,
                      scrape_interval TEXT,
                      is_ui_generated INTEGER NOT NULL DEFAULT 0)""")
        conn.commit()


def get_websites():
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, name, url, plugin_name, is_enabled, last_link_count, last_checked, scrape_interval FROM websites"
        )
        regular_websites = [
            {
                "id": row[0],
                "name": row[1],
                "url": row[2],
                "plugin_name": row[3],
                "is_enabled": row[4],
                "last_link_count": row[5],
                "last_checked": row[6],
                "scrape_interval": row[7],
                "is_ui_generated": False,
            }
            for row in c.fetchall()
        ]

        c.execute(
            "SELECT id, name, url, last_hash, last_checked, scrape_interval, is_ui_generated FROM custom_websites"
        )
        custom_websites = [
            {
                "id": f"custom_{row[0]}",  # Prefix custom website IDs with 'custom_'
                "name": row[1],
                "url": row[2],
                "plugin_name": None,
                "is_enabled": None,
                "last_link_count": None,
                "last_checked": row[4],
                "scrape_interval": row[5],
                "is_ui_generated": row[6],
            }
            for row in c.fetchall()
        ]

        # Combine regular and custom websites
        websites = regular_websites + custom_websites

        return websites


def toggle_website(id):
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE websites SET is_enabled = 1 - is_enabled WHERE id = ?", (id,))
        conn.commit()


def manual_scrape(id):
    app = create_app()
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        if id.startswith("custom_"):
            c.execute(
                "SELECT url, name FROM custom_websites WHERE id = ?",
                (id.split("_")[1],),
            )
        else:
            c.execute("SELECT url, plugin_name FROM websites WHERE id = ?", (id,))
        website = c.fetchone()

        if website:
            if id.startswith("custom_"):
                url, plugin_name = website
                plugin_name = f"custom_{plugin_name}"
            else:
                url, plugin_name = website
        else:
            return "Website not found"

        scrape_result = scrape_website(url, plugin_name)

        if scrape_result:
            current_link_count = scrape_result["link_count"]
            current_links_with_descriptions = scrape_result["links_with_descriptions"]

            if plugin_name.startswith("custom_"):
                html_hash = scrape_result["html_hash"]

            c.execute("SELECT link FROM links WHERE website_id = ?", (id,))
            existing_links = set(link[0] for link in c.fetchall())

            new_links_with_descriptions = [
                link
                for link in current_links_with_descriptions
                if link[0] not in existing_links
            ]

            if new_links_with_descriptions:
                c.executemany(
                    "INSERT INTO links (website_id, link, description) VALUES (?, ?, ?)",
                    [(id, link[0], link[1]) for link in new_links_with_descriptions],
                )

                subject = f"New links detected on {url}"
                body = "The following new links were found:\n\n" + "\n".join(
                    [f"{link[0]} - {link[1]}" for link in new_links_with_descriptions]
                )
                send_email(subject, body, app)

                result = f"Update detected: {len(new_links_with_descriptions)} new links found"
            else:
                result = "No new links found"

            if plugin_name.startswith("custom_"):
                c.execute(
                    "UPDATE custom_websites SET last_hash = ?, last_checked = ? WHERE id = ?",
                    (html_hash, datetime.now(), id.split("_")[1]),
                )
            else:
                c.execute(
                    "UPDATE websites SET last_link_count = ?, last_checked = ? WHERE id = ?",
                    (current_link_count, datetime.now(), id),
                )
            conn.commit()
        else:
            result = "Scraping failed"

    return result


def update_interval(id, interval):
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        if id.startswith("custom_"):
            c.execute(
                "UPDATE custom_websites SET scrape_interval = ? WHERE id = ?",
                (interval, id.split("_")[1]),
            )
        else:
            c.execute(
                "UPDATE websites SET scrape_interval = ? WHERE id = ?", (interval, id)
            )
        conn.commit()
    return f"Scrape interval updated to {interval}"


def init_websites(websites_data):
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM websites")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO websites (name, url, plugin_name, is_enabled, scrape_interval) VALUES (?, ?, ?, ?, ?)",
                websites_data,
            )
            conn.commit()


def check_updates():
    app = create_app()
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, url, plugin_name, last_link_count, scrape_interval FROM websites WHERE is_enabled = 1 AND scrape_interval != 'never'"
        )
        websites = c.fetchall()

        for website in websites:
            id, url, plugin_name, last_link_count, scrape_interval = website
            scrape_result = scrape_website(url, plugin_name)

            if scrape_result:
                current_link_count = scrape_result["link_count"]
                current_links_with_descriptions = scrape_result[
                    "links_with_descriptions"
                ]

                c.execute("SELECT link FROM links WHERE website_id = ?", (id,))
                existing_links = set(link[0] for link in c.fetchall())

                new_links_with_descriptions = [
                    link
                    for link in current_links_with_descriptions
                    if link[0] not in existing_links
                ]

                if new_links_with_descriptions:
                    c.executemany(
                        "INSERT INTO links (website_id, link, description) VALUES (?, ?, ?)",
                        [
                            (id, link[0], link[1])
                            for link in new_links_with_descriptions
                        ],
                    )

                    subject = f"New links detected on {url}"
                    body = "The following new links were found:\n\n" + "\n".join(
                        [
                            f"{link[0]} - {link[1]}"
                            for link in new_links_with_descriptions
                        ]
                    )
                    send_email(subject, body, app)

                c.execute(
                    "UPDATE websites SET last_link_count = ?, last_checked = ? WHERE id = ?",
                    (current_link_count, datetime.now(), id),
                )

        conn.commit()


def add_custom_website(name, url):
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO custom_websites (name, url, last_hash, scrape_interval, is_ui_generated) VALUES (?, ?, ?, ?, ?)",
            (name, url, None, "never", 1),
        )
        conn.commit()

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
        f.write(plugin_content)

    return f"Custom website {name} added successfully"


def check_custom_updates():
    app = create_app()
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, url, last_hash, scrape_interval FROM custom_websites WHERE scrape_interval != 'never'"
        )
        websites = c.fetchall()

        for website in websites:
            id, url, last_hash, scrape_interval = website
            plugin_name = f"custom_{url.replace(' ', '_')}"
            scrape_result = scrape_website(url, plugin_name)

            if scrape_result:
                current_hash = scrape_result["html_hash"]

                if current_hash != last_hash:
                    subject = f"Update detected on {url}"
                    body = "The website content has changed."
                    send_email(subject, body, app)

                    c.execute(
                        "UPDATE custom_websites SET last_hash = ?, last_checked = ? WHERE id = ?",
                        (current_hash, datetime.now(), id),
                    )

        conn.commit()


def delete_custom_website(id):
    with sqlite3.connect("websites.db") as conn:
        c = conn.cursor()
        if id.startswith("custom_"):
            c.execute(
                "SELECT name, is_ui_generated FROM custom_websites WHERE id = ?",
                (id.split("_")[1],),
            )
        else:
            return "Invalid custom website ID"

        website = c.fetchone()

        if website:
            name, is_ui_generated = website
            if is_ui_generated:
                c.execute(
                    "DELETE FROM custom_websites WHERE id = ?", (id.split("_")[1],)
                )
                conn.commit()

                # Delete the corresponding plugin file
                plugin_name = f"custom_{name.replace(' ', '_')}"
                if os.path.exists(f"plugins/{plugin_name}.py"):
                    os.remove(f"plugins/{plugin_name}.py")

                return f"Custom website {name} deleted successfully"
            else:
                return "Cannot delete manually created plugin"
        else:
            return "Website not found"
