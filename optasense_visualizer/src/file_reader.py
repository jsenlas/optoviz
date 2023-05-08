import os
import subprocess
import h5py
import numpy as np
from json import dumps
from re import match
from tqdm import tqdm
import datetime
from random import randint
from asyncio import Event, create_task, wait, sleep
from .range_parser import parse_channel_range
from .spectral_analysis import spectral_analysis
from tempfile import NamedTemporaryFile

def find_h5_files(path="."):
    return find_files(path=path, suffix=".h5")


def find_files(path=".", suffix=""):
    result = []
    if os.path.isdir(path):
        print(f"Searching for {suffix} files...")
        for root, _, files in tqdm(os.walk(path), total=100000):
            result.extend(
                os.path.join(root, file_name)
                for file_name in files
                if match(f".*{suffix}$", file_name)
            )
    else:
        print(f"Given path '{path}' is not a directory")
    return result


def run(cmd, strout=False, hide_stdout=False, nosplit=False, shell=False, check=False, quiet=False):
    """ run terminal command """
    # WHY split()
    # command should be in a list,
    # also there is a chance that terminal will think that the provided string is a file
    # (when separated no problem occurs)
    if not shell and not isinstance(cmd, list) and not nosplit:
        cmd = cmd.split(" ")

    if not quiet:
        print("RUNNING:", cmd)

    if strout:
        ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)
        ret_str = ret.stdout.decode().rstrip()
        print(ret_str)
        return ret_str
    if hide_stdout:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)
    return subprocess.run(cmd, shell=shell, check=check)


def find_h5_files(path=".", suffix=""):
    """ Looking for all .h5 files"""
    if not suffix:
        print("No suffix specified.")
        return []
    
    return run(
        f'/usr/bin/find {path} -type f -name {suffix}',
        strout=True
    ).splitlines()


def find_h5_files(path=".", suffix="*.h5"):
    """ Looking for all .h5 files"""
    return run(
        f'/usr/bin/find {path} -type f -name {suffix}',
        strout=True
    ).splitlines()

class Buffer:
    def __init__(self, x=100, y=100) -> None:
        self.x = x
        self.y = y
        self._buffer = []
    
    def generate_content(self):
        return [[randint(0, 1000) for _ in range(self.x)] for _ in range(self.y)]


class EOFException(Exception):
    pass


