from app import app, APP_ROOT
import os
from flask import render_template, request, send_from_directory
import boto3
import uuid
import requests as req

@app.route("/")
def index():
    return render_template("index.html")


def detect_delimiter(csv_file):
    with open(csv_file, 'r') as file:
        header = file.readline()
        if header.find(";") != -1:
            return ";"
        if header.find(",") != -1:
            return ","
    return ";"

def exec_ml(file_name, pred_col, model_type, extension, delimiter):
    body = {
        "s3bucket": {
            "origin": app.config['S3_USER_DATA_BUCKET_INPUT'],
            "output": app.config['S3_USER_DATA_BUCKET_OUTPUT']
        },
        "file": {
            "name": file_name,
            "extension": extension,
            "delimiter": delimiter
        },
        "pred_col": pred_col,
        "model_type": model_type
    }
    result = req.post(app.config['URL_LAMBDA_ML'], json=body)

    score = 0.0

    if result.status_code == 200:
        score = result.json()['Score'] * 100

    return result.status_code == 200, score


@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, '.temp')

    if not os.path.isdir(target):
        os.mkdir(target)

    session = boto3.Session(profile_name='default')
    s3_client = session.client('s3')

    for file in request.files.getlist("file"):
        processed_filename = 'ssml_{}'.format(file.filename)
        extension = os.path.splitext(file.filename)[1].replace('.','')
        filename = '{}.{}'.format(str(uuid.uuid4()),extension)
        destination = "/".join([target, filename])

    model_type = request.form['modeltype']
    pred_col = request.form['predcol']

    if filename:
        try:
            file.save(destination)
            delimiter = detect_delimiter(destination)
            s3_client.upload_file(destination, app.config['S3_USER_DATA_BUCKET_INPUT'], filename)
        finally:
            os.remove(destination)

        success, accuracy_score = exec_ml(filename, pred_col, model_type, extension, delimiter)

        if success:
            try:
                s3_client.download_file(app.config['S3_USER_DATA_BUCKET_OUTPUT'], filename, destination)
                return send_from_directory(directory=target, filename=filename, as_attachment=True, attachment_filename=processed_filename)
            finally:
                os.remove(destination)

    return render_template("complete.html")