import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import websocket
import json
import win32api, win32con
from LeapLibrary import Leap

import logging
logging.basicConfig(filename='errors.log', filemode='w', level=logging.DEBUG)
		
mouseMove = 0 # flag for detected if last action was click		
		
def on_open(ws):
	enableMessage = "{enableGestures: true}" # Enable gestures to be used
	ws.send(json.dumps(enableMessage))
	ws.send(json.dumps("{focused: true}"))
	
def on_message(ws, message):
	global mouseMove
	frame_data = json.loads(message) # Convert frame data from websocket to Python format
	finger = []
	for i in range(0,len(frame_data['pointables'])):
		finger.append(((frame_data['pointables'])[i])['id']) # Add IDs of all fingers to list
	
	# Cursor positions used for mouse movement and clicking
	cursor_X = 0.00 
	cursor_Y = 0.00
	if len(finger) == 1: # Exactly 1 Finger
		fingerString = str(finger[0])
		if fingerString[-1] == '1': # Check if Index Finger
			mouseMove = 1
			screen_X_size = float(235)/win32api.GetSystemMetrics(0) # scaling factor of fingertip X position to screen size
			screen_Y_size = float(235)/win32api.GetSystemMetrics(1) # scaling factor of fingertip Y position to screen size
			if (frame_data['pointables'][0]['stabilizedTipPosition'][0]) > 117.5: # If fingertip reaches right edge of interaction zone, stay at right edge of screen
				cursor_X = win32api.GetSystemMetrics(0)
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][0]) < -117.5: # If fingertip reaches left edge of interaction zone, stay at left edge of screen
				cursor_X = 0
			else:
				cursor_X = int((frame_data['pointables'][0]['stabilizedTipPosition'][0] + 117.5)/screen_X_size)
			
			if (frame_data['pointables'][0]['stabilizedTipPosition'][1]) > 485.7: # If fingertip reaches top edge of interaction zone, stay at top edge of screen
				cursor_Y = 0
			elif (frame_data['pointables'][0]['stabilizedTipPosition'][1]) < 82.5: # If fingertip reaches bottom edge of interaction zone, stay at bottom edge of screen
				cursor_Y = win32api.GetSystemMetrics(1)
			else:
				cursor_Y = win32api.GetSystemMetrics(1) - int((frame_data['pointables'][0]['stabilizedTipPosition'][1] - 82.5)/screen_Y_size)
			
			win32api.SetCursorPos((cursor_X, cursor_Y))
			
	elif len(finger) == 2: # Exactly 2 Fingers
		correctFingers = False
		for i in range(0,len(finger)): # Check each pointable ID
			fingerString = str(finger[i]) # Convert ID to string
			if i == 0: # Check first pointable ID
				if fingerString[-1] == '1': # Check if Index Finger
					correctFingers = True # First finger is Index Finger
				else:
					correctFingers = False
					break
			elif i == 1: # Check second pointable ID
				if fingerString[-1] == '2': # Check if Middle Finger
					correctFingers = True # Second finger is Middle Finger
				else:
					correctFingers = False
					break
			else:
				pass
				
		if correctFingers:
			direction = []
			for i in range(0,len(frame_data['pointables'])): # Get direction values
				direction.append(frame_data['pointables'][i]['direction'])
			# Get dot product of finger direction vector and gesture normal vector
			
			directionVector1 = Leap.Vector(direction[0][0], direction[0][1], direction[0][2])
			directionVector2 = Leap.Vector(direction[1][0], direction[1][1], direction[1][2])
			normalVector = Leap.Vector(frame_data['gestures'][0]['normal'][0], frame_data['gestures'][0]['normal'][1], frame_data['gestures'][0]['normal'][2])
			
			dotProduct1 = Leap.Vector.dot(directionVector1, normalVector)
			dotProduct2 = Leap.Vector.dot(directionVector2, normalVector)
			
			# Check for clockwise/counterclockwise gesture
			clockwise = 0 # 0 = No movement; 1 = Clockwise; 2 = Counterclockwise
			if (dotProduct1 > 0) and (dotProduct2 > 0):
				clockwise = 1
			elif (dotProduct1 < 0) and (dotProduct2 < 0):
				clockwise = 2
			else:
				pass
				
			# Left click if clockwise circle gesture
			cursor_X = int(cursor_X)
			cursor_Y = int(cursor_Y)
			if clockwise == 1:
				# perform left click
				if mouseMove == 1:
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, cursor_X, cursor_Y, 0, 0)
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, cursor_X, cursor_Y, 0, 0)
					clockwise = 0
					mouseMove = 0
			elif clockwise == 2:
				# perform right click
				if mouseMove == 1:
					win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, cursor_X, cursor_Y, 0, 0)
					win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, cursor_X, cursor_Y, 0, 0)
					clockwise = 0
					mouseMove = 0
			else:
				pass
		else: # Pass
			pass	
	elif len(finger) > 2:
		gestureType = frame_data['gestures'][0]['type']
		if gestureType == 'swipe':
			cursor_X = int(cursor_X)
			cursor_Y = int(cursor_Y)
			# if magnitude of y is greated than x and z
			if abs(frame_data['gestures'][0]['direction'][1]) > (abs(frame_data['gestures'][0]['direction'][0]) and abs(frame_data['gestures'][0]['direction'][2])):
				if frame_data['gestures'][0]['direction'][1] > 0:
					# hand goes from bottom to top, scroll up
					win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, cursor_X, cursor_Y, -10, 0)
				elif frame_data['gestures'][0]['direction'][1] < 0:
					# hand goes from top to bottom, scroll down
					win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, cursor_X, cursor_Y, 10, 0)
				else:
					pass
			else:
				pass
		else:
			pass
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