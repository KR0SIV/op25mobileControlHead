import requests
import json
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext as tks
import threading
# import pyglet
from PIL import Image, ImageTk
import time
import io
import re
from datetime import datetime
import configparser, os
from os import walk
from playsound import playsound


def sysmsgUPDATE(text, bg):
    text = text + '\t' + str(datetime.now().strftime('%I:%M:%S'))
    sys_logTEXT.insert("1.0", text + '\n')
    sys_logTEXT.tag_add('highlightline', '1.0', '2.0')
    sys_logTEXT.tag_add('unhighlightline', '2.0', END)
    sys_logTEXT.tag_configure('highlightline', background='lightgreen')
    sys_logTEXT.tag_configure('unhighlightline', background='gray')
    # if count > 30:
    #   call_logTEXT.delete("30.0", END)
    bottomStatusTEXT.configure(text=text, bg=bg)

directories = ['scan', 'alerts']

for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)
##config bug, until restart when you add your config details the log will double

config = configparser.ConfigParser()


# Just a small function to write the file
def write_file():
    config.write(open('config.ini', 'w'))


def confwriter(argsection, argoption, argvalue):
    if argsection in config.sections():
        config.set(section=argsection, option=argoption, value=argvalue)
        write_file()
    else:
        config.add_section(argsection)
        config.set(section=argsection, option=argoption, value=argvalue)
        write_file()


try:
    config.read('config.ini')
    op25uri = config.get('Pi25MCH', 'uri')
except:
    confwriter('Pi25MCH', 'uri', '')


def jsoncmd(command, arg1, arg2):
    config.read('config.ini')
    op25uri = config.get('Pi25MCH', 'uri')
    if op25uri == '':
        # print('no uri found')
        # time.sleep(1)
        jsoncmd(command=command, arg1=arg1, arg2=arg2)
    if op25uri == 'http://ip_address_to_OP25:port':
        print('default uri found')
        # time.sleep(1)
        jsoncmd(command=command, arg1=arg1, arg2=arg2)
    else:
        try:
            # print('found uri')
            return requests.post(op25uri, json=[{"command": command, "arg1": int(arg1), "arg2": int(arg2)}])
        except:
            sysmsgUPDATE(text='ERROR: Couldn\'t Contact Remote.py', bg='red')


def alertsTSV():
    try:
        alertfile = open("alerts/default.tsv", "r").read()
    except:
        defaultalertTSV = open("alerts/default.tsv", "w")
        defaultalertTSV.write("0000")
        defaultalertTSV.close()
        alertfile = open("alerts/default.tsv", "r").read()
    return alertfile


# ./rx.py --args 'rtl' -N 'LNA:49' -S 2000000 -f 855.8625e6 -o 25000 -T trunk.tsv -V -2 -q -1 -l http:0.0.0.0:8080
# pyglet.font.add_file('digital.ttf')

##Formats numbers with a decminal every 3 char
def formatchan(frequency):
    return '.'.join(frequency[i:i + 3] for i in range(0, len(frequency), 3))


if not os.path.exists('logs/'):
    os.mkdir('logs/')

def call_logSaver(call):
    state = config.get('Menu Button Grid', 'calllogging')
    if "True" in state:
        logFile = open('logs/callLog-adding-improvements-later.log', 'a')
        logFile.write(call+"\r")
        logFile.close()

    else:
        pass



##Update function, runs in a thread to keep checcking for new data from the OP25 web server.
def update():
    count = 1
    current = ""
    currentAlert = ''
    print('Running Update')
    alertfile = alertsTSV()
    while True:
        # time.sleep(0.5)
        try:
            # r = requests.post(op25uri, json=[{"command": "update", "data": 0}]) #OP25 2017 Request Format
            # r = requests.post(op25uri, json=[{"command":"update","arg1":0,"arg2":0}])  # OP25 2020 Request Format
            r = jsoncmd("update", 0, 0)
            data = json.loads(r.content)
            try:
                nac = str(hex(data[0]['nac']))
                # nacTEXT.configure(text='NAC: ' + nac)
                rawnac = str(data[0]['nac'])
                wacn = str(hex(data[0]['wacn']))
                # wacnTEXT.configure(text='WACN: ' + wacn)
                nacwacnTEXT.configure(text='NAC: ' + nac + ' / ' + 'WACN: ' + wacn)
                tgid = str(data[0]['tgid'])
                # tgidTEXT.configure(text=tgid)
                system = str(data[0]['system'])
                systemTEXT.configure(text=system)
                sysid = str('Sys ID: ' + hex(data[0]['sysid']))
                sysidTEXT.configure(text=sysid)
                tag = str(data[0]['tag'])

                if re.search('[a-zA-Z]', tag):
                    tag = tag.lstrip()
                else:
                    #tag = ('TG ID: ' + tgid)
                    tag = ('TGID: ' + tgid + ' [' + str(hex(int(tgid))) + ']')###int(tgid) causes an exception and prevents NONE from printing to the screen. I put this back so that doesn't happen but you need to not fix this by causing an exception!!!!!!!
                    # if 'None' in tgid:
                    #    tag = ('TG ID: ' + grpaddr)


                tagTEXT.configure(text=tag)

                if grpaddr in alertfile:
                    if currentAlert != grpaddr:
                        currentAlert = grpaddr
                        alertTEXT.configure(text=tag[:13], fg='red')
                        timestamp = str(datetime.now().strftime('%I:%M:%S'))
                        row3alertTEXT.configure(text='Last Alert at: ' + timestamp)
                        playsound('static/audio/beep_short_on.wav')
                offset = str(data[0]['fine_tune'])
                # offsetTEXT.configure(text='FREQ OFFSET: ' + offset)
                freq = str(data[0]['freq'])
                # freqTEXT.configure(text='.'.join(freq[i:i + 3] for i in range(0, len(freq), 3)))
            except Exception as e:
                #print(e)
                pass
            try:
                # srcaddrTEXT.configure(text='SRC: ' + srcaddr)
                grpaddr = str(data[1]['grpaddr'])
                enc = str(data[1]['encrypted'])
                if enc == str(0):
                    encTEXT.configure(fg='grey')
                else:
                    encTEXT.configure(fg='black')
                    alertTEXT.configure(text=grpaddr, fg='blue')
                    sysmsgUPDATE(text='Encrypted Call Detected on GRP: ' + grpaddr, bg='gray')
                    # if encTEXT.cget(bg='black'):
                    #    encTEXT.configure(fg='white')
                srcaddr = str(data[1]['srcaddr'])
                if grpaddr == str(0):
                    tagTEXT.configure(text='Scanning...')
                    alertTEXT.configure(fg='#383b39')
                if grpaddr != str(0):
                    if current != tag:
                        regexp = re.compile('[a-z]|[A-Z]')
                        if regexp.search(tag):
                            # callLog = callLog + tag + str('\t' + str(datetime.datetime.now()) + '\n')
                            call = str(count) + " " + tag + str(
                                '\t' + 'GRP: ' + str(grpaddr) + '\tSRC: ' + str(srcaddr) + '\t' + str(
                                    datetime.now().strftime('%I:%M:%S')))
                            # print(callLog)
                            # call_logTEXT.configure(text=callLog)
                            call_logTEXT.insert("1.0", call + '\n')
                            call_logTEXT.tag_add('highlightline', '1.0', '2.0')
                            call_logTEXT.tag_add('unhighlightline', '2.0', END)
                            call_logTEXT.tag_configure('highlightline', background='lightgreen')
                            call_logTEXT.tag_configure('unhighlightline', background='gray')
                            # call_logTEXT.yview_pickplace("end")
                            # call_logTEXT.see("end")
                            call_logSaver(call)
                            current = tag
                            count = count + 1
                            if count > 30:
                                call_logTEXT.delete("30.0", END)
                        else:
                            pass
                # grpaddrTEXT.configure(text='GRP: ' + grpaddr)
                grpTEXT.configure(text=grpaddr)
                bothaddrTEXT.configure(text='SRC: ' + srcaddr + '\r' + 'GRP: ' + grpaddr)
                rxchan = str(data[1][rawnac]['rxchan'])
                # rxchanTEXT.configure(text=rxchan)
                txchan = str(data[1][rawnac]['txchan'])
                # txchanTEXT.configure(text=txchan)
                bothrxtxTEXT.configure(text='RX: ' + formatchan(rxchan) + '\r' + 'TX: ' + formatchan(txchan))
                rfid = str(data[1][rawnac]['rfid'])
                # rfidTEXT.configure(text='RFSS ' + rfid)
                stid = str(data[1][rawnac]['stid'])
                # stidTEXT.configure(text='SITE ' + stid)
                secondary = str(data[1][rawnac]['secondary'])
                altcc = re.sub('\[|]', '', secondary).split(',')
                # secondaryTEXT.configure(
                #    text='ALT CTL: ' + formatchan(altcc[0]) + ', ' + formatchan(altcc[1].replace(' ', '')) + ', ' + formatchan(altcc[2].replace(' ', '')))
                adjacent_data = str(data[1][rawnac]['adjacent_data'])
                # adjacent_dataTEXT.configure(text=adjacent_data)
                # print(adjacent_data)
                frequencies = str(data[1][rawnac]['frequencies'])
                # frequenciesTEXT.configure(text=frequencies)
                tsbks = str(data[1][rawnac]['tsbks'])
                # tsbksTEXT.configure(text='tsbks:' + tsbks)
            except Exception as e:
                # print(e)
                pass
            try:
                error = str(data[2]['error'])
                # errorTEXT.configure(text='ERR: ' + error + 'Hz')
            except:
                pass

        except:
            sysmsgUPDATE(text='Reconnecting to OP25 Instance', bg='red')
            tagTEXT.configure(text='Connecting...')
            time.sleep(1)
            sysmsgUPDATE(text='Remote: Start OP25', bg='green')
            sendCMD(function='startop25', sdr='rtl', lna='49', samplerate='2000000', trunkfile='trunk.tsv',
                    op25dir='/home/op25/op25/op25/gr-op25_repeater/apps/')
            time.sleep(7)
            sysmsgUPDATE(text='Attempting to reconnect', bg='red')
            if jsoncmd('update', 0, 0) == None:
                pass
            else:
                sysmsgUPDATE(text='OP25 Instance Connected!', bg='green')
            update()


def nightMode():
    print('Night Mode Thread Running')
    time.sleep(15)
    nightmodePrompt.grid(row=1, column=0)
    colorFUNC('black')
    compassIMG.configure(bg='black')
    holdBTN.configure(bg='gray')
    gotoBTN.configure(bg='gray')
    skipBTN.configure(bg='gray')
    menuBTN.configure(bg='gray')
    # call_logTEXT.tag_configure('unhighlightline', background='gray')
    call_logTEXT.configure(bg='gray')
    compassRangeTEXT.configure(bg='black', fg='gray')
    style.theme_use('Nightmode')
    count = 10
    while count != 0:
        nightModeTEXT.configure(text='Switching to Nightmode\nMessage will close in ' + str(count) + 'sec')
        time.sleep(1)
        count = count - 1
    nightmodePrompt.grid_remove()


