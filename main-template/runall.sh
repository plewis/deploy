#!/bin/bash

. astral.sh
. svdq.sh
python3 theta-lambda-svdqage.py
. smc.sh
. beast.sh
paup rfsmc.nex
paup rfbeast.nex
python3 summarize.py
cat summary.txt
