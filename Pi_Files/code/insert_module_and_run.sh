#!/bin/bash

insmod /home/pi/Pi_Files/piio/piio.ko
chmod 777 /dev/piiodev
./MQTT_Subscribe.py
