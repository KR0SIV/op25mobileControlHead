import requests
import json
from tkinter import *
import threading
import pyglet
from PIL import Image, ImageTk
import time
import io

op25uri = 'http://192.168.122.25:8080'
#./rx.py --args 'rtl' -N 'LNA:49' -S 2000000 -f 855.8625e6 -o 25000 -T trunk.tsv -V -2 -q -1 -l http:0.0.0.0:8080
#pyglet.font.add_file('digital.ttf')

##Formats numbers with a decminal every 3 char
def formatchan(frequency):
    return '.'.join(frequency[i:i + 3] for i in range(0, len(frequency), 3))

##Update function, runs in a thread to keep checcking for new data from the OP25 web server.
def update():
    while True:
        # time.sleep(0.5)
        try:
            #r = requests.post(op25uri, json=[{"command": "update", "data": 0}]) #OP25 2017 Request Format
            r = requests.post(op25uri, json=[{"command":"update","arg1":0,"arg2":0}])  # OP25 2020 Request Format
            data = json.loads(r.content)
            try:
                nac = str(hex(data[0]['nac']))
                nacTEXT.configure(text='NAC: ' + nac)
                rawnac = str(data[0]['nac'])
                wacn = str(hex(data[0]['wacn']))
                wacnTEXT.configure(text='WACN: ' + wacn)
                nacwacnTEXT.configure(text='NAC: ' + nac + ' / ' + 'WACN: ' + wacn)
                tgid = str(data[0]['tgid'])
                tgidTEXT.configure(text=tgid)
                system = str(data[0]['system'])
                systemTEXT.configure(text=system)
                sysid = str('Sys ID: ' + hex(data[0]['sysid']))
                sysidTEXT.configure(text=sysid)
                tag = str(data[0]['tag'])
                if tgid is None:
                    if tag != " ":
                        tag = tag
                if tgid != None:
                    tag = ('Talkgroup ID: ' + tgid + ' [' + str(hex(int(tgid))) + ']')
                tagTEXT.configure(text=tag)
                offset = str(data[0]['fine_tune'])
                offsetTEXT.configure(text='FREQ OFFSET: ' + offset)
                freq = str(data[0]['freq'])
                freqTEXT.configure(text='.'.join(freq[i:i + 3] for i in range(0, len(freq), 3)))
            except Exception as e:
                #print(e)
                pass
            try:
                srcaddr = str(data[1]['srcaddr'])
                srcaddrTEXT.configure(text='SRC: ' + srcaddr)
                grpaddr = str(data[1]['grpaddr'])
                if grpaddr == str(0):
                    tagTEXT.configure(text='Scanning...')
                grpaddrTEXT.configure(text='GRP: ' + grpaddr)
                bothaddrTEXT.configure(text='SRC: ' + srcaddr + '\r' + 'GRP: ' + grpaddr)
                rxchan = str(data[1][rawnac]['rxchan'])
                rxchanTEXT.configure(text=rxchan)
                txchan = str(data[1][rawnac]['txchan'])
                txchanTEXT.configure(text=txchan)
                bothrxtxTEXT.configure(text='RX: ' + formatchan(rxchan) + '\r' + 'TX: ' + formatchan(txchan))
                rfid = str(data[1][rawnac]['rfid'])
                rfidTEXT.configure(text='RFSS ' + rfid)
                stid = str(data[1][rawnac]['stid'])
                stidTEXT.configure(text='SITE ' + stid)
                secondary = str(data[1][rawnac]['secondary'])
                altcc = re.sub('\[|]', '', secondary).split(',')
                secondaryTEXT.configure(
                    text='ALT CTL: ' + formatchan(altcc[0]) + ', ' + formatchan(altcc[1].replace(' ', '')) + ', ' + formatchan(altcc[2].replace(' ', '')))
                adjacent_data = str(data[1][rawnac]['adjacent_data'])
                adjacent_dataTEXT.configure(text=adjacent_data)
                # print(adjacent_data)
                frequencies = str(data[1][rawnac]['frequencies'])
                frequenciesTEXT.configure(text=frequencies)
                tsbks = str(data[1][rawnac]['tsbks'])
                tsbksTEXT.configure(text='tsbks:' + tsbks)
            except:
                pass
            try:
                error = str(data[2]['error'])
                errorTEXT.configure(text='ERR: ' + error + 'Hz')
            except:
                pass

        except:
            print('failed')

