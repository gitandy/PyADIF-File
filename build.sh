#!/bin/bash

echo "Get version info..."
VERSION=$(git describe --tags)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" = "master" ]; then BRANCH=""; fi
STATUS=$(git status -s -uno --porcelain)
if [ -z "$STATUS" ]; then UNCLEAN="False"; else UNCLEAN="True"; fi
echo "__version__ = '$VERSION'" > src/adif_file/__version__.py
echo "__branch__ = '$BRANCH'" >> src/adif_file/__version__.py
echo "__unclean__ = $UNCLEAN" >> src/adif_file/__version__.py
echo "Version: $VERSION $BRANCH $UNCLEAN"

source ./venv/bin/activate

echo
echo "Build package..."
python -m pip install --upgrade build
python -m build
echo "...Done!"
