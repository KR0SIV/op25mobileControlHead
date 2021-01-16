import requests
import json
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext as tks
import threading
import pyglet
from PIL import Image, ImageTk
import time
import io
import re
from datetime import datetime
import configparser, os

##config bug, until restart when you add your config details the log will double

config = configparser.ConfigParser()

# Just a small function to write the file
def write_file():
    config.write(open('config.ini', 'w'))

config.read('config.ini')

op25uri = config.get('Pi25MCH', 'uri')

def jsoncmd(command, arg1, arg2):
    config.read('config.ini')
    op25uri = config.get('Pi25MCH', 'uri')
    if op25uri == '':
        print('no uri found')
        #time.sleep(1)
        jsoncmd(command=command, arg1=arg1, arg2=arg2)
    if op25uri == 'http://ip_address_to_OP25:port':
        print('default uri found')
        #time.sleep(1)
        jsoncmd(command=command, arg1=arg1, arg2=arg2)
    else:
        try:
            #print('found uri')
            return requests.post(op25uri, json=[{"command":command,"arg1":int(arg1),"arg2":int(arg2)}])
        except:
            bottomStatusTEXT.configure(text='I\'m sorry, seems you\'re not running OP25 or the Remote Command Script. Fix that and Restart', bg='red')


def confwriter(argsection, argoption, argvalue):
    if argsection in config.sections():
        config.set(section=argsection, option=argoption, value=argvalue)
        write_file()
    else:
        config.add_section(argsection)
        config.set(section=argsection, option=argoption, value=argvalue)
        write_file()



#./rx.py --args 'rtl' -N 'LNA:49' -S 2000000 -f 855.8625e6 -o 25000 -T trunk.tsv -V -2 -q -1 -l http:0.0.0.0:8080
#pyglet.font.add_file('digital.ttf')

##Formats numbers with a decminal every 3 char
def formatchan(frequency):
    return '.'.join(frequency[i:i + 3] for i in range(0, len(frequency), 3))

