
#!/usr/bin/env python

import asyncio
import contextlib
import websockets
import json
from datetime import datetime as dt
from argparse import ArgumentParser
from random import randint
from src.optasense_server import Server
from src.message_classes import FindFiles, OpenFile, Streaming, Properties, InitApp

queue = asyncio.Queue()

