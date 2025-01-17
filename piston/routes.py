import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from werkzeug.utils import secure_filename
from piston.models import (
    Website,
    get_websites,
    update_website,
    update_interval,
    add_custom_website,
    delete_custom_website,
    add_uploaded_scraper,
)

app = Blueprint("routes", __name__)


@app.route("/")
def index():
    websites = get_websites()
    return render_template("index.html", websites=websites)


@app.route("/scrape/<path:id>")
def scrape(id):
    result = update_website(id)
    return jsonify({"result": result})

@app.route('/scrape/<id>')
def update_website_route(id):
    result = update_website(id)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"result": result, "last_checked": current_time})

@app.route("/update_interval/<path:id>", methods=["POST"])
def update(id):
    interval = request.json.get("interval")
    if interval:
        result = update_interval(id, interval)
        return jsonify({"result": result})
    else:
        return jsonify({"result": "Invalid interval"}), 400


@app.route("/add_custom_website", methods=["POST"])
def add_custom_website_route():
    name = request.json.get("name")
    url = request.json.get("url")
    if name and url:
        result = add_custom_website(name, url)
        return jsonify({"result": result})
    else:
        return jsonify({"result": "Invalid name or URL"}), 400


@app.route("/delete_custom_website/<path:id>", methods=["DELETE"])
def delete_custom_website_route(id):
    result = delete_custom_website(id)
    return jsonify({"result": result})

@app.route("/upload_scraper", methods=["POST"])
def upload_scraper():
    if 'scraperFile' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['scraperFile']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file and file.filename.endswith('.py'):
        filename = secure_filename(file.filename)
        file_path = os.path.join('plugins', filename)
        file.save(file_path)
        
        # Add the uploaded scraper to the database
        result = add_uploaded_scraper(filename)
        
        if result:
            return jsonify({"message": "Scraper uploaded successfully"}), 200
        else:
            os.remove(file_path)  # Remove the file if it couldn't be added to the database
            return jsonify({"message": "Failed to add scraper to database"}), 500
    else:
        return jsonify({"message": "Invalid file type. Only .py files are allowed."}), 400

@app.route('/fetch_updated_data')
def fetch_updated_data():
    updated_websites = get_websites()
    return jsonify(updated_websites)
