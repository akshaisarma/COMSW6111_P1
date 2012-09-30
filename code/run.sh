#!/bin/bash

# Author: Yuan Du (yd2234@columbia.edu)
# Date: Sep 24, 2012
# Function: test UI.py by given account key, precision and query
# Usage: ./run.sh <bing account key> <precision> <query>

# ACCOUNTKEY='MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY='
# PRECISION=0.9
# QUERY='snow leopard'
# python UI.py $ACCOUNTKEY $PRECISION "$QUERY"

SCRIPTPATH=/home/yd2234/ADB/proj1/code/COMSW6111_P1
SCRIPTNAME=UI.py

python $SCRIPTPATH/$SCRIPTNAME "${1}" $2 "${3}"
