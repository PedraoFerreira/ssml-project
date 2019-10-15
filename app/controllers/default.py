from app import app, APP_ROOT
import os
from flask import render_template, request, send_from_directory
import boto3
import uuid
import requests as req

@app.route("/")
def index():
    return render_template("index.html")


def exec_ml(file_name, pred_col, model_type):
    body = {
        "s3bucket": {
            "origin": "user-data-upload",
            "output": "user-data-upload-output"
        },
        "file": {
            "name": file_name,
            "extension": "csv",
            "delimiter": ","
        },
        "pred_col": pred_col,
        "model_type": model_type
    }
    result = req.post(app.config['URL_LAMBDA_ML'], json=body)

    return result.status_code == 200

@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, '.temp')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    session = boto3.Session(profile_name='default')
    s3_client = session.client('s3')

    for file in request.files.getlist("file"):
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        destination = "/".join([target, filename])

    model_type = request.form['modeltype']
    pred_col = request.form['predcol']

    if filename:
        try:
            file.save(destination)
            s3_client.upload_file(destination, 'user-data-upload', filename)
        finally:
            os.remove(destination)

        if exec_ml(filename, pred_col, model_type):
            try:
                s3_client.download_file('user-data-upload-output', filename, destination)
                return send_from_directory(directory=target, filename=filename)
            finally:
                os.remove(destination)

    return render_template("complete.html")