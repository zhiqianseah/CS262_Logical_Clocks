#!/bin/bash

for i in `seq 1 3`;
do
    echo -e "python $(pwd)/VM$i.py\nbash" > vm$i.command; chmod +x vm$i.command; open vm$i.command 
done
