#!/bin/bash -e


mkdir "${ROOTFS_DIR}/home/pi/pifex"
cp -r files/pifex/pifex-sw/  "${ROOTFS_DIR}/home/pi/pifex"

# Set up the systemd servces to run on the Pi

# ECU Control Menu
cp files/pifex/pifex-sw/services/oled.service "${ROOTFS_DIR}/lib/systemd/system/"
cp files/pifex/pifex-sw/services/jupyter.service "${ROOTFS_DIR}/lib/systemd/system/"
cp files/pifex/pifex-sw/services/openocd.service "${ROOTFS_DIR}/lib/systemd/system/"
cp files/pifex/pifex-sw/services/gadgets.service "${ROOTFS_DIR}/lib/systemd/system/"

# Install the necessary python packages and dependencies
# TODO: Enable jupter service and oled service and pifex-ui service from here as well
on_chroot <<- EOF
	apt-mark auto python3-pyqt5 python3-opengl
	python3 -c "import platform;print(platform.machine());"
	python3 -m venv /home/pi/pifex-env
	source /home/pi/pifex-env/bin/activate
	pip3 install luma.oled
	pip3 install jupyterlab
	pip3 install python-can
	pip3 install scapy
	pip3 install flask
	pip3 install gpiozero
	pip3 install lgpio
	pip3 install spidev
	pip3 install serial
	pip3 install netifaces
	pip3 install flask_socketio
	cd /home/pi/
	sudo chown -R pi *
	sudo chgrp -R pi *
	systemctl enable oled.service
	systemctl enable jupyter.service
	systemctl enable openocd.service
	systemctl enable gadgets.service

EOF
