#!/bin/bash

# https://stackoverflow.com/questions/9449417/how-do-i-assign-the-output-of-a-command-into-an-array

echo " "
echo " "
echo " "
echo " "
echo "  Waterrower Ant and BLE Raspberry Pi Module"
echo "                                                             +-+"
echo "                                           XX+-----------------+"
echo "              +-------+                 XXXX    |----|       | |"
echo "               +-----+                XXX +----------------+ | |"
echo "               |     |             XXX    |XXXXXXXXXXXXXXXX| | |"
echo "+--------------X-----X----------+XXX+------------------------+-+"
echo "|                                                              |"
echo "+--------------------------------------------------------------+"
echo " "
echo " This script will install all the needed packages and modules "
echo " to make the Waterrower Ant and BLE Raspbery Pi Module working"
echo " "

echo " "
echo "-------------------------------------------------------------"
echo "updates the list of latest updates available for the packages"
echo "-------------------------------------------------------------"
echo " "
sudo apt-get update

echo " "
echo "----------------------------------------------"
echo "installed needed packages for python          "
echo "----------------------------------------------"
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip libatlas-base-dev git
echo " "


echo " "
echo "----------------------------------------------"
echo "install needed modules for the project        "
echo "----------------------------------------------"
echo " "

sudo pip3 install -r requirements.txt

echo " "
echo "-------------------------------------------------------"
echo "check for Ant+ dongle in order to set udev rules       "
echo "Load the Ant+ dongle with FTDI driver                  "
echo "and ensure that the user pi has access to              "
echo "-------------------------------------------------------"
echo " "

IFS=$'\n'
arrayusb=($(lsusb | cut -d " " -f 6 | cut -d ":" -f 2))

for i in ${arrayusb[@]}
do
  if [ $i == 1008 ]|| [ $i == 1009 ] || [ $i == 1004 ]; then
    echo "Ant dongle found"
    echo 'ACTION=="add", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=='$i', RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c '"'echo 0fcf 1008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'\""'' > /etc/udev/rules.d/99-garmin.rules
    echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0fcf", ATTR{idProduct}=='$i', MODE="666"' >> /etc/udev/rules.d/99-garmin.rules
    echo "udev rule written to /etc/udev/rules.d/99-garmin.rules"
 >> fileName
    break
  else
    echo "No Ant stick found !"
  fi

done
unset IFS

echo " "
echo "----------------------------------------------"
echo " installation done !"
echo "----------------------------------------------"
echo " "
exit 0