## Preface

A group of functions written to query and record data from various 
astronomical websites.

It is meant to save the user's (and the queried website's) time by
localing at the local library created from previous queries first 
before querying the websites. 

This is an important step in making a script automatically updates any data.

# Installation

## Python
It should be written to work with everything greater than Python 3.7,
so treat yourself to the latest version of Python.

https://www.python.org/downloads/

### Test Python installation from the terminal/shell/command-line
    python --version

To make sure you are using python 3.7 or greater. You me need python3 on you system.
    python3 --version

## Install a virtual environment (recommended)
    python -m venv venv

This way you can keep your system python clean and not have to worry about
what we install here. Just delete the venv folder when you are done. As
a bonus, after activation you can use `python` instead of `python3` in the terminal.

### Activate the virtual environment (linux/mac)
    source venv/bin/activate

### Activate the virtual environment (windows)
    venv\Scripts\activate.bat

## from this repository, run
    pip install .

## from PyPI, run
    pip install autostar
