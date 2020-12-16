#!/usr/bin/env bash

pip install --upgrade setuptools wheel twine
rm -rf build/
rm -rf dist/
python setup.py sdist bdist_wheel
#twine upload dist/*
