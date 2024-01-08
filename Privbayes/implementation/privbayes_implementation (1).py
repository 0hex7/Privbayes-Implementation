# -*- coding: utf-8 -*-
"""Privbayes-implementation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lg_2rgXjz10igkeC5nu78v5jG0RO7ZO-
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /

# Commented out IPython magic to ensure Python compatibility.
# %ls

import os

!pip install autograd

#!pip install scikit-glpk

!pip install pyomo
!pyomo solve abstract1.py abstract1.dat --solver=glpk

pip install swig cython pandas

# Commented out IPython magic to ensure Python compatibility.
#%rm -rf /ektelo/
# %cd /

!git clone https://github.com/0hex7/ektelo.git

# Set the HOME environment variable to root directory '/'
os.environ['HOME'] = '/'

# Define environment variables
os.environ['EKTELO_HOME'] = '/ektelo'
os.environ['EKTELO_DATA'] = '/tmp/ektelo'
os.environ['PYTHON_HOME'] = '/PyEktelo'
os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':/ektelo'
os.environ['EKTELO_LOG_PATH'] = '/logs'
os.environ['EKTELO_LOG_LEVEL'] = 'DEBUG'

# Retrieve and create directories
ektelo_home = os.getenv('EKTELO_HOME')
ektelo_data = os.getenv('EKTELO_DATA')
python_home = os.getenv('PYTHON_HOME')
pythonpath = os.getenv('PYTHONPATH')
ektelo_log_path = os.getenv('EKTELO_LOG_PATH')
ektelo_log_level = os.getenv('EKTELO_LOG_LEVEL')

directories = [ektelo_home, ektelo_data, python_home, pythonpath, ektelo_log_path, ektelo_log_level]

for directory in directories:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory '{directory}' created successfully.")
    except OSError as error:
        print(f"Directory creation failed for '{directory}': {error}")

!sudo apt-get install gfortran liblapack-dev libblas-dev
!sudo apt-get install libpq-dev python3-dev libncurses5-dev swig glpk

print(f"EKTELO_HOME: {ektelo_home}")
print(f"EKTELO_DATA: {ektelo_data}")
print(f"PYTHON_HOME: {python_home}")
print(f"PYTHONPATH: {pythonpath}")
print(f"EKTELO_LOG_PATH: {ektelo_log_path}")
print(f"EKTELO_LOG_LEVEL: {ektelo_log_level}")

pwd

#ektelo_home = os.getenv('EKTELO_HOME')
#%cd $ektelo_home

cd /

# Commented out IPython magic to ensure Python compatibility.
!python3 -m venv $python_home
!source $python_home/bin/activate
# %cd $ektelo_home
!pip install -r resources/requirements.txt

# Commented out IPython magic to ensure Python compatibility.
# %mkdir -p $ektelo_data
!curl -k https://www.dpcomp.org/data/cps.csv > $ektelo_data/cps.csv
!curl -k https://www.dpcomp.org/data/stroke.csv > $ektelo_data/stroke.csv

# Commented out IPython magic to ensure Python compatibility.
# %cd $ektelo_home/ektelo/algorithm
!./setup.sh

# Commented out IPython magic to ensure Python compatibility.
# %cd $ektelo_home/ektelo/algorithm
# %ls
# %cd ahp
!./setup.sh

# Commented out IPython magic to ensure Python compatibility.
# %cd $ektelo_home/ektelo/algorithm
#%pwd
# %ls
# %cd privBayes/
#%ls
!./setup.sh

# Commented out IPython magic to ensure Python compatibility.
# %pwd
!source $python_home/bin/activate

!cd $ektelo_home
!nosetests

# Commented out IPython magic to ensure Python compatibility.
# %cd /

rm -rf privbayes-implementation/

!git clone https://github.com/0hex7/privbayes-implementation.git

# Commented out IPython magic to ensure Python compatibility.
# %cd privbayes-implementation/

!python3 setup.py install
!pip install kaleido python-multipart uvicorn fastapi
!pip install numpy pillow

# Commented out IPython magic to ensure Python compatibility.
# %pwd
# %cd /privbayes-implementation/Privbayes/
# %ls
# %cd data/
# %ls
# %cd ../code/

!python privbayes.py

from IPython.display import Image

Image(filename='/privbayes-implementation/Privbayes/data/graphs/comparision_graph_adult.png')

"""================================================   THE -END=========================================================





"""