#!/bin/bash

mkdir -p wheels

docker run --rm \
    --platform linux/amd64 \
    -v $(pwd):/build \
    python:3.7-slim \
    bash -c "
        set -e
        echo '>>> System info:'
        uname -m
        python3 --version

        echo '>>> Downloading psycopg2 deps...'
        apt-get update && apt-get -y install libpq-dev gcc

        echo '>>> Upgrading pip...'
        pip install --upgrade pip wheel setuptools

        echo '>>> Downloading wheels for Linux x86_64 / Python 3.7 ...'
        pip wheel --wheel-dir=/build/wheels \
                  --prefer-binary \
                  -r /build/requirements.txt
                  
        pip wheel --wheel-dir=/build/wheels pip setuptools wheel
        
        echo '>>> Done!'
    "

