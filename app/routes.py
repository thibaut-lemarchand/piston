from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from .models import (
    get_websites,
    toggle_website,
    manual_scrape,
    update_interval,
    add_custom_website,
    delete_custom_website,
)

app = Blueprint("routes", __name__)


@app.route("/")
def index():
    websites = get_websites()
    return render_template("index.html", websites=websites)


@app.route("/toggle/<int:id>")
def toggle(id):
    toggle_website(id)
    return redirect(url_for("routes.index"))


@app.route("/scrape/<path:id>")
def scrape(id):
    result = manual_scrape(id)
    return jsonify({"result": result})


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
