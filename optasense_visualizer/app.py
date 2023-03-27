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


class UnknownMessageException(Exception):
    """ This exception is called when unknown message is sent
         It is supressed because we don't want to end the app when such message is received
    """
    def __init__(self, type, message, *args: object) -> None:
        super().__init__(*args)
        print(f"Unknown message type {type}, {message}")

class MessageParser:
    """ Parse messages, basically a factory class """
    def __init__(self) -> None:
        pass

    def parse(self, type, message):
        print("PARSE")
        print(message)
        if type == "path":
            return FindFiles(message["path"], message["suffix"])
        if type == "openfile":
            return OpenFile(message["filename"], message.get("datasetname", ""))
        if type == "stream":
            return Streaming(message["value"])
        if type == "properties":
            return Properties(message.get("channel_count"),
                              message.get("subsampling"))
        if type == "initapp":
            return InitApp(message.get("message"))
        
        raise UnknownMessageException(type, message)


async def handler(websocket):
    """ Handling receiving packets """
    backend = Server(websocket)
    mp = MessageParser()

    # process messages
    async for message in websocket:
        print(f"## {dt.now()} ## -----------------------------------")
        print("MSG: ", message)
        event = json.loads(message)
        assert event["type"]

        with contextlib.suppress(UnknownMessageException):
            backend.state = mp.parse(event["type"], event)

        if isinstance(backend.state, FindFiles):
            backend.find_files(path=backend.state.path,
                               suffix=backend.state.suffix)

            event = {
                "type": "choose_files",
                "files": backend.local_files
            }
            await websocket.send(json.dumps(event))

        if isinstance(backend.state, OpenFile):
            with contextlib.suppress(AttributeError):
                if backend.state.datasetname:
                    backend.dataset_name = backend.state.datasetname
            backend.open_file(backend.state.filename)
            if not backend.dataset_name:
                print(backend.dataset_path_list)
                event = {
                    "type": "dataset_content",
                    "content": backend.dataset_path_list
                }
                await websocket.send(json.dumps(event))

        if isinstance(backend.state, Streaming):
            backend.stream.set_streaming(backend.state.value)


def parse_args():
    """ parse arguments """
    parser = ArgumentParser(description='DAS file visualization software. Server application.')

    parser.add_argument("--port", action="store", dest="port", default="8001",
                        help="Port number for websocket.")

    return parser.parse_args()


async def main():
    """ Int he beginning there was main() """
    args = parse_args()

    async with websockets.serve(handler, "localhost", args.port):
        print(f"App is running on port {args.port}...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())