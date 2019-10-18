#!/bin/sh

set -e

cd ~/workspace/noisycols/
./generate.py output_$(date +%s).png
