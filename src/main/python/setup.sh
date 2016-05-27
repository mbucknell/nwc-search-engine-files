#!/bin/bash
if [ -z "$VIRTUALENV" ]; then
    export VIRTUALENV=virtualenv
fi
$VIRTUALENV --no-site-packages --python=python2.7 env
. env/bin/activate
pip install -r requirements.txt
