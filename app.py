from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string
import random
import validators
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with your own secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///url_shortener.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


def generate_short_id(num_chars=6):
    """Generate a random string of letters and digits."""
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

        if not original_url or not validators.url(original_url):
            flash("Please enter a valid URL.", "danger")
            return redirect(url_for("index"))

        if custom_code:
            if URLMap.query.filter_by(short_id=custom_code).first():
                flash(
                    "Custom code already in use. Please choose another one.", "danger"
                )
                return redirect(url_for("index"))
            short_id = custom_code
        else:
            short_id = generate_short_id()

        new_url = URLMap(original_url=original_url, short_id=short_id)
        db.session.add(new_url)
        db.session.commit()

        short_url = request.host_url + short_id
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


@app.route("/stats")
def stats():
    urls = URLMap.query.order_by(URLMap.date_created.desc()).all()
    return render_template("stats.html", urls=urls)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
