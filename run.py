from flask import Flask, request, jsonify
from urllib.parse import urlparse
import random
import string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

urls = []

def url_validator(url):
    result = urlparse(url)
    return all([result.scheme, result.netloc, result.path])

def randomword():
   letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
   return ''.join(random.choice(letters) for i in range(6))

def short_out(random_text):
    return f'https://Koojilink/{random_text}'


@app.route('/', methods=['GET', 'POST'])
def test_post():

    if request.method == 'POST':
        input_url = {'long_url':request.json['long_url']}
        if url_validator(input_url.get('long_url')):
            output_url = {'short_url':short_out(randomword())}
            urls.append([input_url, output_url])
            # return jsonify({'urls':urls})
            return output_url.get('short_url')
        else:
            return 'error'
    else:
        return jsonify({'message':'It works !!!'})

if __name__ == '__main__':
    app.run(debug = True)
