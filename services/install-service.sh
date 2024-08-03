#!/bin/bash

service=$1
sudo cp $service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $service
sudo systemctl start $service
