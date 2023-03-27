import os
import subprocess
import h5py
import numpy as np
from re import match
from tqdm import tqdm
from random import randint

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
    def __init__(self, filename) -> None:
        self.filename = filename
        self.opened_file_name = ""
        self.content = []
    
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

    
    def read_dataset(self, dataset_path) -> np.array:
        dataset_path_set = set()
        print("Reading file...")
        with h5py.File(self.filename, 'r+') as fptr:
            print(dataset_path)
            dataset = fptr.get(dataset_path)
            print(dataset)
            # np.array()
            self.content = dataset[:].copy()
            # self.content = dataset[:]
