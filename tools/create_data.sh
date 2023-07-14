#!/usr/bin/env bash

set -x
export PYTHONPATH=`pwd`:$PYTHONPATH

DATASET=$1
VERSION=$2
MAX_SWEEPS=$3

python -u tools/create_data.py ${DATASET} \
        --version ${VERSION}\
        --root-path ./data/${DATASET} \
        --out-dir ./data/${DATASET} \
        --extra-tag ${DATASET} \
        --max-sweeps ${MAX_SWEEPS}
