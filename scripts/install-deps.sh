#!/bin/bash

# Install basic dependencies
sudo apt-get install build-essential vim tmux git screen flashrom i2c-tools can-utils minicom cmake ipython3 python3-pip urjtag binwalk openocd

# Install LUMA
pip3 install luma.oled

# Clone and install LUMA examples
git clone https://github.com/rm-hull/luma.examples.git
cd luma.examples
sudo -H pip install -e .

# Install Jupyter
pip3 install jupyterlab
