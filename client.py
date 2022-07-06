from socket import socket
from zlib import decompress
import streamlit as st
import cv2
import numpy as np
from win32api import GetSystemMetrics
from PIL import Image
import io
import base64
import pickle

#containers
head = st.container()
section_1 = st.container()


WIDTH = GetSystemMetrics(0)
HEIGHT = GetSystemMetrics(1)

HEADER = 64
FORMAT = 'utf-8'
MSG_DISCONNECTED = '!DISCONNECTED'

host = '192.168.71.1'
port = 9090
client = socket()
client.connect((host, port))

def recvall(conn, length):
    #Retreive all pixels.

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf





with head:
    titile = st.title("Connect to view the record screen")

with section_1:
    st_frame = st.empty()

    def screen_video():
        watching = True   
        stop_btn = st.button("Stop", key="stop_btn")
        try:
            while watching:
                # Create an Empty window
                cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
                # Resize this window
                cv2.resizeWindow("Live", 480, 270)
                
                

                # Retreive the size of the pixels length and pixels
                size_len = int.from_bytes(client.recv(1), byteorder='big')
                size = int.from_bytes(client.recv(size_len), byteorder='big')
                #pixels = decompress(recvall(sock, size))
                #pixels = recvall(sock, size)
                
                pixels = pickle.loads(decompress(base64.b64decode(recvall(client, size))))
                
                frame_final = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
                #print(type(frame_final))
                #cv2.imshow("Live", frame_final)
                st_frame.image(frame_final)
                if stop_btn:
                    #send(MSG_DISCONNECTED)
                    break
                else: continue

                # Create the Surface from raw pixels
                

        finally:
            client.close()

    start_btn = st.button("Connect to the server", key="start", on_click=screen_video)

