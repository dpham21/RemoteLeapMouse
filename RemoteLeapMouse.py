import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import websocket
import json
import win32api
from win32api import GetSystemMetrics

import logging
logging.basicConfig()
		
def on_open(ws):
	enableMessage = "{enableGestures: true}" # Enable gestures to be used
	ws.send(json.dumps(enableMessage))
	ws.send(json.dumps("{focused: true}"))
	
def on_message(ws, message):
	frame_data = json.loads(message) # Convert frame data from websocket to Python format
	finger = []
	for i in range(0,len(frame_data['pointables'])):
		finger.append(((frame_data['pointables'])[i])['id']) # Add IDs of all fingers to list
	
	if len(finger) > 1: # More than 1 finger, pass
		pass
	elif len(finger) == 1: # Exactly 1 Finger
		fingerString = str(finger[0])
		if fingerString[-1] == '1': # Check if Index Finger
			cursor_X = 0.00
			cursor_Y = 0.00
			screen_X_size = float(235)/GetSystemMetrics(0) # scaling factor of fingertip X position to screen size
			screen_Y_size = float(235)/GetSystemMetrics(1) # scaling factor of fingertip Y position to screen size
			if (frame_data['pointables'][0]['stabilizedTipPosition'][0]) > 117.5: # If fingertip reaches right edge of interaction zone, stay at right edge of screen
				cursor_X = GetSystemMetrics(0)
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][0]) < -117.5: # If fingertip reaches left edge of interaction zone, stay at left edge of screen
				cursor_X = 0
			else:
				cursor_X = int((frame_data['pointables'][0]['stabilizedTipPosition'][0] + 117.5)/screen_X_size)
			
			if (frame_data['pointables'][0]['stabilizedTipPosition'][1]) > 485.7: # If fingertip reaches top edge of interaction zone, stay at top edge of screen
				cursor_Y = 0
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][1]) < 82.5: # If fingertip reaches bottom edge of interaction zone, stay at bottom edge of screen
				cursor_Y = GetSystemMetrics(1)
			else:
				cursor_Y = GetSystemMetrics(1) - int((frame_data['pointables'][0]['stabilizedTipPosition'][1] - 82.5)/screen_Y_size)
			
			win32api.SetCursorPos((cursor_X, cursor_Y))
	else: # Pass
		pass
	
def on_close(ws):
	pass
	
def on_error(ws, error):
	print error

if __name__ == "__main__":
	ws = websocket.WebSocketApp("ws://10.159.157.186:8889/v6.json", #connect to websocket server, address should be local IP of server
								on_message = on_message,
								on_close = on_close,
								on_error = on_error)
	ws.on_open = on_open
	ws.run_forever()