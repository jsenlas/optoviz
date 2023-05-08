
#!/usr/bin/env python

import asyncio
import contextlib
import websockets
import json
from datetime import datetime as dt
from argparse import ArgumentParser
from random import randint
# from src.optasense_server import Server
# from src.message_classes import FindFiles, OpenFile, Streaming, Properties, InitApp
import numpy as np

with open("outdata.npy", "r") as fp:
    x = np.load(fp)
    print(x)

# queue = asyncio.Queue()

# data = spectral_analysis(data=data, pulse_rate=1024)
# print("After analysis:", data)
# print(data.shape)
######3data = np.interp(data, (np.min(data), np.max(data)), (0,1000))
# spectral_analysis()
# # for i in dataset:
# try:
#     data = dataset[:,[i]]
#     print("RAW", data.shape)
#     # data = dataset[:,[i]]
# except Exception as exc:
#     print(exc)
#     try:
#         print(exc.message)
#     except:
#         pass
# # if selected_channels_str:
# #     data = dataset[:, selected_channels].copy()
# # else:
# #     data = dataset[:].copy()