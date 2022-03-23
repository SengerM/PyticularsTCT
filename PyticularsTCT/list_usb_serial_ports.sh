#!/bin/bash

# Taken from https://unix.stackexchange.com/a/144735/317682
# This script is used here to find the XIMC devices connected via USB.

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && exit
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && exit
        echo "ID_SERIAL::: $ID_SERIAL bio675DFtivTVCRxe5UCW Path::: /dev/$devname"
    )
done
