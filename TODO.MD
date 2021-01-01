# TODO.md

## Bug Fixes

### Todo in WRtoBLEANT.py

- [x] check why elapsed time is not reset to 0 if rower has been reseted. self.rowerreset = True 
- [x] write a function to average the power during a stroke. Coxswain does calculate the average power for 5 stroke
this can be achieved by checking the flag SS = Start stroke from the waterrower and SE = Stroke end. 
  For 5 Strokes take the maximum and average it. This should result in a good solution. As mention Coxswain
  calculated it that way.
  

## needed Feature
- [ ] add webserver to control the start/stop/restart of the script
- [x] python requirement.txt 
- [ ] python installer

## nice to have Feature 
- [ ] add ANT with an ANT stick in order to send data over ant e.g. Garmin watches. Fenix 6 series has 
got a new update, which for the native rowing app accepts ant sensor (rower) to broadcast the data to the watch 
  e.g. concept2 already use that technic.
  
