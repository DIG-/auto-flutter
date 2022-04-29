#!/bin/sh
python3 -m pip install --prefix=$(python3 -m site --user-base) -e . --upgrade
