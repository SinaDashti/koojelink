from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import random
import string
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(), unique=True, nullable=False)
    random_text = db.Column(db.String(6), unique=True, nullable=False)
    # exp_date = db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return f"Urls('{self.long_url}', '{self.random_text}')"


def url_validator(url):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, url) is not None


def random_word():
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(random.choice(letters) for i in range(6))


def short_out(random_text):
    return f"https://koojelink/{random_text}"


def search_for_url(Urls, random_text):
    match = Urls.query.filter_by(random_text=random_text).first()
    if match:
        return match.long_url
    return False


@app.route("/", methods=["GET", "POST"])
def handle_post_request():
    if request.method == "POST":
        input_url = {"long_url": request.json["long_url"]}
        if url_validator(input_url.get("long_url")):
            output_url = {"short_url": short_out(random_word())}
            new_url = Urls(
                long_url=input_url.get("long_url"),
                random_text=output_url.get("short_url").split("k/")[1],
            )
            db.session.add(new_url)
            db.session.commit()
            return output_url.get("short_url")
        else:
            return jsonify({"error": "wrong key:value input"})
    else:
        return jsonify({"message": "Welcome to koojelink!"})


@app.route("/koojelink/<string:random_text>")
def redirect_to_origin(random_text):
    origin = search_for_url(Urls, random_text)
    if origin:
        return redirect(origin)
    else:
        return """
        <div style="text-align: center;">
            <h1>Pages does not found (Error 404).</h1>
            <h3>Please retry with correct short link.</h3>
        </div>
        """
        # return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