##Update function, runs in a thread to keep checcking for new data from the OP25 web server.
def update():
    callLog = ""
    count = 1
    current = ""
    print('Running Update')
    while True:
        # time.sleep(0.5)
        try:
            #r = requests.post(op25uri, json=[{"command": "update", "data": 0}]) #OP25 2017 Request Format
            #r = requests.post(op25uri, json=[{"command":"update","arg1":0,"arg2":0}])  # OP25 2020 Request Format
            r = jsoncmd("update", 0, 0)
            data = json.loads(r.content)
            try:
                nac = str(hex(data[0]['nac']))
                #nacTEXT.configure(text='NAC: ' + nac)
                rawnac = str(data[0]['nac'])
                wacn = str(hex(data[0]['wacn']))
                #wacnTEXT.configure(text='WACN: ' + wacn)
                nacwacnTEXT.configure(text='NAC: ' + nac + ' / ' + 'WACN: ' + wacn)
                tgid = str(data[0]['tgid'])
                #tgidTEXT.configure(text=tgid)
                system = str(data[0]['system'])
                systemTEXT.configure(text=system)
                sysid = str('Sys ID: ' + hex(data[0]['sysid']))
                #sysidTEXT.configure(text=sysid)
                tag = str(data[0]['tag'])
                if re.search('[a-zA-Z]', tag):
                    tag = tag.lstrip()
                else:
                    tag = ('Talkgroup ID: ' + tgid + ' [' + str(hex(int(tgid))) + ']')
                tagTEXT.configure(text=tag)
                offset = str(data[0]['fine_tune'])
                #offsetTEXT.configure(text='FREQ OFFSET: ' + offset)
                freq = str(data[0]['freq'])
                #freqTEXT.configure(text='.'.join(freq[i:i + 3] for i in range(0, len(freq), 3)))
            except Exception as e:
                #print(e)
                pass
            try:
                enc = str(data[1]['encrypted'])
                if enc == str(0):
                    encTEXT.configure(fg='grey')
                else:
                    encTEXT.configure(fg='black')
                    if encTEXT.cget(bg='black'):
                        encTEXT.configure(fg='white')
                srcaddr = str(data[1]['srcaddr'])
                #srcaddrTEXT.configure(text='SRC: ' + srcaddr)
                grpaddr = str(data[1]['grpaddr'])
                if grpaddr == str(0):
                    tagTEXT.configure(text='Scanning...')
                if grpaddr != str(0):
                    if current != tag:
                        regexp = re.compile('[a-z]|[A-Z]')
                        if regexp.search(tag):
                            #callLog = callLog + tag + str('\t' + str(datetime.datetime.now()) + '\n')
                            call = str(count) + " " + tag + str('\t' + 'GRP: ' + str(grpaddr) + '\tSRC: ' + str(srcaddr) + '\t' + str(datetime.now().strftime('%I:%M:%S')))
                            #print(callLog)
                            #call_logTEXT.configure(text=callLog)
                            call_logTEXT.insert("1.0", call + '\n')
                            call_logTEXT.tag_add('highlightline', '1.0', '2.0')
                            call_logTEXT.tag_add('unhighlightline', '2.0', END)
                            call_logTEXT.tag_configure('highlightline', background='lightgreen')
                            call_logTEXT.tag_configure('unhighlightline', background='gray')
                            #call_logTEXT.yview_pickplace("end")
                            #call_logTEXT.see("end")
                            current = tag
                            count = count + 1
                            if count > 30:
                                call_logTEXT.delete("30.0", END)
                        else:
                            pass
                #grpaddrTEXT.configure(text='GRP: ' + grpaddr)
                grpTEXT.configure(text=grpaddr)
                bothaddrTEXT.configure(text='SRC: ' + srcaddr + '\r' + 'GRP: ' + grpaddr)
                rxchan = str(data[1][rawnac]['rxchan'])
                #rxchanTEXT.configure(text=rxchan)
                txchan = str(data[1][rawnac]['txchan'])
                #txchanTEXT.configure(text=txchan)
                bothrxtxTEXT.configure(text='RX: ' + formatchan(rxchan) + '\r' + 'TX: ' + formatchan(txchan))
                rfid = str(data[1][rawnac]['rfid'])
                #rfidTEXT.configure(text='RFSS ' + rfid)
                stid = str(data[1][rawnac]['stid'])
                #stidTEXT.configure(text='SITE ' + stid)
                secondary = str(data[1][rawnac]['secondary'])
                altcc = re.sub('\[|]', '', secondary).split(',')
                #secondaryTEXT.configure(
                #    text='ALT CTL: ' + formatchan(altcc[0]) + ', ' + formatchan(altcc[1].replace(' ', '')) + ', ' + formatchan(altcc[2].replace(' ', '')))
                adjacent_data = str(data[1][rawnac]['adjacent_data'])
                #adjacent_dataTEXT.configure(text=adjacent_data)
                # print(adjacent_data)
                frequencies = str(data[1][rawnac]['frequencies'])
                #frequenciesTEXT.configure(text=frequencies)
                tsbks = str(data[1][rawnac]['tsbks'])
                #tsbksTEXT.configure(text='tsbks:' + tsbks)
            except Exception as e:
               #print(e)
                pass
            try:
                error = str(data[2]['error'])
                #errorTEXT.configure(text='ERR: ' + error + 'Hz')
            except:
                pass

        except:
                tagTEXT.configure(text='Connecting...')
                bottomStatusTEXT.configure(text='Failed to Connect to OP25 Instance, trying again in 10 Seconds..', bg='red')
                count = 0
                call_logTEXT.insert("1.0", 'Reconnecting to OP25 Instance' + '\t' + str(datetime.now().strftime('%I:%M:%S')) + '\n')
                call_logTEXT.tag_add('highlightline', '1.0', '2.0')
                call_logTEXT.tag_add('unhighlightline', '2.0', END)
                call_logTEXT.tag_configure('highlightline', background='lightgreen')
                call_logTEXT.tag_configure('unhighlightline', background='gray')
                bottomStatusTEXT.configure(text='Sending Remote Command to Start OP25 With Your Selected Defaults')
                sendCMD(function='startop25', sdr='rtl', lna='49', samplerate='2000000', trunkfile='trunk.tsv',
                        offset='0', op25dir='/home/op25/op25/op25/gr-op25_repeater/apps/')
                time.sleep(10)
                bottomStatusTEXT.configure(text='Attempting to reconnect', bg='red')
                if jsoncmd('update', 0, 0) == None:
                    pass
                else:
                    bottomStatusTEXT.configure(text='Connected!', bg='green')
                    bottomStatusTEXT.configure(text='OP25 Instance Connected!', bg='green')
                    call_logTEXT.insert("1.0", 'OP25 Instance Connected' + '\t' + str(
                        datetime.now().strftime('%I:%M:%S')) + '\n')
                    call_logTEXT.tag_add('highlightline', '1.0', '2.0')
                    call_logTEXT.tag_add('unhighlightline', '2.0', END)
                    call_logTEXT.tag_configure('highlightline', background='lightgreen')
                    call_logTEXT.tag_configure('unhighlightline', background='gray')
                update()



