#!/bin/bash

# Install pigpio library
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install

# clean up
cd ..
rm -rf master.zip pigpio-master

# Navigate to the Car directory
cd ./Car

# Create and activate virtual environment, then install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt



