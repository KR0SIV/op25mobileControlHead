import socket
import sys
import os
import ast

op25OutputPath = os.getcwd() + '/'

####################START Radio Reference Import####################
import csv
from zeep import Client
import re
import sys
import os
import requests
import re
from bs4 import BeautifulSoup

def generateTSV(rrUser, rrPass, rrsysid, op25dir):
    # rrSystemId = int(input("What system ID would you like to download?"))
    rrSystemId = int(rrsysid)

    # parameters
    #op25OutputPath = os.getcwd() + "//"
    # op25OutputPath = '/home/pi/Downloads/op25/op25/gr-op25_repeater/apps/'
    #op25OutputPath = op25dir


    # radio reference authentication
    client = Client('http://api.radioreference.com/soap2/?wsdl&v=15&s=rpc')
    auth_type = client.get_type('ns0:authInfo')
    myAuthInfo = auth_type(username=rrUser, password=rrPass, appKey='28801163', version='15',
                           style='rpc')

    # prompt user for system ID

    sysName = client.service.getTrsDetails(rrSystemId, myAuthInfo).sName
    sysresult = client.service.getTrsDetails(rrSystemId, myAuthInfo).sysid
    sysid = sysresult[0].sysid
    print(sysName + ' system selected.')

    # download talkgroups for given sysid
    Talkgroups_type = client.get_type('ns0:Talkgroups')
    result = Talkgroups_type(client.service.getTrsTalkgroups(rrSystemId, 0, 0, 0, myAuthInfo))
    #print(result)

    # construct the talkgroup and blacklist lists
    talkgroups = []
    for row in result:
        if row.enc == 0:
            talkgroups.append([row.tgDec, row.tgAlpha])#description row.tgDescr
        else:
            pass

    try:
        os.makedirs('systems')
    except:
        pass
    try:
        os.makedirs('systems/' + sysid[0].sysid)
    except:
        pass

    def createSitedb():
        client_type = client.get_type('ns0:TrsSites')
        result = client_type(client.service.getTrsSites(rrSystemId, myAuthInfo))

        try:
            os.makedirs('systems/' + sysid)
        except OSError as e:
            pass

        with open(op25OutputPath + '/systems/' + sysid + '/sitelocations.tsv', 'a+') as op25OutputFile:
            op25OutputFile.write('rfss \t site \t lat \t lon \t range\t SiteDescription\n')

        count = 0
        for i in range(len(result)):
            try:
                rfss = str(result[count].rfss)
                site = str(result[count].siteNumber)
                lat = str(result[count].lat)
                lon = str(result[count].lon)
                siterange = str(result[count].range)
                sitedescr = str(result[count].siteDescr)
                with open(op25OutputPath + '/systems/' + sysid + '/sitelocations.tsv', 'a+') as op25OutputFile:
                    op25OutputFile.write(rfss + '\t' + site + '\t' + lat + '\t' + lon + '\t' +siterange + '\t' + sitedescr + '\n')
                count = count + 1
            except Exception as e:
                print(e)
                count = count + 1
                pass

    createSitedb()
    #exit()
    #s384r003s02trunk.tsv

    def createtalkgroupList():
        try:
            os.makedirs('systems/' + sysid)
        except:
            pass


        # output tsv files
        count = 0
        for i in range(len(talkgroups)):
            try:
                result = talkgroups[count]
                tgid = str(result[0])
                tgtag = str(result[1])#.replace('OMMRC', '')
                with open(op25OutputPath + 'systems/' + sysid + '/talkgroups.tsv', 'a+') as op25OutputFile:
                    op25OutputFile.write(tgid + '\t' + tgtag + '\r\n')  # tgid -tab- talkgroup tag
                count = count + 1
            except Exception as e:
                print(e)
                count = count + 1
                pass

    createtalkgroupList()

    def createSites():
        # Sites represented as Trunk.tsv files for OP25 consumption
        client_type = client.get_type('ns0:TrsSites')
        result = client_type(client.service.getTrsSites(rrSystemId, myAuthInfo))

        try:
            os.makedirs('systems/' + sysid + '/sites')
        except OSError as e:
            pass

        trunktsvHeader = '"Sysname"\t' + '"Control Channel List"\t' + '"Offset"\t' + '"NAC"\t' + '"Modulation"\t' + '"TGID Tags File"\t' + '"Whitelist"\t' + '"Blacklist"\t' + '"Center Frequency"\n'

        count = 0
        for i in range(len(result)):
            try:
                r = requests.get('https://www.radioreference.com/apps/db/?siteId=' + str(result[count].siteId))

                soup = BeautifulSoup(r.text, 'html.parser')
                grablinks = soup.find_all('a')
                county = re.findall('(?:ctid.*">)(.*\w)<', str(grablinks))[0]

                sitefreqs = result[count].siteFreqs

                controlcount = 0
                altList = []
                for i in range(len(sitefreqs)):
                    if sitefreqs[controlcount].use == "d":
                        dedicatedCC = str(sitefreqs[controlcount].freq)
                    if sitefreqs[controlcount].use == "a":
                        altList.append(str(sitefreqs[controlcount].freq))
                        alternateCC = re.sub("(\[|\]|')", "", str(altList))
                    else:
                        pass
                    controlcount = controlcount + 1

                systemC = '"' + sysName + ': ' + county + '"'
                cclist = '"' + dedicatedCC + ',' + alternateCC + '"'
                offset = '"0"'
                nac = '"0"'
                modulation = '"CQPSK"'
                tagfile = '"'+op25OutputPath + 'systems/' + sysid + '/talkgroups.tsv"'
                whitelist = '""'
                blacklist = '"' +op25OutputPath + 'blacklist.tsv"'
                centerfreq = '""'

                rfss = str(result[count].rfss)
                site = str(result[count].siteNumber)


                with open(op25OutputPath + '/systems/' + sysid + '/sites/' + 'rfss'+rfss+'site'+site + '.tsv', 'a+') as op25OutputFile:
                    op25OutputFile.write(
                        trunktsvHeader + systemC + '\t' + cclist + '\t' + offset + '\t' + nac + '\t' + modulation + '\t' + tagfile + '\t' + whitelist + '\t' + blacklist + '\t' + centerfreq)

                count = count + 1
            except Exception as e:
                print(e)
                count = count + 1
                pass
    createSites()