##Button Functions
def holdFUNC(input):
    if holdBTN.cget('relief') == SUNKEN:
        if skipBTN.cget('bg') == 'black':  ##Check another button to see what the background color is
            holdBTN.configure(relief=RAISED, fg='white', text='HOLD')  ##If blackbackground then white text
        holdBTN.configure(relief=RAISED, fg='black', text='HOLD')  ##IF any other background then black text
        # requests.post(op25uri, json=[{"command": "hold", "arg1": 0, "arg2": 0}])
        jsoncmd("hold", 0, 0)
        sysmsgUPDATE(text='Releasing Talkgroup: ' + str(input), bg='green')
    else:
        if int(input) != 0:
            holdBTN.configure(relief=SUNKEN, fg='red', text=input)
            # requests.post(op25uri, json=[{"command": "hold", "arg1": int(input), "arg2": 0}])
            jsoncmd("hold", int(input), 0)
            sysmsgUPDATE(text='Holding Talkgroup: ' + str(input), bg='green')


def lockoutFUNC():
    # requests.post(op25uri, json=[{"command": "skip", "arg1": 0, "arg2": 0}])
    jsoncmd('lockout', 0, 0)
    sysmsgUPDATE(text='Locking Out Talkgroup: ' + str(grpTEXT.cget('text')), bg='green')


def skipFUNC():
    # requests.post(op25uri, json=[{"command": "skip", "arg1": 0, "arg2": 0}])
    jsoncmd('skip', 0, 0)
    sysmsgUPDATE(text='Skipping Talkgroup: ' + str(grpTEXT.cget('text')), bg='green')


def gotoFUNC():
    if gotoBTN.cget('relief') == SUNKEN:
        rightkeypadFrame.grid_remove()
        gotoBTN.configure(relief=RAISED)
    else:
        gotoBTN.configure(relief=SUNKEN)
        rightkeypadFrame.grid(column=1, row=0, columns=1, sticky='NESW')
        # rightkeypadFrame.grid_remove()


##END Button Functions


##Main TKInter Config/Setup
screen_width = 2280 // 2
screen_height = 1080 // 2
screen_geometry = '{}x{}'.format(screen_width, screen_height)

main_window = Tk()
# main_window.call('tk', 'scaling', 2.8) #Android phone scale
main_window.call('tk', 'scaling', 2.0)  # Windows 10 scale
main_window.title('OP25 Control Head')
# main_window.resizable(0, 0)
# main_window.wm_attributes('-transparentcolor', main_window['bg'])
# main_window.configure(background='orange')
main_window.geometry(screen_geometry)

##FRAME COLOR OPTIONS
try:
    config.get('Pi25MCH', 'display_color')
except:
    confwriter('Pi25MCH', 'display_color', 'black')
    write_file()

display_color = config.get('Pi25MCH', 'display_color')


rootFrame = Frame(main_window)
rootFrame.grid(column=0, row=0, rows=3, columns=2, sticky='NESW')
main_window.columnconfigure(0, weight=1)  # rootFrame spans to main_window width
main_window.rowconfigure(0, weight=1)  # rootFrame spans to main_window height

##Top Frame;A button bar;menu bar;status text;something
topFrame = Frame(rootFrame)
# topFrame.grid(column=0, row=0, columnspan=2, sticky='NEW')
# Label(topFrame, text='Status or Menu Bar Row').grid()
rootFrame.columnconfigure(0, weight=1)  # topFrame spans to main_window width
##END Top Frame

##Primary Frame Holding Two Column Frames For Presenting Radio System Data
activeFrame = Frame(rootFrame)
activeFrame.grid(column=0, row=1, rows=3, columnspan=2, sticky='NESW')
rootFrame.rowconfigure(1, weight=1)

leftFrame = Frame(activeFrame, bd=1, relief=SOLID)
leftFrame.grid(column=0, row=0, rows=3, columns=1, sticky='NESW')
Label(leftFrame, text='Left Frame Text').grid()

rightFrame = Frame(activeFrame, bd=1, relief=SOLID)
rightFrame.grid(column=1, row=0, rows=3, columns=1, sticky='NESW')
Label(rightFrame, text='Right Frame Text').grid()

rightkeypadFrame = Frame(activeFrame, bd=1, relief=SOLID)
# rightkeypadFrame.grid(column=1, row=0, columns=1, sticky='NESW')
# rightkeypadFrame.grid_remove()

activeFrame.columnconfigure(0, weight=1, uniform='LeftRightFrameGrouping')
activeFrame.columnconfigure(1, weight=1, uniform='LeftRightFrameGrouping')
activeFrame.rowconfigure(0, weight=1)
##END Primary Frame


menu_frame = Frame(rootFrame)

##Bottom Frame;A Button bar...
bottomFrame = Frame(rootFrame, bd=1, relief=SOLID)
bottomFrame.grid(column=0, row=4, columns=10, sticky='SEW')

bottomStatusTEXT = Label(bottomFrame, text='Loading Status Updates....', bg=display_color, anchor='w')
bottomStatusTEXT.grid(sticky='NSEW')

bottomFrame.columnconfigure(0, weight=1)

##END Bottom FRame


######################START CLIENT FOR REMOTE COMMAND FUNCTIONS################################

import socket
import sys


def sendCMD(function, **kwargs):
    try:
        # print(kwargs.keys())
        # print(kwargs.get('siteID'))
        if 'siteID' in kwargs:
            argSiteid = kwargs['siteID']
        else:
            argSiteid = ''
        if 'sysID' in kwargs:
            argSysid = kwargs['sysID']
        else:
            argSysid = ''
        if 'rrUser' in kwargs:
            argrrUser = kwargs['rrUser']
        else:
            argrrUser = ''
        if 'rrPass' in kwargs:
            argrrPass = kwargs['rrPass']
        else:
            argrrPass = ''

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('192.168.122.25', 10000)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)

        # Send data
        # message = b'This is the message.  It will be repeated.'
        message = function + ', ' + str(kwargs)
        bytemsg = bytes(message, 'utf-8')
        print('sending {!r}'.format(bytemsg))
        sock.sendall(bytemsg)

        # Look for the response
        amount_received = 0
        amount_expected = len(bytemsg)

        while amount_received < amount_expected:
            data = sock.recv(1028)
            amount_received += len(data)
            # print('received {!r}'.format(data))
            if data == bytemsg:
                print('Data Match Verified')
                # re.findall("^(.*)", data.decode('utf-8'))
                sysmsgUPDATE(text='Remote: ACK from CMD: ' + str(data.decode('utf-8').split(",")[0]), bg='green')
            else:
                sock.sendall(bytemsg)
                sysmsgUPDATE(text='Remote: Ack not Found, Retrying...', bg='red')
    except Exception as e:
        # print(e)
        print('Server not started: is your remote script runnning?')
        sysmsgUPDATE(text='ERROR: Couldn\'t Contact OP25 Instance', bg='red')

    finally:
        print('closing socket')
        sock.close()


# sendCMD('disableblacklistrange')

###########################################
#####END CLIENT CONNECTION


##Left Primary Column Sub-Frames

##Row 0;Talkgroup and Alpha Tag Frame
lefttalkgroupFrame = Frame(leftFrame, bd=1, relief=SOLID)
lefttalkgroupFrame.grid(column=0, row=0, sticky='NESW')
# Label(lefttalkgroupFrame, text='Talkgroup Frame').grid()
leftFrame.columnconfigure(0, weight=1)

leftalphaFrame = Frame(lefttalkgroupFrame, bd=1, relief=SOLID)
leftalphaFrame.grid(column=0, row=0, rows=5, sticky='NESW')
# Label(leftalphaFrame, text='Alpha Tag Frame').grid()
lefttalkgroupFrame.columnconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(4, weight=1, uniform='addrs')
lefttalkgroupFrame.rowconfigure(5, weight=1, uniform='addrs')

leftstatusFrame = Frame(leftalphaFrame)
leftstatusFrame.grid(column=0, row=0, columns=10, sticky='NEW')
leftalphaFrame.columnconfigure(0, weight=1)

leftbuttonFrame = Frame(lefttalkgroupFrame, bd=1, relief=SOLID)
leftbuttonFrame.grid(column=1, row=0, rows=3, sticky='NESW')
# Label(leftbuttonFrame, text='left Status Frame').grid()
lefttalkgroupFrame.columnconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(0, weight=1)
##END Row0;Talkgroup and Alpha Tag Frame

##Row1;Alert Frame;CAll Alerts;Notifications
rightalertFrame = Frame(rightFrame, bd=1, relief=SOLID)
rightalertFrame.grid(column=0, row=0, sticky='NESW')
# Label(rightalertFrame, text='Alert Frame').grid()
leftFrame.columnconfigure(0, weight=1)
##END Row1;Alert Frame

# Row2;System Detail Frame
leftsysFrame = Frame(leftFrame, bd=1, relief=SOLID)
leftsysFrame.grid(column=0, row=2, sticky='NESW')
#Label(leftsysFrame, text='System Detail Frame').grid()
modeTEXT = Label(leftsysFrame, text='Mode: ', bg=display_color)
modeTEXT.grid()
leftFrame.columnconfigure(0, weight=1)

leftFrame.rowconfigure(0, weight=1, uniform='LeftFrameRowGrouping')
leftFrame.rowconfigure(1, weight=1, uniform='LeftFrameRowGrouping')
leftFrame.rowconfigure(2, weight=1, uniform='LeftFrameRowGrouping')
# END Row2;System Detail Frame

##END Left Primary Column Sub-Frames

##Right Primary Column Sub-Frames
leftsiteFrame = Frame(leftFrame, bd=1, relief=SOLID)
leftsiteFrame.grid(column=0, row=1, sticky='NESW')
# Label(leftsiteFrame, text='Right Site Frame').grid()
rightFrame.columnconfigure(0, weight=1)

rightdetailsFrame = Frame(leftsiteFrame, bd=1, relief=SOLID)
rightdetailsFrame.grid(column=0, row=0, rows=4, sticky='NESW')
# Label(rightdetailsFrame, text='Right Site Details Frame').grid()

righttxrxFrame = Frame(rightdetailsFrame)
righttxrxFrame.grid(column=0, row=3, sticky='EW')

leftcompassFrame = Frame(leftsiteFrame, bd=1, relief=SOLID)
leftcompassFrame.grid(column=1, row=0, sticky='NESW')
# Label(leftcompassFrame, text='Right Site Compass Frame').grid()


leftsiteFrame.columnconfigure(0, weight=1)
leftsiteFrame.columnconfigure(1, weight=0)
leftsiteFrame.rowconfigure(0, weight=1)

rightlogFrame = Frame(rightFrame, bd=1, relief=SOLID)
rightlogFrame.grid(column=0, row=1, sticky='NESW')
rightFrame.columnconfigure(0, weight=1)
rightFrame.rowconfigure(0, weight=1)


def nightmodebuttonFUNC():
    nightmodePrompt.grid_remove()


nightmodePrompt = Frame(rootFrame, bd=5, relief=RAISED)
# nightmodePrompt.grid(row=1, column=0)


nightModeTEXT = Label(nightmodePrompt, text='', bg='black', fg='white', justify=LEFT, font=("Courier", 25), bd=5,
                      relief=RAISED)
nightModeTEXT.grid(row=0, column=0)

