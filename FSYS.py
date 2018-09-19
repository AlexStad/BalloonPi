#!/usr/bin/python
# FLIGHTSYSTEM
# This system is comprised of 4 parts: GPSLOG, GPS, ROCK and EXEC.
# GPSLOG records extensive GPS data on a text file, which serves as a GPS log.
# GPS writes GPS data on a temporary text file
# ROCK reads the temporary text file and sends it to the Iridium net.
# EXEC executes CAM and GPSLOG every 30 minutes and GPS and ROCK every hour.
# ROCK refers to a Python library by MakerSnake:
# https://github.com/MakerSnake/pyRockBlock - All credits to MakerSnake!

import os
import gps
import time
import threading
import rockBlock
from rockBlock import rockBlockProtocol

os.chdir("/home/pi/Desktop/FLIGHT_MODULE")
gpsd = None                             # sets global variable


class GpsPoller(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd                     # bring in scope
        gpsd = gps(mode="WATCH_ENABLE")   # starting stream of info
        self.current_value = None
        self.running = True             # setting thread running to true


# GPSLOG Part
def GPSLOG():
    global gpsp
    gpsp = GpsPoller()                  # create thread
    gpsp.start()                        # start up
    counter = 0
    while gpsd.fix.mode < 2:            # ensures 3D fix
        time.sleep(3)
        counter += 1
        if counter > 5:
            gpsp.running = False
            gpsp.join()
            break
    t = open('GPSDataLog', 'a')
    latlong = str(gpsd.fix.latitude) + ", " + str(gpsd.fix.longitude)
    t.write("\nlat, long     " + latlong)
    t.write("\ntime utc      " + str(gpsd.utc))
    t.write("\naltitude      " + str(gpsd.fix.altitude))
    t.write("\neps           " + str(gpsd.fix.eps))
    t.write("\nepx           " + str(gpsd.fix.epx))
    t.write("\nepv           " + str(gpsd.fix.epv))
    t.write("\nept           " + str(gpsd.fix.ept))
    t.write("\nspeed (m/s)   " + str(gpsd.fix.speed))
    t.write("\nclimb         " + str(gpsd.fix.climb))
    t.write("\ntrack         " + str(gpsd.fix.track))
    t.write("\nmode          " + str(gpsd.fix.mode))
    t.write("\nsats          " + str(gpsd.satellites))
    t.close()
    gpsp.running = False
    gpsp.join()                         # wait for thread to finish


# GPS Part
def GPS():
    global gpsp
    gpsp = GpsPoller()                  # create thread
    gpsp.start()                        # start up
    counter = 0
    while gpsd.fix.mode < 2:            # ensures 3D fix
        time.sleep(3)
        counter += 1
        if counter > 10:
            gpsp.running = False
            gpsp.join()
            break
    t = open('GPSDataMessage', 'w')
    t.write("\n" + str(gpsd.fix.latitude) + ", " + str(gpsd.fix.longitude))
    t.write("\n" + str(gpsd.fix.altitude))
    t.write("\n" + str(gpsd.fix.speed))
    t.write("\n" + str(gpsd.fix.climb))
    t.close()
    gpsp.running = False
    gpsp.join()                         # wait for thread to finish


# ROCK Part
class ROCK (rockBlockProtocol):

    def sendMsg(self):                  # Sends Message
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        t = open('GPSDataMessage', 'r')  # Sets content
        message = t.read()
        t.close()
        rb.sendMessage(message)
        rb.close()

    def rockBlockTxFailed(self):        # Transmission Failed
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        rb.close()
        self.sendMsg()

    def rockBlockTxSuccess(self):
        rb = rockBlock.rockBlock("/dev/ttyUSB0", self)
        rb.close()


# EXEC Part
while True:
    try:
        GPS()
        ROCK().sendMsg()
    except Exception:
        pass
    try:
        GPSLOG()
    except Exception:
        pass

    time.sleep(1800)

    try:
        GPSLOG()
    except Exception:
        pass

    time.sleep(1800)
