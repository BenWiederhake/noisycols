#!/bin/sh

set -e

cd "$(dirname $0)"
./generate.py output_$(date +%s).png
