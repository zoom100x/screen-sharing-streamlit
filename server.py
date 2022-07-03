import streamlit as st

from threading import Thread
import base64
#from win32api import GetSystemMetrics
from zlib import compress
import datetime

import socket
import numpy as np
import cv2
import pickle
import mss

#containers
head = st.container()
section_1 = st.container()
section_2 = st.container()


#constants
TOP = 0
LEFT = 0
WIDTH = 1280
HEIGHT = 720
IP = '0.0.0.0'
PORT = 9090
HEADER = 64
FORMAT = 'utf-8'
MSG_DISCONNECTED = '!DISCONNECTED'

#Setting name to screenvideo
time_d = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
file_name =f'{time_d}.mp4'
path = f'./video/{file_name}'
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
connected = False


with head:
	title = st.title("Screen recorder app")
	ip_adress= st.write(socket.gethostname())
	

with section_1:
	def retreive_screenshot(conn):
		frame_rate = 10.0
		captured_video = cv2.VideoWriter(path, fourcc, frame_rate, (WIDTH, HEIGHT))
		
		with mss.mss() as sct:
			# The region to capture
			rect = {'top': TOP, 'left': LEFT, 'width': WIDTH, 'height': HEIGHT}

			connected = True

			while connected:
				# Capture the screen
				img = sct.grab(rect)

				#saving the video
				img_np = np.array(img)
				frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
				frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				captured_video.write(frame)

				
				# Tweak the compression level here (0-9)
				pixels = base64.b64encode(compress(pickle.dumps(img_np), 9))

				# Send the size of the pixels length
				size = len(pixels)
				size_len = (size.bit_length() + 7) // 8
				conn.send(bytes([size_len]))

				# Send the actual pixels length
				size_bytes = size.to_bytes(size_len, 'big')
				conn.send(size_bytes)

				# Send pixels
				conn.sendall(pixels)

		conn.close()
		captured_video.release()

	def start_server_listening():
		#initialize server
		server = socket.socket()
		server.bind((IP, PORT))

		#start lestining
		server.listen(5)
		starting_text = st.write(f"Server is listening on {IP}")
		while 'connected':
			conn, addr = server.accept()
			client_added_text = st.write(f"[NEW CONNECTION] {addr} connected.")
			#retreive_screenshot(conn)
			thread = Thread(target=retreive_screenshot, args=(conn,))
			thread.start()


	start_server_btn = st.button("Commencer l'enregistrement", key="start_btn", on_click=start_server_listening)

with section_2:
	stop = st.button("Stop", key="stop")
	if stop:
		connected = False
		st.stop()
