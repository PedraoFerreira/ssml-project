import os
from flask import Flask, render_template, request
import boto3
import uuid

__author__ = 'ssml'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'uploads')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    session = boto3.Session(profile_name='default')
    s3_client = session.client('s3')

    for file in request.files.getlist("file"):
        filename =  str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        destination = "/".join([target, filename])
        try:
            file.save(destination)
            s3_client.upload_file(destination, 'user-data-upload', filename)
        finally:
            os.remove(destination)

    return render_template("complete.html")

if __name__ == "__main__":
    app.run(port=4555, debug=True)