##Main TKInter Config/Setup
screen_width = 2280 // 2
screen_height = 1080 // 2
screen_geometry = '{}x{}'.format(screen_width, screen_height)

main_window = Tk()
#main_window.call('tk', 'scaling', 2.8) #Android phone scale
main_window.call('tk', 'scaling', 2.0) #Windows 10 scale
main_window.title('OP25 Control Head')
# main_window.resizable(0, 0)
main_window.geometry(screen_geometry)



##Color function to change display frame background and text color
def colorFUNC(color):
    if color == 'black':
        textcolor = 'white'
    else:
        textcolor = 'black'
    displayframe.configure(background=color)
    nonmenuframe.configure(background=color)
    primedisplayframe.configure(background=color)
    bottomframe.configure(background=color)
    menuframe.configure(background=color)
    systemstatusframe.configure(background=color)
    systemFRAME.configure(background=color)
    nacTEXT.configure(fg=textcolor, bg=color)
    wacnTEXT.configure(fg=textcolor, bg=color)
    nacwacnTEXT.configure(fg=textcolor, bg=color)
    sysidTEXT.configure(fg=textcolor, bg=color)
    tagTEXT.configure(fg=textcolor, bg=color)
    secondaryTEXT.configure(fg=textcolor, bg=color)
    tgidTEXT.configure(fg=textcolor, bg=color)
    systemTEXT.configure(fg=textcolor, bg=color)
    offsetTEXT.configure(fg=textcolor, bg=color)
    freqTEXT.configure(fg=textcolor, bg=color)
    srcaddrTEXT.configure(fg=textcolor, bg=color)
    grpaddrTEXT.configure(fg=textcolor, bg=color)
    bothaddrTEXT.configure(fg=textcolor, bg=color)
    rxchanTEXT.configure(fg=textcolor, bg=color)
    txchanTEXT.configure(fg=textcolor, bg=color)
    rfidTEXT.configure(fg=textcolor, bg=color)
    stidTEXT.configure(fg=textcolor, bg=color)
    secondaryTEXT.configure(fg=textcolor, bg=color)
    adjacent_dataTEXT.configure(fg=textcolor, bg=color)
    frequenciesTEXT.configure(fg=textcolor, bg=color)
    tsbksTEXT.configure(fg=textcolor, bg=color)
    errorTEXT.configure(fg=textcolor, bg=color)
    holdTEXT.configure(fg=textcolor, bg=color)
    bothrxtxTEXT.configure(fg=textcolor, bg=color)
    skipBTN.configure(fg=textcolor, bg=color, activebackground=color)
    menuBTN.configure(fg=textcolor, bg=color, activebackground=color)
    closemenuBTN.configure(fg=textcolor, bg=color, activebackground=color)
    holdBTN.configure(fg=textcolor, bg=color, activebackground=color)

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
def d(event):
    varifont = int(int(event.width) / 28)
    tagTEXT.configure(font=('Digital-7 Mono', varifont))
    systemTEXT.configure(font=('Digital-7 Mono', varifont))

primedisplayframe.bind( "<Configure>", d )
##Modify Prime Display Font Based on window width

#Labels and positions for prime display
tagTEXT = Label(primedisplayframe, text="Scanning...", bg=display_color, font=('Digital-7 Mono', 40))
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

colorFUNC('black')

t = threading.Thread(target=update)
t.start()
main_window.mainloop()