######################START CLIENT FOR REMOTE COMMAND FUNCTIONS################################

import socket
import sys



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
    #call_logTEXT.tag_configure('unhighlightline', background='gray')
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
        #requests.post(op25uri, json=[{"command": "hold", "arg1": 0, "arg2": 0}])
        jsoncmd("hold", 0, 0)
    else:
        if int(input) != 0:

            holdBTN.configure(relief=SUNKEN, fg='red', text='HOLD\n'+input)
            #requests.post(op25uri, json=[{"command": "hold", "arg1": int(input), "arg2": 0}])
            jsoncmd("hold", int(input), 0)


def skipFUNC():
    #requests.post(op25uri, json=[{"command": "skip", "arg1": 0, "arg2": 0}])
    jsoncmd('skip', 0, 0)

def gotoFUNC():
    if gotoBTN.cget('relief') == SUNKEN:
        rightkeypadFrame.grid_remove()
        gotoBTN.configure(relief=RAISED)
    else:
        gotoBTN.configure(relief=SUNKEN)
        rightkeypadFrame.grid(column=1, row=0, columns=1, sticky='NESW')
        #rightkeypadFrame.grid_remove()

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
display_color = 'tan'




rootFrame = Frame(main_window)
rootFrame.grid(column=0, row=0, rows=3, columns=2, sticky='NESW')
main_window.columnconfigure(0, weight=1) #rootFrame spans to main_window width
main_window.rowconfigure(0, weight=1) #rootFrame spans to main_window height


##MENU Frame;Opens Overtop The other Frames
menu_frame = Frame(main_window)


##END MENU Frame

##Top Frame;A button bar;menu bar;status text;something
topFrame = Frame(rootFrame)
#topFrame.grid(column=0, row=0, columnspan=2, sticky='NEW')
#Label(topFrame, text='Status or Menu Bar Row').grid()
rootFrame.columnconfigure(0, weight=1) #topFrame spans to main_window width
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
#rightkeypadFrame.grid(column=1, row=0, columns=1, sticky='NESW')
#rightkeypadFrame.grid_remove()

activeFrame.columnconfigure(0, weight=1, uniform='LeftRightFrameGrouping')
activeFrame.columnconfigure(1, weight=1, uniform='LeftRightFrameGrouping')
activeFrame.rowconfigure(0, weight=1)
##END Primary Frame

##Bottom Frame;A Button bar...
bottomFrame = Frame(rootFrame, bd=1, relief=SOLID)
bottomFrame.grid(column=0, row=4, columns=10, sticky='SEW')

