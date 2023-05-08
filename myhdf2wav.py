import h5py
import argparse
import numpy as np
import sys
import scipy.io.wavfile


def get_dataset_path(h5_file, path_set, name="") -> set:
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


def read_data(path, dataset_path) -> np.array:
    dataset_path_set = set()
    with h5py.File(path, 'r+') as f:
        
        if dataset_path is None:
            # get path from .h5 file
            dataset_path_set = get_dataset_path(f, dataset_path_set)
            dataset_path_list = sorted(list(dataset_path_set))
            for i in range(len(dataset_path_list)):
                print(f"{i} {dataset_path_list[i]}")
            idx = int(input("Please choose one dataset path [NUM]: "))
            # read the dataset from the file
            dataset = f.get(dataset_path_list[idx])
        else:
            dataset = f.get(dataset_path)
        if not isinstance(dataset, h5py._hl.dataset.Dataset):
            print("Not a dataset")
            sys.exit(1)
        print("Provided selection is a dataset")
        print(dataset)
        return dataset[:]


def write_wav(path, samples, fs=8192):
    with open(path, 'wb') as f:
        # samples = samples[1,:]
        print(samples.min())
        print(samples.max())
        # samples = np.interp(samples, (samples.min(), samples.max()), (-1.0, +1.0))
        samples = np.interp(samples, (samples.min(), samples.max()), (-32768, +32767))
        print(samples.min())
        print(samples.max())
        print(samples.shape)
        samples = scipy.signal.resample(samples, int(44100/fs*len(samples)))
        print(samples.shape)
        
        print(samples)
        # scipy.io.wavfile.write(f, 44100, samples.astype(np.int16))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to converting HDF5 container')
    parser.add_argument('-d', '--dataset', help='Define a dataset name')
    parser.add_argument('-o', '--output', help='Specify an output name of audio file')
    parser.add_argument('-a', '--all', action='store_true', help='Export all channels to WAV.')
    parser.add_argument('-c', '--channel', action="store", type=int, default=1, help="Choose one channel, is equivalent to km")
    parser.add_argument('-fs', '--sampling-rate', type=int, default=8192, dest='fs',
                        help='Specify a sampling rate of captured signal')

    args = parser.parse_args()
    if args.output is None:
        args.output = f"{args.file}.wav"

    print(f'Converting {args.file} to {args.output} [dataset: {args.dataset}].')
 
    data = read_data(args.file, args.dataset)
    print(data.max(), data.min())
    if args.all:
        for i in range(data.shape[0]):
            args.output = f"sweep{i}.wav"
            write_wav(args.output, data[i,:], fs=args.fs)
    elif args.channel:
        write_wav(args.output, data[args.channel,:], fs=args.fs)
    return 0


if __name__ == '__main__':
    sys.exit(main())
