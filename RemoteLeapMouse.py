import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import websocket
import json
import Leap
import win32api
from win32api import GetSystemMetrics

import logging
logging.basicConfig()
		
def on_open(ws):
	enableMessage = "{enableGestures: true}"
	ws.send(json.dumps(enableMessage))
	ws.send(json.dumps("{focused: true}"))
	
def on_message(ws, message):
	frame_data = json.loads(message)
	finger = []
	for i in range(0,len(frame_data['pointables'])):
		finger.append(((frame_data['pointables'])[i])['id'])
	
	if len(finger) > 1: # More than 1 finger, pass
		pass
	elif len(finger) == 1: # Exactly 1 Finger
		fingerString = str(finger[0])
		if fingerString[-1] == '1': # Check if Index Finger
			mouseX = 0.00
			mouseY = 0.00
			windowXsize = float(235)/GetSystemMetrics(0)
			windowYsize = float(235)/GetSystemMetrics(1)
			if (frame_data['pointables'][0]['stabilizedTipPosition'][0]) > 117.5:
				mouseX = GetSystemMetrics(0)
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][0]) < -117.5:
				mouseX = 0
			else:
				mouseX = int((frame_data['pointables'][0]['stabilizedTipPosition'][0] + 117.5)/windowXsize)
			
			if (frame_data['pointables'][0]['stabilizedTipPosition'][1]) > 485.7:
				mouseY = 0
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][1]) < 82.5:
				mouseY = GetSystemMetrics(1)
			else:
				mouseY = GetSystemMetrics(1) - int((frame_data['pointables'][0]['stabilizedTipPosition'][1] - 82.5)/windowYsize)
			
			win32api.SetCursorPos((mouseX,mouseY))
	else: # Pass
		pass
	
def on_close(ws):
	pass
	
def on_error(ws, error):
	print error

if __name__ == "__main__":
	ws = websocket.WebSocketApp("ws://10.159.157.186:8889/v6.json",
								on_message = on_message,
								on_close = on_close,
								on_error = on_error)
	ws.on_open = on_open
	ws.run_forever()