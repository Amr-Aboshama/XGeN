from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def test():

    return os.listdir()[0]