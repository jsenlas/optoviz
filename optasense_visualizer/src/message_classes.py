""" Classes saving message values """

from dataclasses import dataclass

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

@dataclass
class Streaming:
    value: str

@dataclass
class Properties:
    channel_count: str
    subsampling: int
