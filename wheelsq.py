#!/usr/bin/python
#
# Change volume with the mouse scroll wheel, pause, play and previous, next track
# for Logitech Media Server (LMS) players
#
# I control squeezelite on a Raspberry Pi with my wireless Logitech mouse.
# The unifying bluetooth receiver is plugged into the raspberry pi.
# Which player is controlled is now hardcoded. 
#
# Preqrequisites
#   sudo apt-get install python-pip python-dev build-essential 
#   sudo pip install --upgrade pip 
#   sudo pip install --upgrade virtualenv 
#   sudo pip install evdev
#
# Verify with "ls /dev/input/*" which events apply for the mouse.
#
# Many thanks to:
#   https://www.raspberrypi.org/forums/viewtopic.php?t=42046
#   https://github.com/elParaguayo/LMSTools
#
# To do
# - retry after some time if a mouse has not been found.
# - make the script more flexible to support multiple players.
#

#
# Configuration: set the LMS server host name and the name of the player to control.
#
SERVER_IP = "lms"
PLAYER_NAME = "woonkamer"

from LMSTools import LMSServer
import logging
from evdev import InputDevice
import evdev 
from select import select
import signal
import sys
import time

def signal_handler(signal, frame):
        logging.debug('You pressed Ctrl+C!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info('Mouse volume control for a Logitech Media Server player.')

dev = None
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    logging.debug("input: %s name:%s phys:%s", device.fn, device.name, device.phys)
    if device.name.find("Mouse") > 0:
        dev = InputDevice(device.fn)
        logging.debug("Mouse linked to event %s", device.fn)
if dev is None:
    logging.info('The mouse is not detected.')
    sys.exit(0)
logging.debug("%s", dev.capabilities(verbose=True))

server= LMSServer(SERVER_IP)

# Find the player by name
myplayer = None;
players = server.get_players()
for player in players:
    logging.debug("Player : %s", player);
    if player.name==PLAYER_NAME:
        myplayer = player;
if myplayer is None:
    logging.info('Player %s is not detected.', PLAYER_NAME)
    sys.exit(0)

def get_volume(zone):
    "get current volume"
    try:
        result = zone.volume
        logging.debug("%s, volume: %d", zone.name, result)
    except:
        logging.warning("%s, Cannot read volume", zone.name)
        result = 0;
        pass;
    return result

def play_previous(zone):
    "skip to previous track"
    logging.info("Previous track")
    try:
        zone.prev()
    except:
        logging.warning("%s, Cannot play previous track", zone.name)
        pass;
    return

def play_next(zone):
    "skip to next track"
    logging.info("Next track")
    try:
        zone.next()
    except:
        logging.warning("%s, Cannot play next track", zone.name)
        pass;
    return

def play_pause(zone):
    "toggle play/pause"
    logging.info("Play/pause track")
    try:
        zone.toggle()
    except:
        logging.warning("%s, Cannot play/pause", zone.name)
        pass;
    return

def change_volume(zone, new_vol):
    "set volumne"
    logging.info("Volume: %d", new_vol)
    try:
        zone.volume = new_vol
    except:
        logging.warning("%s, Cannot play/pause", zone.name)
        pass;
    return

short_press = False

msec = time.time() * 1000
while True:
    r,w,x = select([dev], [], [], 0.1)
    if (r):
        for event in dev.read():
#            print(event)
            if event.code == 8 or event.code == 6:  # scrollwheel
                if (short_press):  # is play/pause is pressed do prev/next track
                    if event.value < 0:
                        play_previous(myplayer)
                    else:
                        play_next(myplayer)
                else:
                    new_vol = get_volume(myplayer)
                    new_vol = new_vol + event.value
                    if new_vol < 0:
                        new_vol=0
                    elif new_vol > 100:
                        new_vol=100
                    change_volume(myplayer, new_vol)
            elif event.code == 277 or event.code == 274: # middle
#                logging.debug("middle: value: %d", event.value)
                if event.value == 1:
                    logging.debug("play/pause pressed")
                    short_press = True
                    msec = time.time() * 1000
                else:
                    if (time.time() * 1000) <= msec+500:
                        play_pause(myplayer)
                    else:
                        logging.debug("play/pause cancelled")
                    short_press = False
            elif event.code == 272:  # left: previous track
                if event.value==1:
                    play_previous(myplayer)
            elif event.code == 273:  # right: next track
                if event.value == 1:
                    play_next(myplayer)
#               elif (event.code <> 0 and event.code <> 1):
#                   print(event)
#                   logging.debug("Mouse event: %s", event.code)