nightmodeokBTN = Button(nightmodePrompt, text='       OK       ', command=nightmodebuttonFUNC)
nightmodeokBTN.grid(row=0, column=1, sticky='NESW')
nightmodePrompt.columnconfigure(1, weight=1)


def nouriFUNC():
    print(nouriENT.get())
    config.set('Pi25MCH', 'uri', nouriENT.get())
    write_file()
    if config.get('Pi25MCH', 'uri') != str(nouriENT.get()):
        config.set('Pi25MCH', 'uri', nouriENT.get())
        write_file()
    else:
        time.sleep(1)
        t = threading.Thread(target=update)
        if not t.is_alive():
            t.start()
        # t2 = threading.Thread(target=nightMode)
        # t2.start()

        nouriPrompt.grid_remove()


nouriPrompt = Frame(rootFrame, bd=5, relief=RAISED)
# nouriPrompt.grid(row=1, column=0)


nouriTEXT = Label(nouriPrompt, text='OP25 Web Server', fg='black', justify=CENTER, font=("Courier", 25), bd=5,
                  relief=RAISED)
nouriTEXT.grid(column=0, row=0, columnspan=2)

nouriENT = Entry(nouriPrompt)

if not config.has_section('Pi25MCH'):
    config.add_section('Pi25MCH')

if not config.get('Pi25MCH', 'uri'):
    nouriENT.insert(0, 'http://ip_address_to_OP25:port')
else:
    nouriENT.insert(0, config.get('Pi25MCH', 'uri'))
nouriENT.grid(column=0, row=1, columnspan=2, sticky='WE')

nouriBTN = Button(nouriPrompt, text='SAVE', command=nouriFUNC)
nouriBTN.grid(column=0, row=2)

nouriBTN = Button(nouriPrompt, text='CANCEL', command=lambda: nouriPrompt.grid_forget())
nouriBTN.grid(column=1, row=2)

##Tabbed Window Start

# style = ttk.Style()

# noteStyle = ttk.Style()

# noteStyle.theme_use('default')
# noteStyle.configure("TNotebook", background=display_color, borderwidth=0)
# noteStyle.configure("TNotebook.Tab", borderwidth=0, padding=25, width=10000)
# noteStyle.map("TNotebook", background=[("selected", display_color)])


style = ttk.Style()
style.theme_create('Cloud', settings={
    ".": {
        "configure": {
            "background": '#aeb0ce',  # All colors except for active tab-button
            "font": 'red'
        }
    },
    "TNotebook": {
        "configure": {
            "background": 'lightgray',  # color behind the notebook
            "tabmargins": [5, 5, 0, 0],  # [left margin, upper margin, right margin, margin beetwen tab and frames]
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "background": 'lightgray',  # Color of non selected tab-button
            "padding": [20, 20],
            # [space beetwen text and horizontal tab-button border, space between text and vertical tab_button border]
            "font": "white",
            "width": 1000,
            "borderwidth": 2
        },
        "map": {
            "background": [("selected", 'grey')],  # Color of active tab
            "expand": [("selected", [1, 1, 1, 0])]  # [expanse of text]
        }
    }
})

style.theme_create('Nightmode', settings={
    ".": {
        "configure": {
            "background": '#aeb0ce',  # All colors except for active tab-button
            "font": 'red'
        }
    },
    "TNotebook": {
        "configure": {
            "background": 'black',  # color behind the notebook
            "tabmargins": [5, 5, 0, 0],  # [left margin, upper margin, right margin, margin beetwen tab and frames]
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "background": 'lightgray',  # Color of non selected tab-button
            "padding": [20, 20],
            # [space beetwen text and horizontal tab-button border, space between text and vertical tab_button border]
            "font": "white",
            "width": 1000,
            "borderwidth": 2
        },
        "map": {
            "background": [("selected", 'grey')],  # Color of active tab
            "expand": [("selected", [1, 1, 1, 0])]  # [expanse of text]
        }
    }
})

style.theme_use('Cloud')

logTAB = ttk.Notebook(rightlogFrame)
rightlogFrame.columnconfigure(0, weight=1)
rightlogFrame.rowconfigure(0, weight=1)

# Tab1
callTAB1 = Frame(logTAB, bg='lightgray')
logTAB.add(callTAB1, text='Call Log', sticky='NESW')

# Tab2
syslogTAB2 = Frame(logTAB, bg='lightgray')
logTAB.add(syslogTAB2, text='Sys Log', sticky='NESW')

# Tab3
themegTAB3 = Frame(logTAB, bg='lightgray')
#logTAB.add(themegTAB3, text='Theme', sticky='NESW')

logTAB.grid(column=0, row=0, sticky='NESW')

logTAB.columnconfigure(0, weight=1)
logTAB.rowconfigure(0, weight=1)

# Tab4

scanGridTAB4 = Frame(logTAB, bg='lightgray')
# logTAB.add(scanGridTAB4, text='ScanGrid', sticky='NESW')

##Tabbed Frames END


rightFrame.rowconfigure(0, weight=1, uniform='RightFrameRowGrouping')
rightFrame.rowconfigure(1, weight=2, uniform='RightFrameRowGrouping')
##END Right Primary Column Sub-Frames

##StatusFrame Labels and Positions

##END StatusFrame Labels and Positions

##AlphaTag Frame Labels and Positions
statusTEXT = Label(leftstatusFrame, text="System Placeholder", bg=display_color, font=('Digital-7 Mono', 15))
statusTEXT.grid(column=0, row=0, sticky='W')

tagTEXT = Label(leftalphaFrame, text="Connecting...", bg=display_color, font=('Digital-7 Mono', 32), anchor=SW,
                justify=LEFT)
tagTEXT.grid(column=0, row=1, sticky='NW')

bothaddrTEXT = Label(leftalphaFrame, bg=display_color, font=('Digital-7 Mono', 15), anchor=SW, justify=LEFT)
bothaddrTEXT.grid(column=0, row=2, rowspan=2, sticky='NW')

##END AlphaTag Frame Labels and Positions

##Left Status Frame labels and Positions
grpTEXT = Label(rightdetailsFrame, text="")  # give holdbutn my text
holdBTN = Button(leftbuttonFrame, text="HOLD", bg='lightgray', font=('Digital-7 Mono', 22),
                 command=lambda: holdFUNC(grpTEXT.cget('text')))  ###CONTAINS PLACEHOLDER TEXT
holdBTN.grid(column=0, row=0, sticky='nesw')

gotoBTN = Button(leftbuttonFrame, text="GOTO", bg='lightgray', font=('Digital-7 Mono', 22), relief=RAISED,
                 command=gotoFUNC)  ###CONTAINS PLACEHOLDER TEXT
gotoBTN.grid(column=0, row=1, sticky='nesw')

lockoutBTN = Button(leftbuttonFrame, text="LOCK", bg='lightgray', font=('Digital-7 Mono', 22), command=lockoutFUNC)
lockoutBTN.grid(column=0, row=3, sticky='nesw')

skipBTN = Button(leftbuttonFrame, text="SKIP", bg='lightgray', font=('Digital-7 Mono', 22),
                 command=skipFUNC)  ###CONTAINS PLACEHOLDER TEXT
skipBTN.grid(column=0, row=2, sticky='nesw')

leftbuttonFrame.rowconfigure(0, weight=1)
leftbuttonFrame.rowconfigure(1, weight=1)
leftbuttonFrame.rowconfigure(2, weight=1)
leftbuttonFrame.rowconfigure(3, weight=1)


##END Left Status Frame Labels and Positions

def d(event):
    framewidth = int(event.width / 20)
    holdBTN.configure(width=framewidth)
    gotoBTN.configure(width=framewidth)
    skipBTN.configure(width=framewidth)


leftcompassFrame.bind("<Configure>", d)


##Right Keypad Frame
def keypadFUNC(int):
    keypadEntry.insert(20, str(int))


def keypadentFUNC(input):
    rightkeypadFrame.grid_remove()
    value = keypadEntry.get()
    keypadEntry.delete(0, 'end')
    # requests.post(op25uri, json=[{"command": "hold", "arg1": int(value), "arg2": 0}, {"command": "update", "arg1": 0, "arg2": 0}])
    jsoncmd('hold', int(value), 0)
    sysmsgUPDATE(text='Going to and Holding Talkgroup: ' + str(input), bg='green')
    jsoncmd('update', 0, 0)
    holdBTN.configure(fg='red', relief=SUNKEN, text=input)
    gotoBTN.configure(relief=RAISED)


def keypadclearFUNC():
    keypadEntry.delete(0, 'end')


keypadEntry = Entry(rightkeypadFrame, text='', bg='gray', justify=CENTER, font=('Digital-7 Mono', 25))
keypadEntry.grid(row=0, column=0, columnspan=3, sticky='NESW')

keypad7BTN = Button(rightkeypadFrame, text='7', bg='lightgray', command=lambda: keypadFUNC(7))
keypad7BTN.grid(row=1, column=0, sticky='NESW')

keypad8BTN = Button(rightkeypadFrame, text='8', bg='lightgray', command=lambda: keypadFUNC(8))
keypad8BTN.grid(row=1, column=1, sticky='NESW')

keypad9BTN = Button(rightkeypadFrame, text='9', bg='lightgray', command=lambda: keypadFUNC(9))
keypad9BTN.grid(row=1, column=2, sticky='NESW')

keypad4BTN = Button(rightkeypadFrame, text='4', bg='lightgray', command=lambda: keypadFUNC(4))
keypad4BTN.grid(row=2, column=0, sticky='NESW')

keypad5BTN = Button(rightkeypadFrame, text='5', bg='lightgray', command=lambda: keypadFUNC(5))
keypad5BTN.grid(row=2, column=1, sticky='NESW')

keypad6BTN = Button(rightkeypadFrame, text='6', bg='lightgray', command=lambda: keypadFUNC(6))
keypad6BTN.grid(row=2, column=2, sticky='NESW')

keypad1BTN = Button(rightkeypadFrame, text='1', bg='lightgray', command=lambda: keypadFUNC(1))
keypad1BTN.grid(row=3, column=0, sticky='NESW')

keypad2BTN = Button(rightkeypadFrame, text='2', bg='lightgray', command=lambda: keypadFUNC(2))
keypad2BTN.grid(row=3, column=1, sticky='NESW')

keypad3BTN = Button(rightkeypadFrame, text='3', bg='lightgray', command=lambda: keypadFUNC(3))
keypad3BTN.grid(row=3, column=2, sticky='NESW')

keypad0BTN = Button(rightkeypadFrame, text='0', bg='lightgray', command=lambda: keypadFUNC(0))
keypad0BTN.grid(row=4, column=0, sticky='NESW')

keypadclearBTN = Button(rightkeypadFrame, text='CLEAR', bg='lightgray', command=keypadclearFUNC)
keypadclearBTN.grid(row=4, column=1, sticky='NESW')

keypadentBTN = Button(rightkeypadFrame, text='ENTER', bg='lightgray', command=lambda: keypadentFUNC(keypadEntry.get()))
keypadentBTN.grid(row=4, column=2, sticky='NESW')

rightkeypadFrame.columnconfigure(0, weight=1)
rightkeypadFrame.columnconfigure(1, weight=1)
rightkeypadFrame.columnconfigure(2, weight=1)

