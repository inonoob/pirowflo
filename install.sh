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
sudo apt-get install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip libatlas-base-dev
echo " "


echo " "
echo "----------------------------------------------"
echo "install needed python3 modules for the project        "
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

# https://unix.stackexchange.com/questions/67936/attaching-usb-serial-device-with-custom-pid-to-ttyusb0-on-embedded

IFS=$'\n'
arrayusb=($(lsusb | cut -d " " -f 6 | cut -d ":" -f 2))

for i in "${arrayusb[@]}"
do
  if [ $i == 1008 ]|| [ $i == 1009 ] || [ $i == 1004 ]; then
    echo "Ant dongle found"
    echo 'ACTION=="add", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="'$i'", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c '"'echo 0fcf 1008 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'\""'' > /etc/udev/rules.d/99-garmin.rules
    echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0fcf", ATTR{idProduct}=="'$i'", MODE="666"' >> /etc/udev/rules.d/99-garmin.rules
    echo "udev rule written to /etc/udev/rules.d/99-garmin.rules"
    break
  else
    echo "No Ant stick found !"
  fi

done
unset IFS

echo "----------------------------------------------"
echo " add user to the group bluetoot and dialout   "
echo "----------------------------------------------"


sudo usermod -a -G bluetooth $USER
sudo usermod -a -G dialout $USER

echo " "
echo "-----------------------------------------------"
echo " Change bluetooth name of the pi to PiRowFlo"
echo "-----------------------------------------------"
echo " "

#echo "PRETTY_HOSTNAME=PiRowFlo" | sudo tee -a /etc/machine-info > /dev/null
echo "PRETTY_HOSTNAME=S4 Comms PI" | sudo tee -a /etc/machine-info > /dev/null

echo " "
echo "------------------------------------------------------"
echo " configuring web interface on http://${HOSTNAME}:9001 "
echo "------------------------------------------------------"
echo " "

# generate supervisord.conf from supervisord.conf.orig with updated paths
#
export repo_dir=$(cd $(dirname $0) > /dev/null 2>&1; pwd -P)
export python3_path=$(which python3)
export supervisord_path=$(which supervisord)
cp supervisord.conf.orig supervisord.conf
sed -i 's@#PYTHON3#@'"$python3_path"'@g' supervisord.conf
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' supervisord.conf
sudo sed -i -e '$i \su '"${USER}"' -c '\''nohup '"${supervisord_path}"' -c '"${repo_dir}"'/supervisord.conf'\''\n' /etc/rc.local

echo " "
  echo "----------------------------------------------------------"
echo " Update bluetooth settings according to Apple specifications"
echo "------------------------------------------------------------"
echo " "
# update bluetooth configuration and start supervisord from rc.local
#
sudo sed -i -e '$i \'"${repo_dir}"'/update-bt-cfg.sh''\n' /etc/rc.local # Update to respect iOS bluetooth specifications



echo "-----------------------------------------------"
echo " update bluart file as it prevents the start of"
echo " internal bluetooth if usb bluetooth dongle is "
echo " present                                       "
echo "-----------------------------------------------"

sudo sed -i 's/hci0/hci2/g' /usr/bin/btuart

echo " "
echo "----------------------------------------------"
echo " installation done ! rebooting in 3, 2, 1 "
echo "----------------------------------------------"
sleep 3
sudo reboot
echo " "
exit 0
