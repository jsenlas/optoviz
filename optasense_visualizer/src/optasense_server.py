#!/usr/bin/env python
from random import randint
import numpy as np
from .file_reader import find_h5_files, find_files, DASHDF5FileReader
from .streaming import Stream
import contextlib

class Server:
    """ backend for Optasense application """

    def __init__(self, websocket) -> None:
        self.websocket = websocket
        self.local_files = []
        self.opened_file = None
        self.state = None
        self.stream = Stream(websocket)
        self.file_reader = None
        self.dataset_path_list = []
        self.dataset_name = ""


    def change_properties(self):
        pass

    def find_files_backend(self, path, suffix):
        """ going through files on local machine
            path: location to start search /home/user/Documents
            suffix: look for all files with given suffix
        """
        # self.local_files = ['/Users/jsencak/Documents/bubu.h5', '/Users/jsencak/Documents/sweep_p1intensity_2021-08-31T162239Z.h5', '/Users/jsencak/Documents/file.h5', '/Users/jsencak/Documents/test/sweep_p1intensity_2021-08-31T17_22_39+0100/sweep_p1intensity_2021-08-31T162239Z.h5']

        self.local_files = find_files(path=path, suffix=suffix)
        print(f"Found files {self.local_files}")

    def open_file(self, filename, selected_channels=None):
        """ opening and reading a chosen file """
        self.file_reader = DASHDF5FileReader(filename, self.dataset_name)
        if not self.dataset_name:
            self.dataset_path_list = self.file_reader.get_dataset_paths()
            print(self.dataset_path_list)
            return
        # self.file_reader.read_dataset(self.dataset_name, selected_channels)
        self.stream.generator_init(self.file_reader.filename,
                                   self.dataset_name,
                                   selected_channels)
        self.stream.open_stream()

    def find_h5_files(self, path):
        """ looking for h5 files """
        self.local_files = find_h5_files(path=path)

