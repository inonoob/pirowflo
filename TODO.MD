# TODO.md

## Bug Fixes

### Todo in WRtoBLEANT.py

- [x] check why elapsed time is not reset to 0 if rower has been reseted. self.rowerreset = True 
- [x] write a function to average the power during a stroke. Coxswain does calculate the average power for 5 stroke
this can be achieved by checking the flag SS = Start stroke from the waterrower and SE = Stroke end. 
  For 5 Strokes take the maximum and average it. This should result in a good solution. As mention Coxswain
  calculated it that way.
  

## needed Feature
- [x] add Ant+ capabiltiy to send data
- [ ] Fix conversion from waterrower to Ant+ format
- [ ] add webserver to control the start/stop/restart of the script (Flask or web.py)
- [x] python requirement.txt
- [ ] Install.sh file which does all the installation stuff

  
  
