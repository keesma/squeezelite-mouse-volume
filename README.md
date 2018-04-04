# squeezelite-mouse-volume

Control squeezelite with a (wireless) mouse running on a raspberry pi.
Plug the bluetooth mouse receiver into the raspberry pi.

Current configuration:
- middle button: play / pause
- scroll wheel: volume
- middle button and scroll wheel: previous / next track
- left button: previous track
- right button: next track

Set the name of you logitech media server and the name of the player you want to control before starting it. Also plugin the mouse receiver before starting it.

- SERVER_IP = "lms"
- PLAYER_NAME = "playername"

It is tested with a Raspberry Pi, Logitech M560 mouse with unifying receiver and a IQAudio DigiAmp+.

Many thanks to https://github.com/elParaguayo/LMSTools for the LMS library.

Add the script to the startup of the raspberry.
