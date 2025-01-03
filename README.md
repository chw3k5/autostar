Autostar has evolved into https://github.com/HypatiaOrg/HySite/tree/main/backend/hypatia/sources

Autostar was too difficult to maintain as a gernallized tool that operted only with CSV files and Python that was both used by [SpExoDisks.com](spexodisks.com) and [HypatiaCatalog.com](hypatiacatalog.com). 
Each orgainiation now maintains it own tooling, and its own database, [MySQL](https://www.mysql.com/) for SpExoDisks and [MongoDB](https://www.mongodb.com/) for HypatiaCatalog.
We no long recommend wrting (CSV) files for intermidaiate database and processing steps, 
we now write everything to a single database that can house all intermidiate and final data products.
This greately simpliifes the number of systems to learn and maintain administrative operations.

Read more in the SpExoDisks paper **Database Design for SpExoDisks: A Database & Web Portal for Spectra of Exoplanet-Forming Disks** [PASP](https://iopscience.iop.org/article/10.1088/1538-3873/ad917d), [arXiv](https://arxiv.org/abs/2411.13308)

The Hypatia Codebase: https://github.com/HypatiaOrg/HySite
The SpExoDisks Codebase: https://github.com/spexod/Portal

## Preface

A group of functions written to query and record data from various 
astronomical websites.

It is meant to save the user's (and the queried website's) time by
creating a local database and updating it with queries from other 
astronomy websites/databases.

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
