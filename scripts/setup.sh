#!/usr/bin/env bash
set -e

python -m pip install --upgrade --no-cache-dir pip

cd /opt/app/dist || exit 1

wheel_package=$(find . -name "*.whl" -print -quit)

pip install -U --no-cache-dir --quiet "$wheel_package"
pip cache purge