bottomStatusTEXT = Label(bottomFrame, text='Loading Status Updates....', bg=display_color, anchor='w')
bottomStatusTEXT.grid(sticky='NSEW')

bottomFrame.columnconfigure(0, weight=1)

##END Bottom FRame


##Left Primary Column Sub-Frames

##Row 0;Talkgroup and Alpha Tag Frame
lefttalkgroupFrame = Frame(leftFrame, bd=1, relief=SOLID)
lefttalkgroupFrame.grid(column=0, row=0, sticky='NESW')
#Label(lefttalkgroupFrame, text='Talkgroup Frame').grid()
leftFrame.columnconfigure(0, weight=1)

leftalphaFrame = Frame(lefttalkgroupFrame, bd=1, relief=SOLID)
leftalphaFrame.grid(column=0, row=0, rows=5, sticky='NESW')
#Label(leftalphaFrame, text='Alpha Tag Frame').grid()
lefttalkgroupFrame.columnconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(4, weight=1, uniform='addrs')
lefttalkgroupFrame.rowconfigure(5, weight=1, uniform='addrs')

leftstatusFrame = Frame(leftalphaFrame)
leftstatusFrame.grid(column=0, row=0, columns=10, sticky='NEW')
leftalphaFrame.columnconfigure(0, weight=1)


leftbuttonFrame = Frame(lefttalkgroupFrame, bd=1, relief=SOLID)
leftbuttonFrame.grid(column=1, row=0, rows=3, sticky='NESW')
#Label(leftbuttonFrame, text='left Status Frame').grid()
lefttalkgroupFrame.columnconfigure(0, weight=1)
lefttalkgroupFrame.rowconfigure(0, weight=1)
##END Row0;Talkgroup and Alpha Tag Frame

##Row1;Alert Frame;CAll Alerts;Notifications
rightalertFrame = Frame(rightFrame, bd=1, relief=SOLID)
rightalertFrame.grid(column=0, row=0, sticky='NESW')
#Label(rightalertFrame, text='Alert Frame').grid()
leftFrame.columnconfigure(0, weight=1)
##END Row1;Alert Frame

#Row2;System Detail Frame
leftsysFrame = Frame(leftFrame, bd=1, relief=SOLID)
leftsysFrame.grid(column=0, row=2, sticky='NESW')
Label(leftsysFrame, text='System Detail Frame').grid()
leftFrame.columnconfigure(0, weight=1)

leftFrame.rowconfigure(0, weight=1, uniform='LeftFrameRowGrouping')
leftFrame.rowconfigure(1, weight=1, uniform='LeftFrameRowGrouping')
leftFrame.rowconfigure(2, weight=1, uniform='LeftFrameRowGrouping')
#END Row2;System Detail Frame

##END Left Primary Column Sub-Frames

##Right Primary Column Sub-Frames
leftsiteFrame = Frame(leftFrame, bd=1, relief=SOLID)
leftsiteFrame.grid(column=0, row=1, sticky='NESW')
#Label(leftsiteFrame, text='Right Site Frame').grid()
rightFrame.columnconfigure(0, weight=1)

rightdetailsFrame = Frame(leftsiteFrame, bd=1, relief=SOLID)
rightdetailsFrame.grid(column=0, row=0, rows=3, sticky='NESW')
#Label(rightdetailsFrame, text='Right Site Details Frame').grid()

righttxrxFrame = Frame(rightdetailsFrame)
righttxrxFrame.grid(column=0, row=2, sticky='EW')

leftcompassFrame = Frame(leftsiteFrame, bd=1, relief=SOLID)
leftcompassFrame.grid(column=1, row=0, sticky='NESW')
#Label(leftcompassFrame, text='Right Site Compass Frame').grid()


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
#nightmodePrompt.grid(row=1, column=0)


nightModeTEXT = Label(nightmodePrompt, text='', bg='black', fg='white', justify=LEFT, font=("Courier", 25), bd=5, relief=RAISED)
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
#nouriPrompt.grid(row=1, column=0)


