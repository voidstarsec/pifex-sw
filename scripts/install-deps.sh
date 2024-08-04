#!/bin/bash

# Install basic dependencies
sudo apt-get install build-essential vim tmux git screen flashrom i2c-tools can-utils minicom cmake ipython3 python3-pip urjtag binwalk openocd

# Install LUMA
sudo apt-get install  python3-luma.oled

# Clone and install LUMA examples
git clone https://github.com/rm-hull/luma.examples.git

# Install Jupyter
pip3 install python3-jupyterlab
