#!/bin/bash

pyrtkproc.py -d ~/RxTURP/BEGPIOS/ASTX/rinex/19134/ -r GALI1340.19O -f 4 -m single -c 5 -e GALI1340.19E -g gal  -t ~/amPython/pyRTKLib/rnx2rtkp.tmpl -i brdc -a saas -s brdc -o -l INFO DEBUG
