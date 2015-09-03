#!/bin/bash
PREFIX="generate_all.sh:"
echo "$PREFIX Creating virtualenv for project"
virtualenv --no-site-packages --python=python2.7 env
echo "$PREFIX Installing project's python dependencies"
. env/bin/activate
pip install -r requirements.txt
python generate_all.py --destination_dir=$1 --geoserver="$2"
