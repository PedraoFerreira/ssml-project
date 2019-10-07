#!/bin/bash

export PKG_DIR="python/lib/python3.6/site-packages"

sudo rm -f my-Python36-DtScience.zip

sudo rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}

docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.6 \
    pip3 install -r requirements.txt --no-deps -t ${PKG_DIR}

zip -r my-Python36-DtScience.zip python/

sudo rm -rf python