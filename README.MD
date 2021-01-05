# BLE and Ant+ for Waterrower


      Waterrower Ant and BLE Raspberry Pi Module
                                                                 +-+
                                               XX+-----------------+
                  +-------+                 XXXX    |----|       | |
                   +-----+                XXX +----------------+ | |
                   |     |             XXX    |XXXXXXXXXXXXXXXX| | |
    +--------------X-----X----------+XXX+------------------------+-+
    |                                                              |
    +--------------------------------------------------------------+



<img src="docs/Hardware/IMG_20210104_155432.jpg" width=36% height=36%> <img src="docs/Hardware/Selection_015.png" width=30% height=30%>



This python script replaces the Waterrower com module. A Raspberry Pi is connected via usb with the Waterrower. The rowing
data are processed by the python script which is then send via bluetooth Low Energy Fitness equipment profile to the connected App. E.g Android
app Coxswain, Kinomap or Cityrow. 

- [x] Status = Done

Additionally, it is planned to have the processed data to be sent also via Ant+. This is an idea for Garmin watches especially 
the Fenix 6 series as the native rowing app can use thoes Data. The Ant+ profile used here is the Fitness Machine. 

- [x] Status = Done

even more, the script will be control via a build in webserver that can control the script to Start/stop 
and Restart it.

- [ ] Status = Pending

Last idea would be to track and export the workout to a FIT file which is then used for Garmin-connect or Strava. 

- [ ] Status = Pending

## Features

- Read Serial Waterrower Data to the Pi
- Send Waterower Data from the Pi over Bluetooth (Build-in or USB-dongle) 
- Send Waterrower Data from the Pi over Ant+ via Ant+ dongle 

## Supported Fitness app or watches: 

- [x] Coxswain  (bluetooth)
- [x] Cityrow   (bluetooth)
- [ ] Kinomap   (bluetooth)     not yet tested 
- [ ] Garmin fenix 6 watch (Ant+) not yet tested 

## Planned Features

- Webserver to control script in order to start/stop/restart Bluetooth,Ant or Waterrower
- Export to FIT files (Garmin )

## Parts of the code based on following Repos:

- [Link to repo](https://github.com/bfritscher/waterrower) base code used to get the Waterrower Data over USB Interface 
- [Link to repo](https://github.com/PunchThrough/espresso-ble) base code for the BLE GATT server and Advertiser example which
is self based on the Bluez Gatt server example
- [Link to repo](https://github.com/WouterJD/FortiusANT) base code for the Ant+ part used for this project

Thoses Repos with some of their code are used as  base code 
which then have been rewritten to meet the requirements of this project. 

## Motivation

I wanted to have the ability to use the Android App Coxswain and also my Garmin smartwatch. Therefore, I though
why not connect the Waterrower via USB to a Raspberry pi and let the Raspberry pi being a BLE and Ant+ transmitter. 
And wouldn't be even better if it could be control for the Webbrowser. And Last but not least, have at the 
end of the training a FIT file for Garmin connect or Strava.

## Requirements

### Hardware 

Bill of Material(BOM)

<img src="docs/Hardware/IMG_20210104_155452.jpg" width=50% height=50%>

| Item for Raspberry pi| 
|------|
| Raspberry Pi || 
| Micro SD card || 
| Mini USB to USB typ A ||  
| Bluetooth USB dongle 4.1 (LogiLink BT0015) || 
| Micro USB to Typ A || 
| 5V USB power supply 2A ||
| **for Ant+ addition** || 
| Ant+ dongle (avoid Cyclone) ||

<img src="docs/Hardware/IMG_20210104_155756.jpg" width=50% height=50%>

| Item for Raspberry pi Zero W | 
|------|
| Raspberry Pi Zero W || 
| Micro SD card || 
| Mini USB to Micro USB || 
| 5V USB power supply 2A ||
| Total||
| **for Ant+ addition**  || 
| Ant+ dongle (avoid Cyclone) ||
| Micro USB to USB Hub || 

<img src="docs/Hardware/IMG_20210104_155825.jpg" width=50% height=50%>

I would recommend buying the Raspberry pi in a kit where most of the parts are inclued 

### Software 

## Installation or Getting Started

Clone the repo from Github: 

    git clone https://github.com/inonoob/WaterrowerAntBle.git 
    
go into the folder: 

    cd WaterrowerAntBle 

make install.sh executable: 

    sudo chmod +x install.sh

execute install.sh in order to setup everything: 

    sudo ./install.sh 

once installation complete, start the main script: 

    python3 WaterrowerThreads.py 