rightkeypadFrame.rowconfigure(0, weight=1, uniform='keypadRow')
rightkeypadFrame.rowconfigure(1, weight=1, uniform='keypadRow')
rightkeypadFrame.rowconfigure(2, weight=1, uniform='keypadRow')
rightkeypadFrame.rowconfigure(3, weight=1, uniform='keypadRow')
rightkeypadFrame.rowconfigure(4, weight=1, uniform='keypadRow')

##END Right Keypad Frame

##RIght Site details Frame

nacwacnTEXT = Label(rightdetailsFrame, text=" "*40, bg=display_color, font=('Digital-7 Mono', 20))
nacwacnTEXT.grid(column=0, row=0)

sysidTEXT = Label(rightdetailsFrame, text="", bg=display_color, font=('Digital-7 Mono', 20))
sysidTEXT.grid(column=0, row=1, sticky='W')

adjacent_dataTEXT = Label(rightdetailsFrame, text="", bg=display_color, font=('Digital-7 Mono', 22))
#adjacent_dataTEXT.grid(column=0, row=2)

frequenciesTEXT = Label(rightdetailsFrame, text="", bg=display_color, font=('Digital-7 Mono', 15))
#frequenciesTEXT.grid(column=0, row=3)

# Label(rightdetailsFrame, text='Placeholder line 2', font=('Digital-7 Mono', 15), bg=display_color).grid(row=1, column=0, sticky='W')

systemTEXT = Label(righttxrxFrame, text="", bg=display_color, font=('Digital-7 Mono', 32), anchor=SW,
                   justify=LEFT)  ###CONTAINS PLACEHOLDER TEXT
systemTEXT.grid(column=0, row=0, sticky='Se')

bothrxtxTEXT = Label(righttxrxFrame, text="", bg=display_color, font=('Digital-7 Mono', 12))
bothrxtxTEXT.grid(column=2, row=0, rowspan=2, ipady=10, sticky='EW')

rightdetailsFrame.rowconfigure(0, weight=1)
rightdetailsFrame.rowconfigure(1, weight=1)
rightdetailsFrame.rowconfigure(2, weight=1)

leftsiteFrame.columnconfigure(3, weight=1)

##END Right site details frame


encTEXT = Label(rightalertFrame, text="ENCRYPTED CHANNEL Ø", bg=display_color, fg='grey', font=('Digital-7 Mono', 10))
encTEXT.grid(column=0, row=0, columnspan=4, sticky='NSEW')

alertTEXT = Button(rightalertFrame, text='TSV Loaded', bg=display_color, fg='gray', font=('Digital-7 Mono', 40), bd=0, activebackground=display_color, command=lambda: holdFUNC(grpTEXT.cget('text')))
alertTEXT.grid(row=1, column=0, columnspan=4, sticky='NSEW')

row3alertTEXT = Label(rightalertFrame, text='', bg=display_color, fg='grey', font=('Digital-7 Mono', 10))
row3alertTEXT.grid(row=2, column=0, columnspan=4, sticky='NSEW')

rightalertFrame.rowconfigure(0, weight=1, uniform='alerts')
rightalertFrame.rowconfigure(1, weight=2, uniform='alerts')
rightalertFrame.rowconfigure(2, weight=1, uniform='alerts')


def openmenuFUNC():
    menu_frame.grid(column=0, row=0, rowspan=2, sticky='NESW')


def closemenuFUNC():
    menu_frame.grid_remove()


##MENU BUTTON;column4 while systemstatusframe of displayframe is a columnspan of 4 keeping it outside the primary frame
menuBTN = Button(rightalertFrame, text=" ≡ ", bg='lightgray', activebackground='gray', font=('Digital-7 Mono', 12),
                 command=openmenuFUNC)
menuBTN.grid(row=0, column=5, sticky='NE')
##MENU BUTTON

rightalertFrame.columnconfigure(0, weight=1)

# Label(leftcompassFrame, text='placeholder').grid(row=0, column=0, sticky='nsew')


compassRangeTEXT = Label(leftcompassFrame, text='15 Miles', bg=display_color)
compassRangeTEXT.grid(row=0, column=1, sticky='NESW')

##Right Site Compass Frame
img = Image.open('static/images/compass.png').rotate(0)  # .rotate(compassRotate(bearing))

tkimage = ImageTk.PhotoImage(img)
compassIMG = Label(leftcompassFrame, image=tkimage, bg=display_color)
compassIMG.grid(row=1, column=1, sticky='NESW')

leftcompassFrame.rowconfigure(0, weight=1)
leftcompassFrame.rowconfigure(1, weight=1)
leftcompassFrame.columnconfigure(0, weight=1)
leftcompassFrame.columnconfigure(1, weight=1)

tuneBTN = Button(leftcompassFrame, text='TUNE', width=10, bg='lightgray')
# tuneBTN.grid(column=0, row=0, sticky='NESW')


##END Right Site Compass Frame

# Tab Name Labels
# tab1Label = Label(callTAB1, text="This is Tab 1", bg=display_color)
call_logTEXT = Text(callTAB1, bg='gray', relief=SOLID)
call_logTEXT.grid(column=0, row=0, padx=2, pady=2, sticky='NESW')

callTAB1.rowconfigure(0, weight=1)
callTAB1.columnconfigure(0, weight=1)

syslogsyslogTAB2Label = Label(syslogTAB2, text="This is Tab 2", bg='lightgray')

syslogsyslogTAB2Label.grid(column=1, row=0, padx=10, pady=10, sticky='NESW')

sys_logTEXT = Text(syslogTAB2, bg='gray', relief=SOLID)
sys_logTEXT.grid(column=0, row=0, padx=2, pady=2, sticky='NESW')



#themegTAB3.rowconfigure(0, weight=1)
#themegTAB3.rowconfigure(1, weight=1)

#themegTAB3.columnconfigure(0, weight=1)
#themegTAB3.columnconfigure(1, weight=1)
#themegTAB3.columnconfigure(2, weight=1)

dbfilename = 'scangrid.db'
scangridDB = configparser.ConfigParser()


def write_scangridDB():
    scangridDB.write(open(dbfilename, 'w'))


def scangridDBwriter(argsection, argoption, argvalue):
    if argsection in scangridDB.sections():
        scangridDB.set(section=argsection, option=argoption, value=argvalue)
        write_scangridDB()
    else:
        scangridDB.add_section(argsection)
        scangridDB.set(section=argsection, option=argoption, value=argvalue)
        write_scangridDB()

if os.path.exists('scangrid.db'):
    os.remove('scangrid.db')

scangridDBwriter('ScanGridState', 'fileDescription', 'This file stores the values of the scanGrid. It is rebuilt at run-time.')


def scangridSaver():
    selection = scanlistVar.get()

    relief1 = gridtabBTN1.cget('relief')
    bg1 = gridtabBTN1.cget('bg')

    relief2 = gridtabBTN2.cget('relief')
    bg2 = gridtabBTN2.cget('bg')

    relief3 = gridtabBTN3.cget('relief')
    bg3 = gridtabBTN3.cget('bg')

    relief4 = gridtabBTN4.cget('relief')
    bg4 = gridtabBTN4.cget('bg')

    relief5 = gridtabBTN5.cget('relief')
    bg5 = gridtabBTN5.cget('bg')

    relief6 = gridtabBTN6.cget('relief')
    bg6 = gridtabBTN6.cget('bg')

    relief7 = gridtabBTN7.cget('relief')
    bg7 = gridtabBTN7.cget('bg')

    relief8 = gridtabBTN8.cget('relief')
    bg8 = gridtabBTN8.cget('bg')

    relief9 = gridtabBTN9.cget('relief')
    bg9 = gridtabBTN9.cget('bg')

    relief10 = gridtabBTN10.cget('relief')
    bg10 = gridtabBTN10.cget('bg')

    relief11 = gridtabBTN11.cget('relief')
    bg11 = gridtabBTN11.cget('bg')

    relief12 = gridtabBTN12.cget('relief')
    bg12 = gridtabBTN12.cget('bg')

    relief13 = gridtabBTN13.cget('relief')
    bg13 = gridtabBTN13.cget('bg')

    relief14 = gridtabBTN14.cget('relief')
    bg14 = gridtabBTN14.cget('bg')

    relief15 = gridtabBTN15.cget('relief')
    bg15 = gridtabBTN15.cget('bg')

    relief16 = gridtabBTN16.cget('relief')
    bg16 = gridtabBTN16.cget('bg')


    if not scangridDB.has_section(section=selection):
        print(selection + ' was not found in the database, adding...')
        scangridDB.add_section(selection)
        scangridDBwriter(selection, 'btn1', relief1)
        scangridDBwriter(selection, 'btn2', relief2)
        scangridDBwriter(selection, 'btn3', relief3)
        scangridDBwriter(selection, 'btn4', relief4)
        scangridDBwriter(selection, 'btn5', relief5)
        scangridDBwriter(selection, 'btn6', relief6)
        scangridDBwriter(selection, 'btn7', relief7)
        scangridDBwriter(selection, 'btn8', relief8)
        scangridDBwriter(selection, 'btn9', relief9)
        scangridDBwriter(selection, 'btn10', relief10)
        scangridDBwriter(selection, 'btn11', relief11)
        scangridDBwriter(selection, 'btn12', relief12)
        scangridDBwriter(selection, 'btn13', relief13)
        scangridDBwriter(selection, 'btn14', relief14)
        scangridDBwriter(selection, 'btn15', relief15)
        scangridDBwriter(selection, 'btn16', relief16)
    if scangridDB.has_section(section=selection):
        print(selection + ' found in database, updating...')
        scangridDB.set(selection, 'btn1', relief1)
        scangridDB.set(selection, 'btn2', relief2)
        scangridDB.set(selection, 'btn3', relief3)
        scangridDB.set(selection, 'btn4', relief4)
        scangridDB.set(selection, 'btn5', relief5)
        scangridDB.set(selection, 'btn6', relief6)
        scangridDB.set(selection, 'btn7', relief7)
        scangridDB.set(selection, 'btn8', relief8)
        scangridDB.set(selection, 'btn9', relief9)
        scangridDB.set(selection, 'btn10', relief10)
        scangridDB.set(selection, 'btn11', relief11)
        scangridDB.set(selection, 'btn12', relief12)
        scangridDB.set(selection, 'btn13', relief13)
        scangridDB.set(selection, 'btn14', relief14)
        scangridDB.set(selection, 'btn15', relief15)
        scangridDB.set(selection, 'btn16', relief16)
        write_scangridDB()






    '''  
    if selection in scangridstateFile:
        print('Found ' + selection + ' in file updating...')
        gridsplit = scangridstateFile.split('\n')
        #print(gridsplit[1])#Start your iteration at #1 to skip the 'help' text in your db file
        splitcounter = 0
        for i in gridsplit:
            print(str(splitcounter) + i)
            if selection in i:
                print('Original in File' + i)
                i.replace(i[splitcounter], str(gridDict))
                print('Replaced in File' + i[splitcounter])

            else:
                pass

            splitcounter = splitcounter + 1
    else:
        print('Could not find ' + selection + ' in file, adding...')
        scangridstateFile = open(filename, 'a+')
        scangridstateFile.write(str(gridDict) + '\n')
'''

