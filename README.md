# OP25 Mobile Control Head

A 'remote' control head that interfaces with an OP25 instance.
We take advantage of some data end-points left exposed for the web interface of OP25 to fill out control head with data.

## Goal of This Project

Our goal is to build a commercial radio or mobile scanner-like control head for remote mounting an SDR based P25 Phase 1 and Phase 2 capable scanner.
_without_ making modifications to the OP25 software itself.

## Screenshots

![op25mch_uri](https://github.com/KR0SIV/op25mobileControlHead/blob/main/github_images/pi25_uri.gif)
![op25mch_nightmode](https://github.com/KR0SIV/op25mobileControlHead/blob/main/github_images/Pi25_NightMode.gif)


## Progress

- [X] Build the base 'Frame' / 'Grid' Tkinter Display
- [X] Pull data from OP25 WebUI Server
- [X] Run application on Android
- [X] Background Display Selector
- [X] Night Mode Functionality
- [X] OP25 URI Entry
- [ ] OP25 Instantance Broadcast to Find URI Automatically (Base Code Done, Not Tested Within UI)
- [X] Radio Reference System Importing
- [X] Automatic Generation of .tsv files
- [X] Remote Command Execution Server for Making Changes to OP25 Whitelist/Blacklist and Starting OP25 with Given Parameters
- [X] Call Log (Current Run Only)
- [ ] Bearing to nearrest site using Compass (need usb gps to complete testing, code written and placeholder compass on display)
- [X] Status Bar for Reporting Errors, Remote Command Send / Recieve Messages and more
- [ ] Automatic Site Switching (Very close to being implemented, all supporting code is done)
- [ ] 16 Channel 'On-The-Fly' Scannlist on a Button Grid. (Plan is to right click a button to give tag/talkgroupID, Press in to Enable Scan of Talkgroup) 


## How Do I Use It?

I have soooooo much to add, consider this VERY unfinished.
Manually pip install any dependancies...

Upon first start you'll be prompted for your OP25 URI.
If you enter it incorrectly that's okay, after first run "config.ini" will be created in the directory you ran it in.
You can edit the URI there directly.

You _NEED_ to be sure you enable the OP25 Web interface on the _BOATBOD_ fork!
''' -l http:0.0.0.0:8080'''

Eventually this is all going to be automated.
