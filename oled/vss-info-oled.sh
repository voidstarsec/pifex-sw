#!/bin/bash

source /home/pi/pifex-env/bin/activate
cd /home/pi/pifex/pifex-sw-hhb/oled/
python3 vss_sys_info.py --i2c-port 6
