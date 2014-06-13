#!/bin/bash

set +eux

# Use virtualenv (see ./prep.sh).
source PYTHON_ENV/bin/activate

# Prepare dependencies.
cp Info.plist goog.docset/Contents/.
cp goog.docset/Contents/Resources/Documents/api/static/images/16px.png \
    goog.docset/icon.png

# Generate docset.
python gendocset.py

echo "Done.  Type

    open goog.docset

to open this docset in Dash.
"