class NotDatasetError(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        print(message)


class DASHDF5FileReader:
    def __init__(self, filename, datasetname) -> None:
        self.filename = filename
        self.dataset_path = datasetname
        self.opened_file_name = ""
        self.min = 0
        self.max = 1000
        self.content = []
        self.DECIMATE = 8
        self.processed_file_name = f"{self.filename}.npy"
        self.pulse_rate = 1000
        # self.__delete_tmp_file()
    
    def __delete_tmp_file(self):
        try:
            os.remove(self.processed_file_name)
        except Exception as exc:
            print(exc)

    def _get_dataset_path(self, h5_file, path_set, name="") -> set:
        """ Recursion reading keys and creating filepath """
        try:
            h5_file.keys()
        except AttributeError:
            return path_set
        
        tmp_set = set()
        keys = list(h5_file.keys())
        for key in keys:
            path_set.add(f"{name}/{key}")
            tmp_set = self._get_dataset_path(h5_file[key], path_set, f"{name}/{key}")
        path_set.union(tmp_set)
        return path_set

    def get_dataset_paths(self):
        dataset_path_set = set()
        with h5py.File(self.filename, 'r+') as f:
            # get path from .h5 file
            dataset_path_set = self._get_dataset_path(f, dataset_path_set)

            return [dataset for dataset in dataset_path_set
                    if isinstance(f.get(dataset), h5py._hl.dataset.Dataset)]

    # def read_dataset(self, dataset_path, selected_channels_str) -> np.array:
    #     self._create_task()
    #     with h5py.File(self.filename, 'r+') as fptr:
    #         print(dataset_path)
    #         dataset_reference = fptr.get(dataset_path)  # this does not read the whole file
    #         if not isinstance(dataset_reference, h5py._hl.dataset.Dataset):
    #             raise NotDatasetError("Not a dataset")


    # def read_dataset_old(self, dataset_path, selected_channels_str) -> np.array:
    #     if selected_channels_str:
    #         selected_channels = parse_channel_range(selected_channels_str)

    #     dataset_path_set = set()
    #     print("Reading file...")
    #     with h5py.File(self.filename, 'r+') as fptr:
    #         print(dataset_path)
    #         dataset = fptr.get(dataset_path)
    #         print(dataset)
    #         # np.array()
    #         self.min = np.min(dataset)
    #         self.max = np.max(dataset)
    #         if selected_channels_str:
    #             data = dataset[:, selected_channels].copy()
    #         else:
    #             data = dataset[:].copy()
    #         data = np.array(data, dtype=np.float64)
    #         data -= np.median(data, axis=0)
    #         print("BEFORE DECIMATE")
    #         print(len(data))
    #         data = data[:self.DECIMATE,:]
    #         print("AFTER DECIMATE")
    #         self.content = data.copy()
    #         print(len(self.content))
    #         # self.content = dataset[:]

    def dataset_reading_generator(self, read_all=False):
        with h5py.File(self.filename, 'r+') as fptr:
            dataset = fptr.get(self.dataset_path)
            chunk_size = 65536
            
            self.pulse_rate = fptr['Acquisition'].attrs['PulseRate']

            # print("SPAHE", dataset.shape)
            # data = dataset[:65536, :]
            # print("after decimate", data.shape)
            # yield data
            
            # self.dataset_min = np.min(dataset)
            # self.dataset_max = np.max(dataset)
            # print("MM", self.dataset_min, self.dataset_max)
            if read_all:
                yield dataset
            else:
                for i in tqdm(range(0, dataset.shape[0], chunk_size)):
                    data = dataset[i: i+chunk_size, :]

                    print("raw reading", data.shape)
                    # data = data[:self.DECIMATE,:]    #read every Xth value
                    print("after decimate", data.shape)
                    yield data

    def preprocess(self):
        if os.path.isfile(self.processed_file_name):
            print("The preprocessed file already exists.\nSkipping the preprocess stage...")
            return
        nnnn = ""
        outdata = np.array([])
        for data in self.dataset_reading_generator(read_all=True):
            print("PREPROCESS", data)
            print("PREPROCESS", data.shape)
            outdata = spectral_analysis(data, self.pulse_rate)
            print("PROCESSING DONE", outdata.shape)
            # print(out.dtype)
            # print(type(out))
            # outdata = np.array(outdata, out)
            
            # # working
            # outdata = np.array(data, dtype=np.float64)
            # # outdata = outdata[:self.DECIMATE,:]
            # outdata -= np.median(outdata, axis=0)
            
            # self.min = np.min(outdata)
            # self.max = np.max(outdata)
            
            # outdata = np.interp(outdata, (self.min, self.max), (0,1000))
            # outdata = np.rint(outdata)

            # print("OUTDATA", outdata)
            # print(outdata.shape)
            # # working
        # with open(self.processed_file_name, 'wb') as fp:
        print(f"Saving preprocessed file into {self.processed_file_name}")
        np.save(self.processed_file_name, outdata)
        # print("FILESIZE", os.stat(fp.name).st_size)

    # async def read_preprocessed_file

    async def read_dataset_v2(self):
        print("Reading preprocessed file...")
        with open(self.processed_file_name, "rb") as fp:
            print("NP load")
            try:
                all_data = np.load(fp)
            except Exception as exc:
                print(exc)

            self.min = np.min(all_data)
            self.max = np.max(all_data)

            print("NP loaded")
            print("SHAPE", all_data.shape)
            all_data = np.interp(all_data, (self.min, self.max), (0,1000))
            all_data = np.rint(all_data)
            yield dumps({
                "type": "properties",
                "min": 0,
                "max": 1000,
                "number_of_channels": all_data.shape[1],
                "number_of_rows": all_data.shape[0]
            })
            for data in all_data:
                yield dumps({
                    "type" : "data",
                    "data" : data.tolist(),
                })

    async def read_dataset(self, dataset_path, selected_channels_str):
        if selected_channels_str:
            selected_channels = parse_channel_range(selected_channels_str)
        dataset_path_set = set()
        print("Reading file...")
        with h5py.File(self.filename, 'r+') as fptr:
            # print(dataset_path)
            dataset = fptr.get(dataset_path)
            print(dataset)
            # np.array()
            # self.min = np.min(dataset)
            # self.max = np.max(dataset)
            chunk_size = 4096
            print("SPAHE", dataset.shape)
            # print("MM", np.min(dataset), np.max(dataset))
            for i in range(0, dataset.shape[0], chunk_size):
                data = dataset[i: i+chunk_size, :]
                print("Shape", data.shape)
                print("LEN", len(data))
                
                # data = spectral_analysis(data=data, pulse_rate=1024)
                # print("After analysis:", data)
                
                data = np.array(data, dtype=np.float64)
                data = data[:self.DECIMATE,:]
                data -= np.median(data, axis=0)
                data = np.interp(data, (np.min(dataset), np.max(dataset)), (0,1000))
                data = np.rint(data)
                ######data = np.array(data, dtype=np.int32)
                
                print("BEFORE DECIMATE")
                print(len(data))
                print(data)

                print("EDIT", data)
                yield dumps({
                    "type" : "data",
                    "data" : data.tolist()
                })