nouriTEXT = Label(nouriPrompt, text='No OP25 URI Configured!', fg='red', justify=LEFT, font=("Courier", 25), bd=2, relief=RAISED)
nouriTEXT.grid(column=0, row=0)

nouriENT = Entry(nouriPrompt)
nouriENT.insert(0, 'http://ip_address_to_OP25:port')
nouriENT.grid(column=0, row=1, sticky='WE')

nouriBTN = Button(nouriPrompt, text='SAVE', command=nouriFUNC)
nouriBTN.grid(column=0, row=2)


##Tabbed Window Start

#style = ttk.Style()

#noteStyle = ttk.Style()

#noteStyle.theme_use('default')
#noteStyle.configure("TNotebook", background=display_color, borderwidth=0)
#noteStyle.configure("TNotebook.Tab", borderwidth=0, padding=25, width=10000)
#noteStyle.map("TNotebook", background=[("selected", display_color)])


style = ttk.Style()
style.theme_create('Cloud', settings={
    ".": {
        "configure": {
            "background": '#aeb0ce', # All colors except for active tab-button
            "font": 'red'
        }
    },
    "TNotebook": {
        "configure": {
            "background": 'lightgray', # color behind the notebook
            "tabmargins": [5, 5, 0, 0], # [left margin, upper margin, right margin, margin beetwen tab and frames]
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "background": 'lightgray', # Color of non selected tab-button
            "padding": [20, 20], # [space beetwen text and horizontal tab-button border, space between text and vertical tab_button border]
            "font":"white",
            "width":1000,
            "borderwidth":2
        },
        "map": {
            "background": [("selected", 'grey')], # Color of active tab
            "expand": [("selected", [1, 1, 1, 0])] # [expanse of text]
        }
    }
})

style.theme_create('Nightmode', settings={
    ".": {
        "configure": {
            "background": '#aeb0ce', # All colors except for active tab-button
            "font": 'red'
        }
    },
    "TNotebook": {
        "configure": {
            "background": 'black', # color behind the notebook
            "tabmargins": [5, 5, 0, 0], # [left margin, upper margin, right margin, margin beetwen tab and frames]
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "background": 'lightgray', # Color of non selected tab-button
            "padding": [20, 20], # [space beetwen text and horizontal tab-button border, space between text and vertical tab_button border]
            "font":"white",
            "width":1000,
            "borderwidth":2
        },
        "map": {
            "background": [("selected", 'grey')], # Color of active tab
            "expand": [("selected", [1, 1, 1, 0])] # [expanse of text]
        }
    }
})



style.theme_use('Cloud')


logTAB = ttk.Notebook(rightlogFrame)
rightlogFrame.columnconfigure(0, weight=1)
rightlogFrame.rowconfigure(0, weight=1)


#Tab1
callTAB1 = Frame(logTAB, bg='lightgray')
logTAB.add(callTAB1, text='Call Log', sticky='NESW')

#Tab2
syslogTAB2 = Frame(logTAB, bg='lightgray')
logTAB.add(syslogTAB2, text='System Log', sticky='NESW')

#Tab3
themegTAB3 = Frame(logTAB, bg='lightgray')
logTAB.add(themegTAB3, text='Theme', sticky='NESW')

logTAB.grid(column=0, row=0, sticky='NESW')

logTAB.columnconfigure(0, weight=1)
logTAB.rowconfigure(0, weight=1)

##Tabbed Frames END


rightFrame.rowconfigure(0, weight=1, uniform='RightFrameRowGrouping')
rightFrame.rowconfigure(1, weight=2, uniform='RightFrameRowGrouping')
##END Right Primary Column Sub-Frames

##StatusFrame Labels and Positions

##END StatusFrame Labels and Positions

##AlphaTag Frame Labels and Positions
statusTEXT = Label(leftstatusFrame, text="System Placeholder", bg=display_color, font=('Digital-7 Mono', 10))
statusTEXT.grid(column=0, row=0, sticky='W')

