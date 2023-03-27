# import numpy as np
from json import dumps
from asyncio import Event, create_task, wait, sleep
from .file_reader import Buffer


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

    def open_stream(self, content):
        self.content = content
        self.streaming_wait_event.clear()
        self._create_stream_task()
        print("Stream opened")

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

    async def stream_data(self):

        # self.file_reader.read_dataset()
        # self.file_reader.content
        while True:
            # ensures that scheduler has time to check received messages
            # so that sending data does not block receiving messages
            await sleep(1) # TODO set to 0

            if not self.streaming_wait_event.is_set():
                await self.websocket.send(
                    dumps({
                        "type": "ready"
                }))
                print("Stream waiting for an event...")
            await self.streaming_wait_event.wait()
            print("Streaming")
            await self.websocket.send(
                dumps({
                    "type": "data",
                    "data": self.get_data()
            }))
            self.increment_content_index()

    def stop_streaming(self):
        self.streaming_wait_event.clear()
        if self.streaming_task:
            self.streaming_task.cancel()
            print("Streaming task stopped")
        print("Stream stopped")

    def increment_content_index(self):
        self.content_i += 1

    def get_data(self):
        return self.buffer.generate_content()[0]  # TODO
        # print(self.content[self.content_i])
        # return self.content[self.content_i]
