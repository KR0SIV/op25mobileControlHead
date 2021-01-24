import serial#pyserial
from gettext import lngettext


# Requirments Python3, pySerial 3.0

class BU343S4Driver:

    # @brief constructor for usb driver
    # @pararm serialPortName, virtual tty port of BU-343S4
    #
    #
    #
    def __init__(self, serialPortName):
        self.setup_serial_interface(serialPortName)

    # @brief connect to GPS USB virtual serial port
    # @param serialPortName, name of serial prot ex. "/dev/ttyUSB0"
    def setup_serial_interface(self, serialPortName):
        self.serialPort = serial.Serial(serialPortName, 4800, timeout=5)

    def get_ascii(self, s):
        x = 0
        for i in range(len(s)):
            x += ord(s[i]) * 2 ** (8 * (len(s) - i - 1))
        return x

    # @brief validates checksum GPGGA Line
    # @param GPGGA_Line ascii line recived from gps reciver
    # @return True if valid checksum or False otherwise
    def validate_checksum_GPGGA(self, GPGGA_Line):
        checksum_val = 0
        get_reported_check = False
        get_reported_checkSec = False
        reported_check_value = ""
        chkCmpVal = 0

        for i in GPGGA_Line:
            numVal = self.get_ascii(i)

            # get second reported checksum char
            if get_reported_check:
                if not get_reported_checkSec:
                    reported_check_value = i
                    get_reported_checkSec = True

                else:
                    chkCmpVal = int(reported_check_value + i, 16)

                    if chkCmpVal == checksum_val:
                        return True
                    else:
                        return False
                    break

            if not get_reported_check:
                # not equal to $, *, /r, /n
                if numVal != 36 and numVal != 42 and numVal != 13 and numVal != 10:
                    checksum_val = checksum_val ^ numVal

                # if at * get reported check value
                if numVal == 42:
                    get_reported_check = True

    # @brief quiery gps for position, this must be called before accessing any get methods
    #
    def update_position(self):

        # clear junk from buffer
        line = self.serialPort.readline()

        # wait until GPS sends data in the GPGGA format and GPGGA has valid checksum
        while 1:
            line = self.serialPort.readline()
            strLn = line.decode("Ascii")
            splitline = strLn.split(',')

            if splitline[0] == str("$GPGGA") and self.validate_checksum_GPGGA(strLn):
                break

            # parse out all gps data
            self.systemFixData = splitline[0]
            self.utcTime = splitline[1]
            self.latitude = splitline[2]
            self.latDirec = splitline[3]
            self.longitude = splitline[4]
            self.longDirec = splitline[5]
            self.fixQuality = splitline[6]
            self.trackedSatellites = splitline[7]
            self.horizontalDilution = splitline[8]
            self.altitudeAboveMeanSea = splitline[9]
            self.heightOfGeoid = splitline[11]



    # @brief returns GGA - Global Positioning System fix data record type
    #
    def get_systemFixData(self):
        return self.systemFixData

    # @brief returns utc [hhmmss.ss]
    #
    def get_utcTime(self):
        return self.utcTime

    # @brief returns Latitude in [DDMM.MMMMMM]
    #
    def get_latitude(self):
        return self.latitude

    # @brief returns latitude direction, E: for East, W: for West
    #
    def get_latDirec(self):
        return self.latDirec

    # @brief returns Longitude in [DDDMM.MMMMMM]
    #
    def get_longitude(self):
        return self.longitude

    # @brief returns Longitude direction, E: for East, W: for West
    #
    def get_longDirec(self):
        return self.longDirec

    # @brief returns fixQuality
    # GPS Quality Indicator
    #    0: fix not available
    #    1: GPS fix
    #    2: Differential GPS fix
    #    4: Real-Time Kinematic, fixed integers
    #    5: Real-Time Kinematic, float integers
    #
    def get_fixQuality(self):
        return self.fixQuality

    # @brief returns Number of GPS satellites being used [0 - 12]
    #
    def get_trackedSatellites(self):
        return self.trackedSatellites

    # @brief returns horizontal dilution of precision of fix
    #
    def get_horizontalDilution(self):
        return self.horizontalDilution

    # @brief returns altitude Above Mean Sea in meters
    #
    def get_altitudeAboveMeanSea(self):
        return self.altitudeAboveMeanSea

    # @brief returns heightOfGeoid / sea level
    #
    def get_heightOfGeoid(self):
        return self.heightOfGeoid
