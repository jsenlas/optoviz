import h5py
import argparse
import pandas as pd
import numpy as np
import sys
import scipy.io.wavfile


def get_dataset_path(h5_file, path_set, name=""):
    """ Recursion reading keys and creating filepath """
    try:
        h5_file.keys()
    except AttributeError:
        return path_set
    
    tmp_set = set()
    keys = list(h5_file.keys())
    for key in keys:
        path_set.add(f"{name}/{key}")
        tmp_set = get_dataset_path(h5_file[key], path_set, f"{name}/{key}")
    path_set.union(tmp_set)
    return path_set


def read_data(path, dataset) -> np.array:
    dataset_path_set = set()
    with h5py.File(path, 'r+') as f:
        # get path from .h5 file
        dataset_path_set = get_dataset_path(f, dataset_path_set)
        dataset_path_list = sorted(list(dataset_path_set))
        for i in range(len(dataset_path_list)):
            print(f"{i} {dataset_path_list[i]}")
        idx = int(input("Please choose one dataset path [NUM]: "))

        # read the dataset from the file
        dataset = f.get(dataset_path_list[idx])
        if not isinstance(dataset, h5py._hl.dataset.Dataset):
            print("Not a dataset")
            sys.exit(1)
        print("Provided selection is a dataset")
        print(dataset)
        return dataset[:]


def write_wav(path, samples, fs=8192):
    with open(path, 'wb') as f:
        print(samples.max())
        print(type(samples))
        print(samples)

        samples = scipy.signal.resample(samples, int(44100/fs*len(samples)))
        print(samples)
        samples = samples.astype(np.float32)
        print("INFLOAT")
        print(samples)
        # samples = np.interp(samples, (samples.min(), samples.max()), (-1.0, +1.0))
        samples = np.interp(samples, (samples.min(), samples.max()), (0, +(32767 *2 +1)))
        print("AFTER INTERP")
        print(samples)
        scipy.io.wavfile.write(f, 44100, samples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to converting HDF5 container')
    parser.add_argument('-d', '--dataset', help='Define a dataset name')
    parser.add_argument('-o', '--output', help='Specify an output name of audio file')
    parser.add_argument('-fs', '--sampling-rate', type=int, default=8192, dest='fs',
                        help='Specify a sampling rate of captured signal')

    args = parser.parse_args()
    if args.output is None:
        args.output = f"{args.file}.wav"

    print(f'Converting {args.file} to {args.output} [dataset: {args.dataset}].')

    data = read_data(args.file, args.dataset)
    write_wav(args.output, data, fs=args.fs)

    return 0


if __name__ == '__main__':
    sys.exit(main())
