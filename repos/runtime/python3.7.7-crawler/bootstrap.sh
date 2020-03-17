#!/bin/bash
#
# docker image installation script

# install python library
echo "[Bootstrap] install requests, beautifulsoup4"
pip install --upgrade pip --no-cache-dir
pip install requests==${PYTHON_REQUESTS_VERSION} --no-cache-dir
pip install beautifulsoup4==${PYTHON_BEAUTIFULSOUP_VERSION} --no-cache-dir