encTEXT = Label(leftstatusFrame, text="Ø", bg=display_color, fg='grey', font=('Digital-7 Mono', 10))
encTEXT.grid(column=5, row=0, sticky='E')

tagTEXT = Label(leftalphaFrame, text="Connecting...", bg=display_color, font=('Digital-7 Mono', 32), anchor=SW, justify=LEFT)
tagTEXT.grid(column=0, row=1, sticky='NW')

bothaddrTEXT = Label(leftalphaFrame, bg=display_color, font=('Digital-7 Mono', 15), anchor=SW, justify=LEFT)
bothaddrTEXT.grid(column=0, row=2, rowspan=2, sticky='NW')

##END AlphaTag Frame Labels and Positions

##Left Status Frame labels and Positions
grpTEXT = Label(rightdetailsFrame, text="")#give holdbutn my text
holdBTN = Button(leftbuttonFrame, text="HOLD", bg='lightgray', font=('Digital-7 Mono', 22), command=lambda: holdFUNC(grpTEXT.cget('text')))###CONTAINS PLACEHOLDER TEXT
holdBTN.grid(column=0, row=0, sticky='nesw')

gotoBTN = Button(leftbuttonFrame, text="GOTO", bg='lightgray', font=('Digital-7 Mono', 22), relief=RAISED, command=gotoFUNC)###CONTAINS PLACEHOLDER TEXT
gotoBTN.grid(column=0, row=1, sticky='nesw')


skipBTN = Button(leftbuttonFrame, text="SKIP", bg='lightgray', font=('Digital-7 Mono', 22), command=skipFUNC)###CONTAINS PLACEHOLDER TEXT
skipBTN.grid(column=0, row=2, sticky='nesw')

leftbuttonFrame.rowconfigure(0, weight=1)
leftbuttonFrame.rowconfigure(1, weight=1)
leftbuttonFrame.rowconfigure(2, weight=1)
##END Left Status Frame Labels and Positions

def d(event):
    framewidth = int(event.width / 20)
    holdBTN.configure(width=framewidth)
    gotoBTN.configure(width=framewidth)
    skipBTN.configure(width=framewidth)

leftcompassFrame.bind( "<Configure>", d )



##Right Keypad Frame
def keypadFUNC(int):
    keypadEntry.insert(20, str(int))

def keypadentFUNC(input):
    rightkeypadFrame.grid_remove()
    value = keypadEntry.get()
    keypadEntry.delete(0, 'end')
    #requests.post(op25uri, json=[{"command": "hold", "arg1": int(value), "arg2": 0}, {"command": "update", "arg1": 0, "arg2": 0}])
    jsoncmd('hold', int(value), 0)
    jsoncmd('update', 0, 0)
    holdBTN.configure(fg='red', relief=SUNKEN, text='HOLD\n'+input)
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

nacwacnTEXT = Label(rightdetailsFrame, text="", bg=display_color, font=('Digital-7 Mono', 20))
nacwacnTEXT.grid(column=0, row=0)

#Label(rightdetailsFrame, text='Placeholder line 2', font=('Digital-7 Mono', 15), bg=display_color).grid(row=1, column=0, sticky='W')

systemTEXT = Label(righttxrxFrame, text="", bg=display_color, font=('Digital-7 Mono', 32), anchor=SW, justify=LEFT)###CONTAINS PLACEHOLDER TEXT
systemTEXT.grid(column=0, row=0, sticky='Se')

bothrxtxTEXT = Label(righttxrxFrame, text="", bg=display_color, font=('Digital-7 Mono', 12))
bothrxtxTEXT.grid(column=2, row=0, rowspan=2, ipady=10, sticky='EW')



rightdetailsFrame.rowconfigure(0, weight=1)
rightdetailsFrame.rowconfigure(1, weight=1)
rightdetailsFrame.rowconfigure(2, weight=1)

