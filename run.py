from flask import Flask, request, jsonify, redirect
import re
import random
import string
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

urls = []


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


# without database
def search_for_url(all_urls, random_text):
    for url in all_urls:
        if url[1]["short_url"].split("k/")[1] == random_text:
            return url[0]["long_url"]

    # just for test, it should change !
    return "https://www.manutd.com"


@app.route("/", methods=["GET", "POST"])
def handle_post_request():
    if request.method == "POST":
        input_url = {"long_url": request.json["long_url"]}
        if url_validator(input_url.get("long_url")):
            output_url = {"short_url": short_out(random_word())}
            urls.append([input_url, output_url])
            # return jsonify({'urls':urls})
            return output_url.get("short_url")
        else:
            return jsonify({"error": "wrong key:value input"})
    else:
        return jsonify({"message": "Welcome to koojelink!"})


@app.route("/koojelink/<string:random_text>")
def redirect_to_origin(random_text):
    return redirect(search_for_url(urls, random_text))


if __name__ == "__main__":
    app.run(debug=True)
