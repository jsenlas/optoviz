#!/usr/bin/env python

import asyncio
import contextlib
import websockets
import json
from datetime import datetime as dt
from argparse import ArgumentParser
from random import randint
from src.optasense_server import Server
from src.message_classes import FindFiles, OpenFile, Streaming, Properties, InitApp, ChannelSelection, MessageFactory, ExportToWAV, UnknownMessageException

async def handler(websocket):
    """ Handling receiving packets """
    backend = Server(websocket)
    message_factory = MessageFactory()

    # process messages
    async for message in websocket:
        print(f"## {dt.now()} ## -----------------------------------")
        print("MSG: ", message)
        event = json.loads(message)
        assert event["type"]

        with contextlib.suppress(UnknownMessageException):
            backend.state = message_factory.parse(event["type"], event)

        if isinstance(backend.state, FindFiles):
            backend.find_files_backend(path=backend.state.path,
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
            backend.open_file(backend.state.filename, backend.state.selected_channels)
            if not backend.dataset_name:
                print(backend.dataset_path_list)
                event = {
                    "type": "dataset_content",
                    "filename": backend.state.filename,
                    "content": backend.dataset_path_list,
                }
                await websocket.send(json.dumps(event))

        if isinstance(backend.state, Streaming):
            backend.stream.set_streaming(backend.state.value)
        if isinstance(backend.state, ChannelSelection):
            if backend.dataset_name:
                backend.open_file(backend.file_reader.filename, backend.state.selected_channels)
            else:
                print("No file opened.")
                await websocket.send(json.dumps({"warning": "No file opened."}))
        if isinstance(backend.state, ExportToWAV):
            pass


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