leftsiteFrame.columnconfigure(3, weight=1)



##END Right site details frame

#Label(rightalertFrame, text='Placeholder').grid(row=0, column=0, columnspan=4, sticky='NSEW')

def openmenuFUNC():
    menu_frame.grid(column=0, row=0, rowspan=2, sticky='NESW')

def closemenuFUNC():
    menu_frame.grid_remove()

##MENU BUTTON;column4 while systemstatusframe of displayframe is a columnspan of 4 keeping it outside the primary frame
menuBTN = Button(rightalertFrame, text=" ≡ ", bg=display_color, activebackground=display_color, font=('Digital-7 Mono', 12), command=openmenuFUNC)
menuBTN.grid(row=0, column=5, sticky='E')
##MENU BUTTON

rightalertFrame.columnconfigure(0, weight=1)



#Label(leftcompassFrame, text='placeholder').grid(row=0, column=0, sticky='nsew')




compassRangeTEXT = Label(leftcompassFrame, text='15 Miles', bg=display_color)
compassRangeTEXT.grid(row=0, column=1, sticky='NESW')

##Right Site Compass Frame
img = Image.open('static/images/compass.png')#.rotate(compassRotate(bearing))

tkimage = ImageTk.PhotoImage(img)
compassIMG = Label(leftcompassFrame, image=tkimage, bg=display_color)
compassIMG.grid(row=1, column=1, sticky='NESW')



leftcompassFrame.rowconfigure(0, weight=1)
leftcompassFrame.rowconfigure(1, weight=1)
leftcompassFrame.columnconfigure(0, weight=1)
leftcompassFrame.columnconfigure(1, weight=1)



tuneBTN = Button(leftcompassFrame, text='TUNE', width=10, bg='lightgray')
#tuneBTN.grid(column=0, row=0, sticky='NESW')


##END Right Site Compass Frame

#Tab Name Labels
#tab1Label = Label(callTAB1, text="This is Tab 1", bg=display_color)
call_logTEXT = Text(callTAB1, bg='gray', relief=SOLID)
call_logTEXT.grid(column=0, row=0, padx=2, pady=2, sticky='NESW')

callTAB1.rowconfigure(0, weight=1)
callTAB1.columnconfigure(0, weight=1)


syslogsyslogTAB2Label = Label(syslogTAB2, text="This is Tab 2", bg='lightgray')

syslogsyslogTAB2Label.grid(column=1, row=0, padx=10, pady=10, sticky='NESW')


##Tab3 Color Picker
tanBTN = Button(themegTAB3, text='TAN', bg='tan', command=lambda: colorFUNC('tan'))
tanBTN.grid(column=0, row=0, sticky='NESW')

blackBTN = Button(themegTAB3, text='BLK', bg='black', fg='white', command=lambda: colorFUNC('black'))
blackBTN.grid(column=1, row=0, sticky='NESW')

greenBTN = Button(themegTAB3, text='GRN', bg='green', command=lambda: colorFUNC('green'))
greenBTN.grid(column=2, row=0, sticky='NESW')

orangeBTN = Button(themegTAB3, text='ORG', bg='orange', command=lambda: colorFUNC('orange'))
orangeBTN.grid(column=0, row=1, sticky='NESW')

yellowBTN = Button(themegTAB3, text='YEL', bg='yellow', command=lambda: colorFUNC('yellow'))
yellowBTN.grid(column=1, row=1, sticky='NESW')

pinkBTN = Button(themegTAB3, text='PNK', bg='pink', command=lambda: colorFUNC('pink'))
pinkBTN.grid(column=2, row=1, sticky='NESW')

themegTAB3.rowconfigure(0, weight=1)
themegTAB3.rowconfigure(1, weight=1)

themegTAB3.columnconfigure(0, weight=1)
themegTAB3.columnconfigure(1, weight=1)
themegTAB3.columnconfigure(2, weight=1)
##END Tab 3


