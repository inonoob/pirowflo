#!/bin/bash

## needed for the PyGObject

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
echo "installed needed modules for the project      "
echo "----------------------------------------------"
echo " "

sudo pip3 install -r requirements.txt

echo " "
echo "----------------------------------------------"
echo " installation done !"
echo "----------------------------------------------"
echo " "
