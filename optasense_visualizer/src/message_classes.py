""" Classes saving message values """

from dataclasses import dataclass

class UnknownMessageException(Exception):
    """ This exception is called when unknown message is sent
         It is supressed because we don't want to end the app when such message is received
    """
    def __init__(self, type, message, *args: object) -> None:
        super().__init__(*args)
        print(f"Unknown message type {type}, {message}")

class MessageFactory:
    """ Parse messages, basically a factory class """
    def __init__(self) -> None:
        pass

    def parse(self, type, message):
        print("PARSE")
        print(message)
        if type == "path":
            return FindFiles(message.get("path"), message.get("suffix"))
        if type == "openfile":
            return OpenFile(message["filename"], 
                            message.get("datasetname", ""), 
                            message.get("selected_channels", "all"))
        if type == "stream":
            return Streaming(message.get("value"))
        if type == "properties":
            return Properties(message.get("channel_count"),
                              message.get("subsampling"))
        if type == "initapp":
            return InitApp(message.get("message"))
        if type == "channel_selection":
            return ChannelSelection(message.get("channel_selection"))
        
        raise UnknownMessageException(type, message)


@dataclass
class InitApp:
    message: str


@dataclass
class FindFiles:
    path: str
    suffix: str

@dataclass
class OpenFile:
    filename: str
    datasetname: str
    selected_channels: str

@dataclass
class Streaming:
    value: str

@dataclass
class Properties:
    channel_count: str
    subsampling: int

@dataclass
class ChannelSelection:
    selected_channels: str