##MENU FRAME
closemenuBTN = Button(menu_frame, text=" ≡ ", bg=display_color, activebackground=display_color, font=('Digital-7 Mono', 12), command=closemenuFUNC)
closemenuBTN.grid(row=0, column=5, sticky='E')
menu_frame.columnconfigure(0, weight=1)

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
    if rr_ischecked.get() == str(0):
        print('start rr command i guess')
        pass
    else:
        confwriter('RadioReference', 'rruser', usernameENT.get())
        confwriter('RadioReference', 'rrpass', passwordENT.get())


rr_ischecked = StringVar()
rememberCHK = Checkbutton(rrloginFrame, text='Remember Me?', variable=rr_ischecked)
rememberCHK.grid(column=3, row=3)
rememberCHK.deselect()
rrloginFrame.rowconfigure(4, weight=1)

def clearrrFUNC():
    usernameENT.delete(0, END)
    passwordENT.delete(0, END)


clearrrBTN = Button(rrloginFrame, text='Clear', command=clearrrFUNC)
clearrrBTN.grid(column=4, row=3)


enterrrBTN = Button(rrloginFrame, text='Enter', command=submitrr)
enterrrBTN.grid(column=5, row=3, pady=5, padx=5)



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
    #leftcompassFrame.configure(background=color)
    rightdetailsFrame.configure(background=color)
    rightlogFrame.configure(background=color)
    righttxrxFrame.configure(background=color)
    leftstatusFrame.configure(background=color)
    #rightkeypadFrame.configure(background=color)
    #rightkeypadFrame.configure(background=color)
    #leftcompassFrame.configure(background=color)
    ##Text/Labels
    nacwacnTEXT.configure(fg=textcolor, bg=color)
    tagTEXT.configure(fg=textcolor, bg=color)
    bothrxtxTEXT.configure(fg=textcolor, bg=color)
    bothaddrTEXT.configure(fg=textcolor, bg=color)
    statusTEXT.configure(fg=textcolor, bg=color)
    encTEXT.configure(fg=textcolor, bg=color)
    #compassIMG.configure(fg=textcolor, bg=color)
    #compassRangeTEXT.configure(fg=textcolor, bg=color)
    systemTEXT.configure(fg=textcolor, bg=color)
    #call_logTEXT.configure(fg=textcolor, bg=color)

    ##Buttons
    #holdBTN.configure(fg=textcolor, bg=color, activebackground=color)
    #skipBTN.configure(fg=textcolor, bg=color, activebackground=color)
    #gotoBTN.configure(fg=textcolor, bg=color, activebackground=color)

    #keypadEntry.configure(fg=textcolor, bg=color)
    #keypadentBTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad0BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad3BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad2BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad1BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad6BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad5BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad4BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad9BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad7BTN.configure(fg=textcolor, bg=color, activebackground=color)
    #keypad8BTN.configure(fg=textcolor, bg=color, activebackground=color)

    '''
    nacTEXT.configure(fg=textcolor, bg=color)
    wacnTEXT.configure(fg=textcolor, bg=color)
    
    sysidTEXT.configure(fg=textcolor, bg=color)
    
    secondaryTEXT.configure(fg=textcolor, bg=color)
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
    #print(config.sections())

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
    #t2.start()



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
                bottomStatusTEXT.configure(text='ACK: ' + str(data.decode('utf-8')), bg='green')
            else:
                sock.sendall(bytemsg)
                bottomStatusTEXT.configure(text='Failed to send command, trying again', bg='red')
    except Exception as e:
        #print(e)
        print('Server not started: is your remote script runnning?')
        bottomStatusTEXT.configure(text='ERROR: Couldn\'t Contact OP25 Instance', bg='red')

    finally:
        print('closing socket')
        sock.close()


print('MODULE LOADED: op25mch_client.py')
bottomStatusTEXT.configure(text='MODULE LOADED: op25mch_client.py', bg='green')


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
