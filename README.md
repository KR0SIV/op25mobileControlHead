# OP25 Mobile Control Head

A 'remote' control head that interfaces with an OP25 instance.
We take advantage of some data end-points left exposed for the web interface of OP25 to fill out control head with data.

### UPDATE
## This application is being ported to Kivy. The repo will be made public upon first release and eventually linked here. While some bug fixes may be done the future is set on the Kivy implementation of Pi25mch.

## Goal of This Project

My goal is to build a commercial radio or mobile scanner-like control head for remote mounting an SDR based P25 Phase 1 and Phase 2 capable scanner.
_without_ making modifications to the OP25 software itself.

### This Project was born out of Pi25 Which consists of a portable handheld and mobile version. The mobile version is this repository and is the only one currently being actively developed at the moment.

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
- [X] Bearing to nearrest site using Compass (need usb gps to complete testing, code written and placeholder compass on display)
- [X] Status Bar for Reporting Errors, Remote Command Send / Recieve Messages and more
- [X] Automatic Site Switching (Very close to being implemented, all supporting code is done)
- [X] 16 Channel 'On-The-Fly' Scannlist on a Button Grid. (Plan is to right click a button to give tag/talkgroupID, Press in to Enable Scan of Talkgroup) 
     ![op25mch_scanmodes](https://github.com/KR0SIV/op25mobileControlHead/blob/main/github_images/Pi25_MCH_ScanGrid_ScanMode.gif)
     I'm pretty excited about this one. You can switch between 'Scan List' mode or 'Site Scan' mode to hear all site traffic or just scanlists (whitelist.tsv). To make this a bit more special though I've added a 16ch 'ScanGrid' which loads from a user provided 'scangrid.tsv' file. This grid is available ONLY in 'List Scan Mode'. Simple push the buttons that correspond to the talk groups you wish to hear and there ya go! To mute them, just hit the button again!
When you're done, just switch back to 'site scan' mode.

- [ ] Port code over to Kivy for better mobile distribution as an iOS and (primarily) Android App.
This is in-progress in a private repo until the first public release.

## List of parts used in the hardware build
- *NOTE: These are affiliate links which help support the project. This is a work-in-progress project, incomplete.
- Raspberry pi 'Juice' battery backup board: https://amzn.to/3FiMTmC
- Arkon VESA mount for mobile/car use: https://amzn.to/3iv9tON
- Official Raspberry pi 4 power supply for desktop use: https://amzn.to/2ZU4b9j
- Pi Touch Raspberry pi 3/4 housing for LCD: https://amzn.to/3ovVuMO
- 4GB Raspberry pi 4: https://amzn.to/3Bklv4U
- Official Raspberry pi Touch Display: https://amzn.to/2ZVAggY
- VESA mount screws: https://amzn.to/3it9Idg
     

## How Do I Use It?

I have soooooo much to add, consider this VERY unfinished.
Manually pip install any dependancies...

Upon first start you'll be prompted for your OP25 URI.
If you enter it incorrectly that's okay, after first run "config.ini" will be created in the directory you ran it in.
You can edit the URI there directly.

If you do not run the remote script on the device hosting your OP25 instance you'll _NEED_ to be sure you enable the OP25 Web interface on the _BOATBOD_ fork!
''' -l http:0.0.0.0:8080'''