##END Tab 3

##START Tab 4

def gridtab1Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN1.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN1.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab2Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN2.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN2.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab3Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN3.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN3.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab4Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN4.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN4.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab5Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN5.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN5.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab6Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN6.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN6.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab7Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN7.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN7.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab8Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN8.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN8.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab9Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN9.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN9.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab10Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN10.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN10.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab11Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN11.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN11.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab12Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN12.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN12.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab13Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN13.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN13.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab14Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN14.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN14.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab15Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN15.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN15.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

def gridtab16Func(buttontext, buttonrelief):
    btnsplit = buttontext.split('\n')
    tgid = btnsplit[0]
    tgtag = btnsplit[1]
    if buttonrelief == RAISED:
        jsoncmd('whitelist', int(tgid), 0)
        sysmsgUPDATE(text='Whitelisting Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN16.configure(relief=SUNKEN, bg='gray')
    if buttonrelief == SUNKEN:
        jsoncmd('lockout', int(tgid), 0)
        sysmsgUPDATE(text='Locking out Talkgroup: ' + str(tgid), bg='green')
        gridtabBTN16.configure(relief=RAISED, bg='SystemButtonFace')
    scangridSaver()

##GET LIST OF SCANLIST FILES

scangridfiles = []
for (dirpath, dirnames, filenames) in walk('scan/'):
    scangridfiles.extend(filenames)
    break

if scangridfiles == []:
    defaultscangridTSV = open('scan/default.tsv', 'w')
    defaultscangridTSV.write(
        '0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n0000\tPlaceholder\n')
    defaultscangridTSV.close()

    scangridfiles = []
    for (dirpath, dirnames, filenames) in walk('scan/'):
        scangridfiles.extend(filenames)
        break


# print(f)
##END GET LIST OF SCANLIST FILES

def loadscangridFUNC(selection):
    setscangridFUNC(selection)
    ##IF exists then configure, otherwise configure default
    #scangridDB.read(dbfilename)
    #scangridDB.get(selection, 'fileDescription')

    if scangridDB.has_section(selection):
        btn1 = scangridDB.get(selection, 'btn1')
        if btn1 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN1.configure(relief=btn1, bg=bg)

        btn2 = scangridDB.get(selection, 'btn2')
        if btn2 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN2.configure(relief=btn2, bg=bg)

        btn3 = scangridDB.get(selection, 'btn3')
        if btn3 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN3.configure(relief=btn3, bg=bg)

        btn4 = scangridDB.get(selection, 'btn4')
        if btn4 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN4.configure(relief=btn4, bg=bg)

        btn5 = scangridDB.get(selection, 'btn5')
        if btn5 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN5.configure(relief=btn5, bg=bg)

        btn6 = scangridDB.get(selection, 'btn6')
        if btn6 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN6.configure(relief=btn6, bg=bg)

        btn7 = scangridDB.get(selection, 'btn7')
        if btn7 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN7.configure(relief=btn7, bg=bg)

        btn8 = scangridDB.get(selection, 'btn8')
        if btn8 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN8.configure(relief=btn8, bg=bg)

        btn9 = scangridDB.get(selection, 'btn9')
        if btn9 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN9.configure(relief=btn9, bg=bg)

        btn10 = scangridDB.get(selection, 'btn10')
        if btn10 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN10.configure(relief=btn10, bg=bg)

        btn11 = scangridDB.get(selection, 'btn11')
        if btn11 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN11.configure(relief=btn11, bg=bg)

        btn12 = scangridDB.get(selection, 'btn12')
        if btn12 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN12.configure(relief=btn12, bg=bg)

        btn13 = scangridDB.get(selection, 'btn13')
        if btn13 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN13.configure(relief=btn13, bg=bg)

        btn14 = scangridDB.get(selection, 'btn14')
        if btn14 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN14.configure(relief=btn14, bg=bg)

        btn15 = scangridDB.get(selection, 'btn15')
        if btn15 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN15.configure(relief=btn15, bg=bg)

        btn16 = scangridDB.get(selection, 'btn16')
        if btn16 == 'sunken':
            bg = 'gray'
        else:
            bg = 'SystemButtonFace'
        gridtabBTN16.configure(relief=btn16, bg=bg)
    if not scangridDB.has_section(selection):
        gridtabBTN1.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN2.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN3.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN4.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN5.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN6.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN7.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN8.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN9.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN10.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN11.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN12.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN13.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN14.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN15.configure(relief=RAISED, bg='SystemButtonFace')
        gridtabBTN16.configure(relief=RAISED, bg='SystemButtonFace')


scanlistVar = StringVar()
scanlistVar.set('Select a ScanGrid TSV File to Load')

gridtabDRPDWN = OptionMenu(scanGridTAB4, scanlistVar, *scangridfiles, command=loadscangridFUNC)
gridtabDRPDWN.grid(column=0, row=0, columnspan=4, sticky='NESW')

##Row 1 Start
gridtabBTN1 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab1Func(gridtabBTN1.cget('text'), gridtabBTN1.cget('relief')))
gridtabBTN1.grid(column=0, row=1, sticky='NESW')

gridtabBTN2 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab2Func(gridtabBTN2.cget('text'), gridtabBTN2.cget('relief')))
gridtabBTN2.grid(column=1, row=1, sticky='NESW')

gridtabBTN3 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab3Func(gridtabBTN3.cget('text'), gridtabBTN3.cget('relief')))
gridtabBTN3.grid(column=2, row=1, sticky='NESW')

gridtabBTN4 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab4Func(gridtabBTN4.cget('text'), gridtabBTN4.cget('relief')))
gridtabBTN4.grid(column=3, row=1, sticky='NESW')
# Row 1 End

# Row 2 Start
gridtabBTN5 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab5Func(gridtabBTN5.cget('text'), gridtabBTN5.cget('relief')))
gridtabBTN5.grid(column=0, row=2, sticky='NESW')

gridtabBTN6 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab6Func(gridtabBTN6.cget('text'), gridtabBTN6.cget('relief')))
gridtabBTN6.grid(column=1, row=2, sticky='NESW')

gridtabBTN7 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab7Func(gridtabBTN7.cget('text'), gridtabBTN7.cget('relief')))
gridtabBTN7.grid(column=2, row=2, sticky='NESW')

gridtabBTN8 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab8Func(gridtabBTN8.cget('text'), gridtabBTN8.cget('relief')))
gridtabBTN8.grid(column=3, row=2, sticky='NESW')
# Row 2 End


# Row 3 Start
gridtabBTN9 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                     command=lambda: gridtab9Func(gridtabBTN9.cget('text'), gridtabBTN9.cget('relief')))
gridtabBTN9.grid(column=0, row=3, sticky='NESW')

gridtabBTN10 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab10Func(gridtabBTN10.cget('text'), gridtabBTN10.cget('relief')))
gridtabBTN10.grid(column=1, row=3, sticky='NESW')

gridtabBTN11 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab11Func(gridtabBTN11.cget('text'), gridtabBTN11.cget('relief')))
gridtabBTN11.grid(column=2, row=3, sticky='NESW')

gridtabBTN12 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab12Func(gridtabBTN12.cget('text'), gridtabBTN12.cget('relief')))
gridtabBTN12.grid(column=3, row=3, sticky='NESW')
# Row 3 End


# Row 4 Start
gridtabBTN13 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab13Func(gridtabBTN13.cget('text'), gridtabBTN13.cget('relief')))
gridtabBTN13.grid(column=0, row=4, sticky='NESW')

gridtabBTN14 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab14Func(gridtabBTN14.cget('text'), gridtabBTN14.cget('relief')))
gridtabBTN14.grid(column=1, row=4, sticky='NESW')

gridtabBTN15 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab15Func(gridtabBTN15.cget('text'), gridtabBTN15.cget('relief')))
gridtabBTN15.grid(column=2, row=4, sticky='NESW')

gridtabBTN16 = Button(scanGridTAB4, text='GridScan TSV\rNot Loaded',
                      command=lambda: gridtab16Func(gridtabBTN16.cget('text'), gridtabBTN16.cget('relief')))
gridtabBTN16.grid(column=3, row=4, sticky='NESW')
# Row 4 End

scanGridTAB4.columnconfigure(0, weight=1, uniform='scangrid')
scanGridTAB4.columnconfigure(1, weight=1, uniform='scangrid')
scanGridTAB4.columnconfigure(2, weight=1, uniform='scangrid')
scanGridTAB4.columnconfigure(3, weight=1, uniform='scangrid')

scanGridTAB4.rowconfigure(0, weight=1, uniform='scangridrow')
scanGridTAB4.rowconfigure(1, weight=1, uniform='scangridrow')
scanGridTAB4.rowconfigure(2, weight=1, uniform='scangridrow')
scanGridTAB4.rowconfigure(3, weight=1, uniform='scangridrow')
scanGridTAB4.rowconfigure(4, weight=1, uniform='scangridrow')


##END Tab 4


def setscangridFUNC(selection):  #############################YOU NEED TO LOCKOUT EVERYTHING WHEN YOU SWITCH SCANLISTS
    from os import walk

    scangridfiles = []
    for (dirpath, dirnames, filenames) in walk('scan/'):
        scangridfiles.extend(filenames)
        break
    tsvfilecount = 0

    scangridTSV = open("scan/" + selection, "r")
    tsvrow = scangridTSV.read().split("\n")
    tsvcount = 0
    # tsvcolumnTG = tsvcolumn.split("    ")[0]
    # tsvcolumnTAG = tsvcolumn.split("    ")[1]
    # print('TG: ' + tsvcolumnTG + ' TAG: ' + tsvcolumnTAG)

    for i in tsvrow:
        if tsvcount == 0:
            gridtabBTN1.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 1:
            gridtabBTN2.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 2:
            gridtabBTN3.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 3:
            gridtabBTN4.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 4:
            gridtabBTN5.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 5:
            gridtabBTN6.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 6:
            gridtabBTN7.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 7:
            gridtabBTN8.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 8:
            gridtabBTN9.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 9:
            gridtabBTN10.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 10:
            gridtabBTN11.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 11:
            gridtabBTN12.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 12:
            gridtabBTN13.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 13:
            gridtabBTN14.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 14:
            gridtabBTN15.configure(text=tsvrow[tsvcount].replace('\t', '\n'))
        if tsvcount == 15:
            gridtabBTN16.configure(text=tsvrow[tsvcount].replace('\t', '\n'))

        tsvcount = tsvcount + 1
        # gridtabBTN1.configure(text=tsvcolumnTAG)


#setscangridFUNC(scangridfiles[0])
###
###MENU DEVELOPMENT OPEN ON START
###
# openmenuFUNC()
###
###
###


##MENU FRAME
closemenuBTN = Button(menu_frame, text=" ≡ ", bg='lightgray', activebackground='gray', font=('Digital-7 Mono', 12),
                      command=closemenuFUNC)
closemenuBTN.grid(row=0, column=2, sticky='E')

menu_frame.columnconfigure(0, weight=1)
menu_frame.columnconfigure(1, weight=1)
menu_frame.columnconfigure(2, weight=0)

