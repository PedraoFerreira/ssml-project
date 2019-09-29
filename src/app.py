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
    target = os.path.join(APP_ROOT, 'uploads/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)

    ## Colocar credenciar na SESSAO DO OS ou CRIAR ARQUIVOS NO OS
    s3_client = boto3.client('s3',
                             aws_access_key_id='AKIASDY73AT2L2NHAWH6',
                             aws_secret_access_key='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'
                             )

    s3filename = uuid.uuid4()

    s3_client.upload_file(destination, '', s3filename)

    return render_template("complete.html")


if __name__ == "__main__":
    app.run(port=4555, debug=True)