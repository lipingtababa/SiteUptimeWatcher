from flask import Flask, make_response
from random import random


app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handle(**kwargs):
    if random() < 0.1:
        return make_response("SERVER ERROR", 500)
    elif random() < 0.2:
        return make_response("NOT FOUND", 404)
    else:
        return 'You are always welcome!'

if __name__ == '__main__':
    app.run(debug=False, port=9876)
