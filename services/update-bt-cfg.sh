#!/bin/sh
# This script will update the bluetooth interface for iOS compatibility
# usage:
# update-bt-cfg.sh [interface] [conn_min_interval] [conn_max_interval] [supervision_timeout]
# if no arguments are provided the script will use the following defaults: hci0, 12, 12, 500
# https://stackoverflow.com/questions/55189681/unable-to-maintain-ble-connection-bluez-linux-ios/55228279?fbclid=IwAR1Icm-sRfzDsBzFJzTp2KYzhIgM6FTyW0t-WbDdHh2DpGeQ9lhEUCgxu28#55228279
#
print_bt_config() {
  conn_min_interval=$(cat ${bt_dir}/conn_min_interval)
  conn_max_interval=$(cat ${bt_dir}/conn_max_interval)
  conn_max_interval=$(cat ${bt_dir}/conn_max_interval)
  supervision_timeout=$(cat ${bt_dir}/supervision_timeout)
  echo "conn_min_interval : ${conn_min_interval}"
  echo "conn_max_interval : ${conn_max_interval}"
  echo "supervision_timeout : ${supervision_timeout}"
}

device_id="${1:-hci1}"
echo "device: ${device_id}"

bt_dir="/sys/kernel/debug/bluetooth/${device_id}/"
if [ ! -d ${bt_dir} ] ; then
    echo "${bt_dir} does not exist"
    exit 1
fi

echo "----------------------------"
echo "original values:"
print_bt_config

# update config values for iOS compatibility
echo "${2:-12}" > ${bt_dir}/conn_min_interval
echo "${3:-12}" > ${bt_dir}/conn_max_interval
echo "${4:-500}" > ${bt_dir}/supervision_timeout

echo "----------------------------"
echo "updated values:"
print_bt_config
