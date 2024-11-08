from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import string
import random
import validators
from datetime import datetime
from dotenv import load_dotenv
import os
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///url_shortener.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    video_origin = db.Column(db.String(256), nullable=True)


def generate_short_id(num_chars=6):
    while True:
        short_id = "".join(
            random.choices(string.ascii_letters + string.digits, k=num_chars)
        )
        if not URLMap.query.filter_by(short_id=short_id).first():
            return short_id


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form.get("original_url")
        custom_code = request.form.get("custom_code")
        video_origin = request.form.get("video_origin")

        # Validate the original URL
        if not original_url or not validators.url(original_url):
            flash("Please enter a valid URL.", "danger")
            return redirect(url_for("index"))

        # Handle custom code
        if custom_code:
            if URLMap.query.filter_by(short_id=custom_code).first():
                flash(
                    "Custom code already in use. Please choose another one.", "danger"
                )
                return redirect(url_for("index"))
            short_id = custom_code
        else:
            short_id = generate_short_id()

        # Create a new URL mapping
        new_url = URLMap(
            original_url=original_url, short_id=short_id, video_origin=video_origin
        )
        db.session.add(new_url)
        db.session.commit()

        # Use short_id directly
        short_url = short_id
        return render_template("index.html", short_url=short_url)

    return render_template("index.html")


@app.route("/<short_id>")
def redirect_to_url(short_id):
    url_data = URLMap.query.filter_by(short_id=short_id).first()
    if url_data:
        url_data.clicks += 1
        db.session.commit()
        return redirect(url_data.original_url)
    else:
        flash("Invalid or expired URL.", "danger")
        return redirect(url_for("index"))


@app.route("/stats", methods=["GET"])
def stats():
    # Get sorting parameters
    sort = request.args.get("sort", "date_created")
    order = request.args.get("order", "desc")
    search = request.args.get("search", "")

    # Map sort parameter to model attribute
    sort_options = {
        "original_url": URLMap.original_url,
        "short_id": URLMap.short_id,
        "clicks": URLMap.clicks,
        "date_created": URLMap.date_created,
        "video_origin": URLMap.video_origin,
    }
    sort_attr = sort_options.get(sort, URLMap.date_created)

    # Apply ordering
    if order == "desc":
        sort_attr = sort_attr.desc()
        order_toggle = "asc"
    else:
        sort_attr = sort_attr.asc()
        order_toggle = "desc"

    # Apply search filter
    query = URLMap.query
    if search:
        query = query.filter(
            URLMap.original_url.ilike(f"%{search}%")
            | URLMap.video_origin.ilike(f"%{search}%")
        )

    # Pagination
    page = request.args.get("page", 1, type=int)
    urls = query.order_by(sort_attr).paginate(page=page, per_page=10)

    return render_template(
        "stats.html", urls=urls, sort=sort, order=order_toggle, search=search
    )


@app.route("/delete/<int:url_id>", methods=["POST"])
def delete_url(url_id):
    url_data = URLMap.query.get_or_404(url_id)
    db.session.delete(url_data)
    db.session.commit()
    flash("URL has been deleted successfully.", "success")
    return redirect(url_for("stats"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0")
