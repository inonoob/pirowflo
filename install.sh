#!/bin/bash
# https://stackoverflow.com/questions/9449417/how-do-i-assign-the-output-of-a-command-into-an-array

echo " "
echo " "
echo " "
echo " "
echo "  PiRowFlo for Waterrower"
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

set -e  # Exit the script if any command fails

echo " "
echo "-------------------------------------------------------------"
echo "updates the list of latest updates available for the packages"
echo "-------------------------------------------------------------"
echo " "
sudo apt-get update

echo " "
echo "----------------------------------------------"
echo "install needed packages for python          "
echo "----------------------------------------------"
echo " "

sudo apt-get install -y \
    python3 \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    python3-pip \
    libatlas-base-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff6

echo " "
echo "----------------------------------------------"
echo "set up virtual environment        "
echo "----------------------------------------------"
echo " "

python3 -m venv venv
source venv/bin/activate

echo " "
echo "----------------------------------------------"
echo "install needed python3 modules for the project        "
echo "----------------------------------------------"
echo " "

pip install --upgrade pip
pip install -r requirements.txt

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
echo " Add current user to bluetooth and dialout groups"
echo " (pirowflo should be run by this user) "
echo "----------------------------------------------"

CURRENT_USER=$(whoami)
sudo usermod -a -G bluetooth "$CURRENT_USER"
sudo usermod -a -G dialout "$CURRENT_USER"

echo " "
echo "-----------------------------------------------"
echo " Change bluetooth name of the pi to PiRowFlo"
echo "-----------------------------------------------"
echo " "

echo "PRETTY_HOSTNAME=PiRowFlo" | sudo tee -a /etc/machine-info > /dev/null
#echo "PRETTY_HOSTNAME=S4 Comms PI" | sudo tee -a /etc/machine-info > /dev/null




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
export supervisorctl_path=$(which supervisorctl)

cp services/supervisord.conf.orig services/supervisord.conf
sed -i 's@#PYTHON3#@'"$python3_path"'@g' services/supervisord.conf
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' services/supervisord.conf
sed -i 's@#USER#@'"$CURRENT_USER"'@g' services/supervisord.conf

# configure a systemd service to start supervisord automatically at boot
#
cp services/supervisord.service services/supervisord.service.tmp
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' services/supervisord.service.tmp
sed -i 's@#SUPERVISORD_PATH#@'"$supervisord_path"'@g' services/supervisord.service.tmp
sed -i 's@#SUPERVISORCTL_PATH#@'"$supervisorctl_path"'@g' services/supervisord.service.tmp
sudo mv services/supervisord.service.tmp /etc/systemd/system/supervisord.service
sudo chown root:root /etc/systemd/system/supervisord.service
sudo chmod 655 /etc/systemd/system/supervisord.service
sudo systemctl enable supervisord
sudo rm -f /tmp/pirowflo*
sudo rm -f /tmp/supervisord.log

echo " "
echo "------------------------------------------------------------"
echo " Update bluetooth settings according to Apple specifications"
echo "------------------------------------------------------------"
echo " "
# update bluetooth configuration and start supervisord from rc.local
#
cp services/update-bt-cfg.service services/update-bt-cfg.service.tmp
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' services/update-bt-cfg.service.tmp
sudo mv services/update-bt-cfg.service.tmp /etc/systemd/system/update-bt-cfg.service
sudo chown root:root /etc/systemd/system/update-bt-cfg.service
sudo chmod 655 /etc/systemd/system/update-bt-cfg.service
sudo systemctl enable update-bt-cfg


echo " "
echo "------------------------------------------------------------"
echo " setup screen setting to start up at boot                   "
echo "------------------------------------------------------------"
echo " "

sudo sed -i 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/firmware/config.txt
cp src/adapters/screen/settings.ini.orig src/adapters/screen/settings.ini
sudo sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' src/adapters/screen/settings.ini

cp services/screen.service services/screen.service.tmp
sed -i 's@#PYTHON3#@'"$python3_path"'@g' services/screen.service.tmp
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' services/screen.service.tmp
sed -i 's@#USER#@'"$CURRENT_USER"'@g' services/screen.service.tmp
sudo mv services/screen.service.tmp /etc/systemd/system/screen.service
sudo chown root:root /etc/systemd/system/screen.service
sudo chmod 655 /etc/systemd/system/screen.service
sudo systemctl enable screen

echo " "
echo "-----------------------------------------------"
echo " update bluart file as it prevents the start of"
echo " internal bluetooth if usb bluetooth dongle is "
echo " present                                       "
echo "-----------------------------------------------"
echo " "

sudo sed -i 's/hci0/hci2/g' /usr/bin/btuart

echo " "
echo "----------------------------------------------"
echo " Add absolut path to the logging.conf file    "
echo "----------------------------------------------"
echo " "

cp src/logging.conf.orig src/logging.conf
sed -i 's@#REPO_DIR#@'"$repo_dir"'@g' src/logging.conf

echo " "
echo "----------------------------------------------"
echo " installation done ! rebooting in 3, 2, 1 "
echo "----------------------------------------------"
sleep 3
sudo reboot
echo " "
exit 0
