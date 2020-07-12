from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import re
import random
import string
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(), unique=True, nullable=False)
    random_text = db.Column(db.String(6), unique=True, nullable=False)
    exp_date = db.Column(
        db.DateTime, default=datetime.strptime("2212-12-12", "%Y-%m-%d")
    )
    # exp_date = db.Column(db.DateTime, nullable=False, default=datetime(2212,12,12))

    def __repr__(self):
        return f"Urls('{self.long_url}', '{self.random_text}', '{self.exp_date}' )"


def url_validator(url):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port,
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, url) is not None


def random_word():
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(random.choice(letters) for i in range(6))


def short_out(random_text):
    return f"https://koojelink/{random_text}"

def long_url_exist(Urls, l_url):
    return Urls.query.filter_by(long_url=l_url).first()

def get_random_text(l_url_query):
    return l_url_query.random_text if l_url_query is not None else None

def random_text_exist(Urls, random_text):
    return Urls.query.filter_by(random_text=random_text).first()


def search_for_url(Urls, random_text):
    match = random_text_exist(Urls, random_text)
    if match:
        if match.exp_date >= datetime.now():
            return True, match.long_url
        else:
            return False, match.exp_date
    else:
        return None, None



def get_exp(exp_date):
    if exp_date is None:
        return datetime.strptime("2212-12-12", "%Y-%m-%d")
    else:
        return datetime.strptime(exp_date, "%Y-%m-%d")

def add_url_to_db(l_url, s_url, exp_date):
    new_url = Urls(
        long_url=l_url,
        random_text=s_url.split("k/")[1],
        exp_date=get_exp(exp_date),
    )
    db.session.add(new_url)
    db.session.commit()


def validate_time_format(date_text):
    try:
        if date_text is None:
            return True
        else:
            if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y-%m-%d"):
                raise ValueError
            return True
    except ValueError:
        return False


def recreate_random_word():
    while(True):
        r_txt = random_word()
        if random_text_exist(Urls, r_txt) is None:
            break
    return short_out(r_txt)

@app.route("/", methods=["GET", "POST"])
def handle_post_request():
    if request.method == "POST":
        req_data = request.get_json()
        long_url = req_data.get("long_url")
        exp_date = req_data.get("exp_date")
        if url_validator(long_url):
            l_exist = long_url_exist(Urls, long_url)
            if l_exist is None:
                output_url = recreate_random_word()
                if validate_time_format(exp_date):
                    add_url_to_db(long_url, output_url, exp_date)
                    return f"{output_url}"
                else:
                    return "Incorrect data format, should be YYYY-MM-DD"
            else:
                return f"{short_out(get_random_text(l_exist))}"


        else:
            return jsonify({"error": "wrong key:value input"})
    else:
        return jsonify({"message": "Welcome to koojelink!"})


@app.route("/koojelink/<string:random_text>")
def redirect_to_origin(random_text):
    origin = search_for_url(Urls, random_text)
    if origin[0]:
        return redirect(origin)
    elif origin[0] == False:
        return f"""
        <div style='text-align: center;'>
            <h1>Short link has been expired {origin[1]}</h1>
            <h3>Please retry with a new short link.</h3>
        </div>
        """
    elif origin[0] == None:
        return """
        <div style="text-align: center;">
            <h1>Pages does not found (Error 404).</h1>
            <h3>Please retry with correct short link.</h3>
        </div>
        """
        # return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)
    # manager.run()
