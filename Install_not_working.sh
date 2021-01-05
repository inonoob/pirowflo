#!/bin/bash

## needed for the PyGObject

echo "updates the list of latest updates available for the packages"
echo "-------------------------------------------------------------"
sudo apt-get update

echo "Check Python version and Bluetooth version    "
echo "----------------------------------------------"

BTversion= $(bluetoothd --version)
Pythonversion = $(python3 --version | cut -d " " -f2| cut -d "." -f1-2 )

if $BTversion -lt 5.49
then
  sudo apt-get install bluez -y
fi

if $Pythonversion -lt 3.6
then
  sudo apt-get install python3.7 -y
fi

echo "    "
echo "----------------------------------------------"
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0



## installation of needed module:

sudo pip3 install -r requirements.txt