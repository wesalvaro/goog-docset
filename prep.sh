#!/bin/bash

set +eux

# Prepare virtualenv environment.
virtualenv PYTHON_ENV
source PYTHON_ENV/bin/activate

# Ensure BeautifulSoup 4 and lxml are available.
pip install beautifulsoup4 lxml

# Checkout docs submodule.
git submodule update --init goog.docset/Contents/Resources/Documents