rrloginTEXT = Label(menu_frame, text='Radio Reference')
rrloginTEXT.grid(column=0, row=0, padx=15, pady=0, sticky='NW')

rrloginFrame = Frame(menu_frame, bd=3, relief=GROOVE)
rrloginFrame.grid(column=0, row=1, padx=50, sticky='NW')

usernameTEXT = Label(rrloginFrame, text='Username: ')
usernameTEXT.grid(column=1, row=1, pady=5, padx=5)

usernameENT = Entry(rrloginFrame, text='')
usernameENT.grid(column=2, row=1, columnspan=5, sticky='EW', pady=5, padx=5)

passwordTEXT = Label(rrloginFrame, text='Password: ')
passwordTEXT.grid(column=1, row=2)

passwordENT = Entry(rrloginFrame, text='', show='*')
passwordENT.grid(column=2, row=2, columnspan=4, sticky='EW', pady=5, padx=5)

if 'RadioReference' in config.sections():
    usernameENT.insert(0, config.get('RadioReference', 'rruser'))
    passwordENT.insert(0, config.get('RadioReference', 'rrpass'))


def submitrr():
    confwriter('RadioReference', 'rruser', usernameENT.get())
    confwriter('RadioReference', 'rrpass', passwordENT.get())


rrloginFrame.rowconfigure(4, weight=1)


def clearrrFUNC():
    usernameENT.delete(0, END)
    passwordENT.delete(0, END)


clearrrBTN = Button(rrloginFrame, text='Clear', command=clearrrFUNC)
clearrrBTN.grid(column=4, row=3)

enterrrBTN = Button(rrloginFrame, text='Save', command=submitrr)
enterrrBTN.grid(column=5, row=3, pady=5, padx=5)

defaultSDRTEXT = Label(menu_frame, text='Default SDR Settings')
defaultSDRTEXT.grid(column=0, row=2, padx=15, pady=0, sticky='NW')

defaultSDRFrame = Frame(menu_frame, bd=3, relief=GROOVE)
defaultSDRFrame.grid(column=0, row=3, padx=50, sticky='NESW')

menu_frame.columnconfigure(0, weight=1)

rrimportFrame = Frame(menu_frame, bd=3, relief=GROOVE)
rrimportFrame.grid(column=1, row=1, sticky='NSEW', padx=25)

Pi25SettingsTEXT = Label(menu_frame, text='Pi25 Mobile Control Head Settings')
Pi25SettingsTEXT.grid(column=1, row=2, padx=0, pady=0, sticky='NW')

pi25settingsthemeOverlay = Frame(menu_frame, bd=3, relief=GROOVE)

pi25settingsFrame = Frame(menu_frame, bd=3, relief=GROOVE)
pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')

def updateDisplay_color(color):
    config.set('Pi25MCH', 'display_color', color)
    write_file()
    sysmsgUPDATE('Setting Theme: ' + str(color.upper()), bg='green')
