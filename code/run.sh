#!/bin/bash

# Author: Yuan Du (yd2234@columbia.edu)
# Date: Sep 24, 2012
# Function: test UI.py by given account key, precision and query
# Usage: ./run.sh

ACCOUNTKEY="MWQrrA8YW+6ciAUTJh56VHz1vi/Mdqu0lSbzms3N7NY="
PRECISION=0.9
QUERY="gates"
python UI.sh $ACCOUNTKEY $PRECISION $QUERY
