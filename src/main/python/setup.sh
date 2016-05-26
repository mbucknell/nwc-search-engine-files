#!/bin/bash
$VIRTUALENV --no-site-packages --python=python2.7 env
. env/bin/activate
pip install -r requirements.txt