####################END Radio Reference Import####################

def startop25(sdr='rtl', lna='49', samplerate='2000000', trunkfile='trunk.tsv', offset='0', op25dir=''):
    import os

    #op25dir = "op25/op25/gr25-op_repeater/apps"
    screen = "screen -Sdm op25 ./rx.py --args '" + sdr + "' -N 'LNA:" + lna + "' -S " + samplerate + " -o 25000 -T " + trunkfile + " -U -V -2 -X -l http:0.0.0.0:8080"

    os.popen('cd ' + op25OutputPath + ' && ' + screen)

def stopop25():
    import os
    os.popen('screen -X -S op25 quit')

def blacklistRange(enabled):
    try:
        blacklistFile = open(op25OutputPath + 'blacklist.tsv', 'r+')
        blacklist = blacklistFile.read()
        print("Full Blacklist: " + blacklist)
    except:
        blacklistFile = open(op25OutputPath + 'blacklist.tsv', 'w')
        blacklistFile.write('#0\t65536')
        blacklistFile = open(op25OutputPath + 'blacklist.tsv', 'r+')
        blacklist = blacklistFile.read()
        print("Full Blacklist: " + blacklist)
    if enabled == True: #True means you  want the range to exist, remove comment
        print('true')
        if "#0" in blacklist: #IF you don't see
            print('Block All Talkgroups by Default')
            modified = re.sub('^#0', '0', blacklist)
            blacklistFile = open(op25OutputPath + 'blacklist.tsv', 'w')
            blacklistFile.write(modified)
            blacklistFile.close()
        if "#0" not in blacklist:
            print('Block Only Talkgroups in blacklist')
            pass
    if enabled == False: #False means you want to comment out the range
        print('false')
        if "#0" in blacklist: #If you see "#0" then you lave it alone
            print('Block All Talkgroups by Default')
            pass
        if "#0" not in blacklist: #if you see see "0" then append the #
            print('Block Only Talkgroups in blacklist')
            modified = re.sub('^0', '#0', blacklist)
            blacklistFile = open(op25OutputPath + 'blacklist.tsv', 'w')
            blacklistFile.write(modified)
            blacklistFile.close()


##Working on blacklist range, there is a blacklistrange command run around the startop25 command1!!!!!!!!!1
#
#
#
#
#
#
#
#
#
#
#


####################Command and Control Socket Server####################

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('Listening for commands....\r\n')
    connection, client_address = sock.accept()
    try:
        #print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1028)
            if data:
                print('Echoing Data back to op25mch_client')
                connection.sendall(data)
                decoded = data.decode('utf-8')
                function = re.findall("(.*)(?:,.{)", decoded)[0]
                #print(function)
                print('Found Function: ' + function)
                payload = re.findall("({.*})", str(decoded))[0]
                #print(payload
                dict = ast.literal_eval(payload)
                #print(dict['rrUser'])
                if function == 'radioreference':
                    #print('Found Function: ' + function + ' Generating TSV Files')
                    generateTSV(rrUser=dict['rrUser'], rrPass=dict['rrPass'], rrsysid=dict['sysID'], op25dir=op25OutputPath)
                if function == 'startop25':
                    startop25(sdr=dict['sdr'], lna=dict['lna'], samplerate=dict['samplerate'], trunkfile=dict['trunkfile'], op25dir=op25OutputPath)
                if function == 'stopop25':
                    stopop25()
                if function == 'enableblacklistrange':
                    blacklistRange(enabled=True)
                if function == 'disableblacklistrange':
                    blacklistRange(enabled=False)


            else:
                #print('no data from', client_address)
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up the connection
        connection.close()