#[pi25settingsthemeOverlay.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW'), pi25settingsFrame.grid_forget()]
##Tab3 Color Picker
tanBTN = Button(pi25settingsthemeOverlay, text='TAN', bg='tan', command=lambda: [colorFUNC('tan'), updateDisplay_color('tan'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
tanBTN.grid(column=0, row=0, sticky='NESW')

blackBTN = Button(pi25settingsthemeOverlay, text='BLK', bg='black', fg='white', command=lambda: [colorFUNC('black'), updateDisplay_color('black'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
blackBTN.grid(column=1, row=0, sticky='NESW')

greenBTN = Button(pi25settingsthemeOverlay, text='GRN', bg='green', command=lambda: [colorFUNC('green'), updateDisplay_color('green'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
greenBTN.grid(column=2, row=0, sticky='NESW')

orangeBTN = Button(pi25settingsthemeOverlay, text='ORG', bg='orange', command=lambda: [colorFUNC('orange'), updateDisplay_color('orange'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
orangeBTN.grid(column=0, row=1, sticky='NESW')

yellowBTN = Button(pi25settingsthemeOverlay, text='YEL', bg='yellow', command=lambda: [colorFUNC('yellow'), updateDisplay_color('yellow'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
yellowBTN.grid(column=1, row=1, sticky='NESW')

pinkBTN = Button(pi25settingsthemeOverlay, text='PNK', bg='pink', command=lambda: [colorFUNC('pink'), updateDisplay_color('pink'), pi25settingsFrame.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW')])
pinkBTN.grid(column=2, row=1, sticky='NESW')

pi25settingsthemeOverlay.rowconfigure(0, weight=1, uniform='pi25themeoverlay')
pi25settingsthemeOverlay.rowconfigure(1, weight=1, uniform='pi25themeoverlay')

pi25settingsthemeOverlay.columnconfigure(0, weight=1, uniform='pi25themeoverlay')
pi25settingsthemeOverlay.columnconfigure(1, weight=1, uniform='pi25themeoverlay')
pi25settingsthemeOverlay.columnconfigure(2, weight=1, uniform='pi25themeoverlay')



#        confwriter(sectionname, 'callLogging', 'False')
###Column 0 and Rows 0-2

def menugridBTN1FUNC():
    sectionname = 'Menu Button Grid'
    if not config.has_section(sectionname):
        config.add_section(sectionname)
        #write_file(
    if 'raised' in menugridBTN1.cget('relief'):
        confwriter(sectionname, 'calllogging', 'True')
        menugridBTN1.configure(relief=SUNKEN)
        #write_file()
    else:
        confwriter(sectionname, 'calllogging', 'False')
        menugridBTN1.configure(relief=RAISED)
        #write_file()


menugridBTN1 = Button(pi25settingsFrame, text='Save Call Log\rTo File', command=menugridBTN1FUNC)
menugridBTN1.grid(column=0, row=0, sticky='NESW')

menugridBTN2 = Button(pi25settingsFrame, text='Update OP25\rURI', command=lambda: nouriPrompt.grid(row=1, column=0))
menugridBTN2.grid(column=0, row=1, sticky='NESW')

menugridBTN3 = Button(pi25settingsFrame, text='Select\rTheme', command=lambda: [pi25settingsthemeOverlay.grid(column=1, row=3, rowspan=3, columns=4, rows=3,  padx=25, sticky='NESW'), pi25settingsFrame.grid_forget()])
menugridBTN3.grid(column=0, row=2, sticky='NESW')

###Column 1 and Rows 0-3

menugridBTN4 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN4.grid(column=1, row=0, sticky='NESW')

menugridBTN5 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN5.grid(column=1, row=1, sticky='NESW')

menugridBTN6 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN6.grid(column=1, row=2, sticky='NESW')

###Column 2 and Rows 0-3


menugridBTN7 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN7.grid(column=2, row=0, sticky='NESW')

menugridBTN8 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN8.grid(column=2, row=1, sticky='NESW')

menugridBTN9 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN9.grid(column=2, row=2, sticky='NESW')

###Column 3 and Rows 0-3

menugridBTN10 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN10.grid(column=3, row=0, sticky='NESW')

menugridBTN11 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN11.grid(column=3, row=1, sticky='NESW')

menugridBTN12 = Button(pi25settingsFrame, text='Unpopulated\rButton')
menugridBTN12.grid(column=3, row=2, sticky='NESW')

pi25settingsFrame.rowconfigure(0, weight=1, uniform='pi25settingsgrid')
pi25settingsFrame.rowconfigure(1, weight=1, uniform='pi25settingsgrid')
pi25settingsFrame.rowconfigure(2, weight=1, uniform='pi25settingsgrid')

pi25settingsFrame.columnconfigure(0, weight=1, uniform='pi25settingsgrid')
pi25settingsFrame.columnconfigure(1, weight=1, uniform='pi25settingsgrid')
pi25settingsFrame.columnconfigure(2, weight=1, uniform='pi25settingsgrid')
pi25settingsFrame.columnconfigure(3, weight=1, uniform='pi25settingsgrid')


#read button config and set buttons
sectionname = 'Menu Button Grid'
if not config.has_section(sectionname):
    config.add_section(sectionname)
    confwriter(sectionname, 'calllogging', 'False')
    # write_file()
if 'True' in config.get(sectionname, 'calllogging'):
    menugridBTN1.configure(relief=SUNKEN)##Save Log to File


def rrpopulateSystems(selection):
    import requests
    from bs4 import BeautifulSoup
    import re

    # rrSearch = 'https://www.radioreference.com/apps/db/?action=regexp&regexp=' + input('State: ')
    rrSearch = 'https://www.radioreference.com/apps/db/?action=regexp&regexp=' + selection
    r = requests.get(rrSearch)

    soup = BeautifulSoup(r.text, features='lxml')
    table = soup.find('table', {"class": "rrtable"})

    items = re.findall("sid(.*)", str(table))

    # print(items)

    count = 0
    result = []

    for i in items:
        test = items[count].split('>')

        sysid = re.findall("\d{1,10}", str(test[0]))[0]
        sysname = test[1].replace('</a', '')
        sysmodulation = test[4].replace('</td', '')
        sysstate = test[10].replace("</td", "")

        if '25' not in sysmodulation:
            count = count + 1
        else:
            if selection in sysstate:
                # print({'SysID': sysid, 'Sysname': sysname, 'sysModulation': sysmodulation})
                result.append(sysname)
                count = count + 1
            else:
                count = count + 1

    rrselectsystemDRPDWN = OptionMenu(rrimportFrame, rrimportselectsystemVar, *result)
    rrselectsystemDRPDWN.grid(column=1, row=0, columnspan=5, sticky='EW', pady=5, padx=5)
    rrimportselectsystemVar.set(result[0])


rrimportselectsystemVar = StringVar(rrimportFrame)
rrimportselectsystemVar.set('Select a System')  # default value

# rrstateentryTEXT = Label(rrimportFrame, text='State: ')
# rrstateentryTEXT.grid(column=1, row=0, pady=5, padx=5)

stateList = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

rrstateentryVar = StringVar(rrimportFrame)
rrstateentryVar.set('Select a State')

rrstateDRPDWN = OptionMenu(rrimportFrame, rrstateentryVar, *stateList, command=rrpopulateSystems)
rrstateDRPDWN.grid(column=0, row=0, pady=5, padx=5, sticky='W')

# rrselectsystemTEXT = Label(rrimportFrame, text='System: ')
# rrselectsystemTEXT.grid(column=1, row=1, pady=5, padx=5)

rrselectsystemDRPDWN = OptionMenu(rrimportFrame, rrimportselectsystemVar, [])
rrselectsystemDRPDWN.grid(column=1, row=0, columnspan=5, sticky='NSEW', pady=5, padx=5)

#rrSectionErrorTEXT = Label(rrimportFrame, text='Failed! Check Account')

def rrimportFUNC():
    selectedsystem = rrimportselectsystemVar.get()
    selectedstate = rrstateentryVar.get()
    import requests
    from bs4 import BeautifulSoup
    import re

    # rrSearch = 'https://www.radioreference.com/apps/db/?action=regexp&regexp=' + input('State: ')
    rrSearch = 'https://www.radioreference.com/apps/db/?action=regexp&regexp=' + selectedstate
    r = requests.get(rrSearch)

    soup = BeautifulSoup(r.text, features='lxml')
    table = soup.find('table', {"class": "rrtable"})

    items = re.findall("sid(.*)", str(table))

    # print(items)

    count = 0
    result = []

    for i in items:
        test = items[count].split('>')

        sysid = re.findall("\d{1,10}", str(test[0]))[0]
        sysname = test[1].replace('</a', '')
        sysmodulation = test[4].replace('</td', '')
        sysstate = test[10].replace("</td", "")

        if '25' not in sysmodulation:
            count = count + 1
        else:
            if selectedsystem in sysname:
                config.read('config.ini')
                rrUser = config.get('RadioReference', 'rruser')
                rrPass = config.get('RadioReference', 'rrpass')
                print({'SysID': sysid, 'Sysname': sysname, 'sysModulation': sysmodulation})
                #rrSectionErrorTEXT.configure(text='Allow Upto 60sec For Server to Import').grid(column=2, row=2, sticky='EW', pady=5, padx=5)

                sendCMD('radioreference', rrUser=rrUser, rrPass=rrPass, sysID=sysid,op25dir="/home/op25/op25/op25/gr-op25_repeater/apps/")

                #rrSectionErrorTEXT.grid_forget()
                count = count + 1
            else:
                count = count + 1




rrimportsystemBTN = Button(rrimportFrame, text='Import System', command=rrimportFUNC)
rrimportsystemBTN.grid(column=3, row=2, sticky='EW', pady=5, padx=5)

rrimportFrame.columnconfigure(0, weight=0)
rrimportFrame.columnconfigure(1, weight=0)
rrimportFrame.columnconfigure(2, weight=1)




def sdrFUNC(selection):
    config.set(sdrSection, 'sdr', selection)
    write_file()


def lnaFUNC(selection):
    config.set(sdrSection, 'lna', selection)
    write_file()


def samplerateFUNC(selection):
    config.set(sdrSection, 'samplerate', selection)
    write_file()


def restartop25FUNC():
    config.read('config.ini')
    sdr = config.get(sdrSection, 'sdr')
    lna = config.get(sdrSection, 'lna')
    samplerate = config.get(sdrSection, 'samplerate')
    sendCMD(function='stopop25')
    time.sleep(2)
    updateStatusText()
    sendCMD(function='startop25', sdr=sdr, lna=lna, samplerate=samplerate, trunkfile='trunk.tsv',
            op25dir='/home/op25/op25/op25/gr-op25_repeater/apps/')


sdrTEXT = Label(defaultSDRFrame, text='SDR: ')
sdrTEXT.grid(column=0, row=0, sticky='NEWS')

sdrVar = StringVar(defaultSDRFrame)
sdrVar.set("RTL")  # default value

sdrOptions = OptionMenu(defaultSDRFrame, sdrVar, "rtl", "rtl_tcp", "airspy", "hackrf", command=sdrFUNC)
sdrOptions.grid(column=1, row=0, sticky='NESW')

# defaultSDRFrame.columnconfigure(0, weight=1, uniform='sdrMenu')
defaultSDRFrame.columnconfigure(1, weight=1, uniform='sdrMenu')
# defaultSDRFrame.columnconfigure(2, weight=1, uniform='sdrMenu')
# defaultSDRFrame.columnconfigure(3, weight=1, uniform='sdrMenu')


lnaTEXT = Label(defaultSDRFrame, text='GAIN: ')
lnaTEXT.grid(column=0, row=1, sticky='NEWS')

lnaVar = StringVar(defaultSDRFrame)
lnaVar.set("35")  # default value

lnaOptions = OptionMenu(defaultSDRFrame, lnaVar, '0', '10', '15', '20', '25', '30', '35', '40', '45', '49',
                        command=lnaFUNC)
lnaOptions.grid(column=1, row=1, sticky='NESW')

samplerateTEXT = Label(defaultSDRFrame, text='SR:   ')
samplerateTEXT.grid(column=0, row=2, sticky='NEWS')

samplerateVar = StringVar(defaultSDRFrame)
samplerateVar.set("1.4e6")  # default value

samplerateOptions = OptionMenu(defaultSDRFrame, samplerateVar, '1.2e6', '1.4e6', '2.0e6', '2.8e6', '3.2e6',
                               command=samplerateFUNC)
samplerateOptions.grid(column=1, row=2, sticky='NESW')

restartop25BTN = Button(defaultSDRFrame, text='Restart OP25', command=restartop25FUNC)
restartop25BTN.grid(column=1, row=3, pady=5, padx=5, sticky='E')

config.read('config.ini')
sdrSection = 'SDR_Defaults'
if sdrSection not in config.sections():
    config.add_section(sdrSection)
    confwriter(sdrSection, 'sdr', sdrVar.get())
    confwriter(sdrSection, 'lna', lnaVar.get())
    confwriter(sdrSection, 'samplerate', samplerateVar.get())
config.read('config.ini')
sdrVar.set(config.get(sdrSection, 'sdr'))
lnaVar.set(config.get(sdrSection, 'lna'))
samplerateVar.set(config.get(sdrSection, 'samplerate'))

scanmodeTEXT = Label(menu_frame, text='Default Scanning Mode')
scanmodeTEXT.grid(column=0, row=4, padx=15, pady=0, sticky='NW')

scanmodeFrame = Frame(menu_frame, bd=3, relief=GROOVE)
scanmodeFrame.grid(column=0, row=5, padx=50, sticky='NESW')

menu_frame.columnconfigure(0, weight=0)

scanmodebtnTEXT = Label(scanmodeFrame, text='Select Your Scan Mode: ')
scanmodebtnTEXT.grid(column=0, row=0)

scanmodebtnFrame = Frame(scanmodeFrame)
scanmodebtnFrame.grid(column=1, row=0, sticky='NESW')

scanmodeFrame.columnconfigure(0, weight=1)
scanmodeFrame.columnconfigure(1, weight=1)

def scanmodeConf(mode):
    config.read('config.ini')
    if config.has_section('ScanMode'):
        confwriter('ScanMode', 'mode', mode)
    else:
        config.add_section('ScanMode')
        confwriter('ScanMode', 'mode', mode)



##You're adding logTAB.add(scanGridTAB4, text='ScanGrid', sticky='NESW') to the grid when scanlist mode is enabled.
scanmodeScanlistTEXT = Button(scanmodebtnFrame, text='List Scan',
                              command=lambda: [sysmsgUPDATE(text='Enabling List Scan Mode', bg='green'),
                                               sendCMD('enableblacklistrange'), restartop25FUNC(),
                                               logTAB.add(scanGridTAB4, text='ScanGrid', sticky='NESW'),
                                               scanmodeConf('list'),
                                               scanmodeButtonFUNC()])
scanmodeScanlistTEXT.grid(column=0, row=0, pady=3)

scanmodeSiteTEXT = Button(scanmodebtnFrame, text='Site Scan', command=lambda: [sendCMD('disableblacklistrange'),
                                                                               sysmsgUPDATE(
                                                                                   text='Enabling Site Scan Mode',
                                                                                   bg='green'), restartop25FUNC(),
                                                                               logTAB.hide(scanGridTAB4),scanmodeConf('site'),scanmodeButtonFUNC()])  # , logTAB.hide(scanGridTAB4)
scanmodeSiteTEXT.grid(column=1, row=0)

def scanmodeButtonFUNC():
    config.read('config.ini')
    if config.has_section('ScanMode'):
        currentmode = config.get('ScanMode', 'mode')
        modeTEXT.configure(text='Mode: ' + currentmode)
        if currentmode == 'site':
            scanmodeScanlistTEXT.configure(relief=RAISED)
            scanmodeSiteTEXT.configure(relief=SUNKEN)
        if currentmode == 'list':
            scanmodeScanlistTEXT.configure(relief=SUNKEN)
            scanmodeSiteTEXT.configure(relief=RAISED)
            logTAB.add(scanGridTAB4, text='ScanGrid', sticky='NESW')
        else:
            pass

scanmodeButtonFUNC()
##END MENU FRAME


##Color function to change display frame background and text color
def colorFUNC(color):
    if color == 'black':
        textcolor = 'darkgrey'
    else:
        textcolor = 'black'
    rootFrame.configure(background=color)
    topFrame.configure(background=color)
    activeFrame.configure(background=color)
    leftFrame.configure(background=color)
    rightFrame.configure(background=color)
    bottomFrame.configure(background=color)
    lefttalkgroupFrame.configure(background=color)
    leftalphaFrame.configure(background=color)
    rightalertFrame.configure(background=color)
    leftbuttonFrame.configure(background=color)
    leftsysFrame.configure(background=color)
    leftsiteFrame.configure(background=color)
    # leftcompassFrame.configure(background=color)
    rightdetailsFrame.configure(background=color)
    rightlogFrame.configure(background=color)
    righttxrxFrame.configure(background=color)
    leftstatusFrame.configure(background=color)
    # rightkeypadFrame.configure(background=color)
    # rightkeypadFrame.configure(background=color)
    # leftcompassFrame.configure(background=color)
    ##Text/Labels
    nacwacnTEXT.configure(fg=textcolor, bg=color)
    tagTEXT.configure(fg=textcolor, bg=color)
    bothrxtxTEXT.configure(fg=textcolor, bg=color)
    bothaddrTEXT.configure(fg=textcolor, bg=color)
    statusTEXT.configure(fg=textcolor, bg=color)
    encTEXT.configure(fg=textcolor, bg=color)
    # compassIMG.configure(fg=textcolor, bg=color)
    # compassRangeTEXT.configure(fg=textcolor, bg=color)
    systemTEXT.configure(fg=textcolor, bg=color)
    # call_logTEXT.configure(fg=textcolor, bg=color)
    row3alertTEXT.configure(fg=textcolor, bg=color)

    compassRangeTEXT.configure(bg=color, fg=textcolor)
    compassIMG.configure(bg=color)
    alertTEXT.configure(bg=color)

    modeTEXT.configure(bg=color, fg=textcolor)

    sysidTEXT.configure(fg=textcolor, bg=color)

    #secondaryTEXT.configure(fg=textcolor, bg=color)

    ##Buttons
    # holdBTN.configure(fg=textcolor, bg=color, activebackground=color)
    # skipBTN.configure(fg=textcolor, bg=color, activebackground=color)
    # gotoBTN.configure(fg=textcolor, bg=color, activebackground=color)

    # keypadEntry.configure(fg=textcolor, bg=color)
    # keypadentBTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad0BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad3BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad2BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad1BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad6BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad5BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad4BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad9BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad7BTN.configure(fg=textcolor, bg=color, activebackground=color)
    # keypad8BTN.configure(fg=textcolor, bg=color, activebackground=color)

    '''
    nacTEXT.configure(fg=textcolor, bg=color)
    wacnTEXT.configure(fg=textcolor, bg=color)


    tgidTEXT.configure(fg=textcolor, bg=color)
    systemTEXT.configure(fg=textcolor, bg=color)
    offsetTEXT.configure(fg=textcolor, bg=color)
    freqTEXT.configure(fg=textcolor, bg=color)
    srcaddrTEXT.configure(fg=textcolor, bg=color)
    grpaddrTEXT.configure(fg=textcolor, bg=color)

    rxchanTEXT.configure(fg=textcolor, bg=color)
    txchanTEXT.configure(fg=textcolor, bg=color)
    rfidTEXT.configure(fg=textcolor, bg=color)
    stidTEXT.configure(fg=textcolor, bg=color)
    secondaryTEXT.configure(fg=textcolor, bg=color)
    adjacent_dataTEXT.configure(fg=textcolor, bg=color)
    frequenciesTEXT.configure(fg=textcolor, bg=color)
    tsbksTEXT.configure(fg=textcolor, bg=color)
    errorTEXT.configure(fg=textcolor, bg=color)


    skipBTN.configure(fg=textcolor, bg=color, activebackground=color)
    menuBTN.configure(fg=textcolor, bg=color, activebackground=color)
    closemenuBTN.configure(fg=textcolor, bg=color, activebackground=color)

'''



colorFUNC(display_color)


if not os.path.exists('config.ini'):
    config['Pi25MCH'] = {'uri': ''}

    write_file()
else:
    # Read File
    config.read('config.ini')

    # Get the list of sections
    # print(config.sections())

    # Print value at test2
    print(config.get('Pi25MCH', 'uri'))



##Check if op25 url is specified
if config.get('Pi25MCH', 'uri') == '':
    ##open frame to configure Pi25MCH
    nouriPrompt.grid(row=1, column=0)
if config.get('Pi25MCH', 'uri') == 'http://ip_address_to_OP25:port':
    ##open frame to configure Pi25MCH
    nouriPrompt.grid(row=1, column=0)
else:
    time.sleep(1)
    t = threading.Thread(target=update)
    if not t.is_alive():
        t.start()


# t2 = threading.Thread(target=nightMode)
# t2.start()


def updateStatusText():
    statusTEXT.configure(text='SDR: ' + config.get(sdrSection, 'sdr') + "  LNA: " + config.get(sdrSection,
                                                                                               'lna') + "  SR: " + config.get(
        sdrSection, 'samplerate'))


print('MODULE LOADED: op25mch_client.py')
sysmsgUPDATE(text='MODULE LOADED: op25mch_client.py', bg='green')

if tagTEXT.cget('text') == "Connecting...":
    updateStatusText()

#####TRAILING SLASH IS VERY IMPORTANT

# sendCMD(function='radioreference', sysID='6643', rrUser='kr0siv', rrPass='', op25dir='/home/op25/op25/op25/gr-op25_repeater/apps/')
# sendCMD(function='stopop25')
'''
try:
    jsoncmd('skip', 0, 0)
except:
    print('Not Connecting to OP25, Attempting to Start with Remote Script')
    sendCMD(function='startop25', sdr='rtl', lna='49', samplerate='2000000', trunkfile='trunk.tsv', offset='0', op25dir='/home/op25/op25/op25/gr-op25_repeater/apps/')

'''

main_window.mainloop()

'''

##Json post functions


def holdFUNC():
    if holdBTN.cget('relief') == RAISED:
        holdBTN.configure(relief = SUNKEN, fg='red')
        requests.post(op25uri, json=[{"command": "hold", "arg1": 0, "arg2": 0}])
    else:
        if skipBTN.cget('bg') == 'black':##Check another button to see what the background color is
            holdBTN.configure(relief=RAISED, fg='white')##If blackbackground then white text
        holdBTN.configure(relief=RAISED, fg='black')##IF any other background then black text
        requests.post(op25uri, json=[{"command": "hold", "arg1": 0, "arg2": 0}])


def skipFUNC():
    requests.post(op25uri, json=[{"command": "skip", "arg1": 0, "arg2": 0}])


def gotoPostFUNC(talkgroup):
#    requests.post(op25uri, json=[{"command": "hold", "data": int(talkgroup)}])#2017 variant
    requests.post(op25uri, json=[{"command": "hold", "arg1": int(talkgroup), "arg2": 0}, {"command": "update", "arg1": 0, "arg2": 0}])
    holdTEXT.configure(text='HOLD')

##Rewrite this shit goto function
def gotoFUNC():
    # Toplevel object which will
    # be treated as a new window
    gotoWIN = Toplevel(main_window)

    # sets the title of the
    # Toplevel widget
    gotoWIN.title("GoTo")

    # sets the geometry of toplevel
    gotoWIN.geometry("200x50")

    # A Label widget to show in toplevel
    talkgroupENT = Entry(gotoWIN, text="")
    talkgroupENT.pack()
    goBTN = Button(gotoWIN, text='GO', command=lambda: [gotoPostFUNC(talkgroupENT.get()), gotoWIN.destroy()])
    goBTN.pack()

def openMENU():
    menuframe.grid(row=0, column=0, columnspan=5, rowspan=4, sticky='nsew')

def closeMENU():
    menuframe.grid_forget()


##Tuning Functions for The Key Frame

def tune100negFUNC():
    requests.post(op25uri, json=[{"command":"adj_tune","arg1":-100,"arg2":0}])


def tune100posFUNC():
    requests.post(op25uri, json=[{"command":"adj_tune","arg1":100,"arg2":0}])


def tune1200negFUNC():
    requests.post(op25uri, json=[{"command":"adj_tune","arg1":-1200,"arg2":0}])


def tune1200posFUNC():
    requests.post(op25uri, json=[{"command":"adj_tune","arg1":1200,"arg2":0}])

##FRAME COLOR OPTIONS
display_color = 'orange'
keyframe_color = 'lightgray'

##DISPLAY FRAME FOR PLOTTING OP25 DATA
displayframe = Frame(main_window)
displayframe.pack(side=TOP, pady=10, padx=10, ipady=0, expand=True, fill=BOTH)
displayframe.configure(background=display_color)


##Variables used but not referenced on grid
sysidTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
tgidTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
freqTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 30))
bothaddrTEXT = Label(displayframe, text="", bg=display_color, anchor='w', font=('Digital-7 Mono', 22))
rxchanTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 15))
txchanTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 15))
adjacent_dataTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
frequenciesTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 15))

#System Status Frame;Keeping everything looking nice
systemstatusframe = Frame(displayframe)
systemstatusframe.grid(row=0, column=0, sticky='new', columnspan=4)
systemstatusframe.configure(background=display_color)

systemstatusframe.columnconfigure(0, weight=1)


##MENU BUTTON;column4 while systemstatusframe of displayframe is a columnspan of 4 keeping it outside the primary frame
menuBTN = Button(displayframe, text=" ≡ ", bg=display_color, activebackground=display_color, font=('Digital-7 Mono', 12), command=openMENU)
menuBTN.grid(row=0, column=4, sticky='ne')
##MENU BUTTON

##Labels and positions for system status frame
nacTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
#nacTEXT.grid(row=0, column=0, sticky='nw')

wacnTEXT = Label(displayframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
#wacnTEXT.grid(row=0, column=0, sticky='nw')

nacwacnTEXT = Label(systemstatusframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
nacwacnTEXT.grid(row=0, column=0, sticky='nw')

rfidTEXT = Label(systemstatusframe, text="", bg=display_color, anchor='e', font=('Digital-7 Mono', 22))
rfidTEXT.grid(row=0, column=1, sticky='nw')

stidTEXT = Label(systemstatusframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
stidTEXT.grid(row=0, column=2, sticky='nw')

tsbksTEXT = Label(systemstatusframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
tsbksTEXT.grid(row=0, column=3, sticky='nw')


##Prime Display hold the TAG and System Data including the SystemFrame
primedisplayframe = Frame(displayframe)
primedisplayframe.grid(row=1, column=0, sticky='nsew', columnspan=5)
primedisplayframe.configure(background=display_color)

##Modify Prime Display Font Based on window width

##Modify Prime Display Font Based on window width

#Labels and positions for prime display
tagTEXT = Label(primedisplayframe, text="Scanning...", bg=display_color, font=('Digital-7 Mono', 40), anchor=SW, justify=LEFT)
#tagTEXT = Message(primedisplayframe, text="Scanning...", bg=display_color, font=('Digital-7 Mono', 40), width=1500)
tagTEXT.grid(row=0, column=0, columnspan=5, sticky='nw')


##SYSTEM FRAME FOR KEEPING SYSTEM DETAILS TOGETHER;exists within primedisplayframe
systemFRAME = Frame(primedisplayframe)
systemFRAME.configure(background=display_color)
systemFRAME.grid(row=1, column=0, sticky='nw')

#LABELS AND POSITIONS FOR SYSTEM FRAME
systemTEXT = Label(systemFRAME, text="", bg=display_color, font=('Digital-7 Mono', 40))
systemTEXT.grid(row=0, column=0, columnspan=1, sticky='nw')

bothrxtxTEXT = Label(systemFRAME, text="", bg=display_color, font=('Digital-7 Mono', 15))
bothrxtxTEXT.grid(row=0, column=1, rowspan=2, ipady=10, sticky='nw')

##Bottom frame for display
bottomframe = Frame(displayframe)
bottomframe.grid(column=0, row=3, sticky='nsew', columnspan=5)
bottomframe.configure(background=display_color)

bottomframe.columnconfigure(0, weight=1)

grpaddrTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
grpaddrTEXT.grid(row=3, column=0, rowspan=1, sticky='nw')

srcaddrTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
srcaddrTEXT.grid(row=4, column=0, rowspan=1, sticky='nw')

offsetTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
offsetTEXT.grid(row=3, column=5, sticky='ne')

errorTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 22))
errorTEXT.grid(row=4, column=5, sticky='ne')

holdTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 32))
#holdTEXT.grid(row=5, column=5, sticky='ne')


secondaryTEXT = Label(bottomframe, text="", bg=display_color, font=('Digital-7 Mono', 20))
secondaryTEXT.grid(row=5, column=0, sticky='nw')


##NON MENU BUTTONS FRAME
nonmenuframe = Frame(bottomframe)
nonmenuframe.grid(row=5, column=5, sticky='ne')

##NON MENU BUTTONS
skipBTN = Button(nonmenuframe, text="SKIP", bg=display_color, activebackground=display_color, fg='grey', font=('Digital-7 Mono', 22), command=skipFUNC)
skipBTN.grid(row=0, column=0, sticky='ne')

holdBTN = Button(nonmenuframe, text="HOLD", bg=display_color, activebackground=display_color, fg='grey', font=('Digital-7 Mono', 22), command=holdFUNC)
holdBTN.grid(row=0, column=1, sticky='ne')
##NON MENU BUTTONS


displayframe.columnconfigure(0, weight=0)
displayframe.columnconfigure(1, weight=0)
displayframe.columnconfigure(2, weight=1)
displayframe.columnconfigure(3, weight=0)

displayframe.rowconfigure(0, weight=1)
displayframe.rowconfigure(1, weight=0)
displayframe.rowconfigure(2, weight=1)

##MENU FRAME APPEARS OVER TOP OF ALL OTHER FRAMES
menuframe = Frame(displayframe)
menuframe.configure(background=display_color)
menuframe.columnconfigure(0, weight=1)
closemenuBTN = Button(menuframe, text=" ≡ ", bg=display_color, activebackground=display_color, font=('Digital-7 Mono', 12), command=closeMENU)
closemenuBTN.grid(row=0, column=4, sticky='ne')




'''
