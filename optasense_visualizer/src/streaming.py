# import numpy as np
from json import dumps
from asyncio import Event, create_task, wait, sleep
from .file_reader import Buffer, DASHDF5FileReader


class Stream:
    def __init__(self, websocket) -> None:
        self.websocket = websocket
        self.buffer = Buffer(x=100, y=100)
        self.state = "stop"
        self.streaming_wait_event = Event()
        self.streaming_task = None
        self.content_i = 0
        self.content = []

    def _create_stream_task(self):
        if not self.streaming_task or self.streaming_task.cancelled:
            self.streaming_task = create_task(self.stream_data())

    def open_stream(self):
        self.streaming_wait_event.clear()
        self._create_stream_task()

    def start_streaming(self):
        self.streaming_wait_event.set()
        # self._create_stream_task()
        print("Stream started")

    def pause_streaming(self):
        self.streaming_wait_event.clear()
        print("Stream paused")

    def set_streaming(self, value: bool):
        self.state = value
        if self.state == "play":
            self.start_streaming()
        elif self.state == "pause":
            self.pause_streaming()
        elif self.state == "stop":
            self.stop_streaming()
    
    def generator_init(self, filename, datasetname, selected_channels):
        self.filename = filename
        self.datasetname = datasetname
        self.selected_channels = selected_channels
        self.reader = DASHDF5FileReader(filename, datasetname, selected_channels)
        self.reader.preprocess()


    async def stream_data(self):
        # while True:
        print("Stream opened")
        # async for msg in self.reader.read_dataset(self.datasetname, self.selected_channels):
        async for msg in self.reader.read_dataset_v2():
            # ensures that scheduler has time to check received messages
            # so that sending data does not block receiving messages
            await sleep(0.01) # TODO set to 0

            if not self.streaming_wait_event.is_set():
                await self.websocket.send(
                    dumps({
                        "type": "ready"
                }))
                print("Stream waiting for an event...")
            await self.streaming_wait_event.wait()
            print(".", end="")
            await self.websocket.send(msg)

    def stop_streaming(self):
        self.streaming_wait_event.clear()
        if self.streaming_task:
            self.streaming_task.cancel()
            print("Streaming task stopped")
        print("Stream stopped")
