#!/bin/bash

## needed for the PyGObject

echo "Check for required binaries and python modules"
echo "----------------------------------------------"
sudo apt-get update

BTversion= $(bluetoothd --version)
Pythonversion = $(python3 --version | cut -d " " -f2| cut -d "." -f1-2 )

if $BTversion -lt 5.49
then
  sudo apt-get install bluez
fi

if $Pythonversion -lt 3.7
then
  sudo apt-get install python3.7
fi
#echo "Install lib to compile bluez"
#sudo apt-get install libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev -y
#
#wget www.kernel.org/pub/linux/bluetooth/bluez-5.55.tar.xz
#
#tar xvf bluez-5.55.tar.xz && cd bluez-5.55
#
#./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-experimental
#
#make -j4
#
#sudo make install


echo "Install python and PyGObject"
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0



## installation of needed module:

sudo pip3 install -r requirements.txt