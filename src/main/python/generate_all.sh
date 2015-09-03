#!/bin/bash
./setup.sh
python generate_all.py --destination_dir=$1 --geoserver="$2"
