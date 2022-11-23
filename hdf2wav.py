import h5py
import argparse
import numpy as np
import sys
import scipy.io.wavfile


def read_data(path, dataset) -> np.array:
    with h5py.File(path, 'r+') as f:
        if dataset is None:
            dataset = list(f.keys())[0]
        return f[dataset][:]


def write_wav(path, samples, fs=8192):
    with open(path, 'wb') as f:
        samples = scipy.signal.resample(samples, int(44100/fs*len(samples)))
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
        args.output = args.file + '.wav'

    print(f'Converting {args.file} to {args.output} [dataset: {args.dataset}].')

    data = read_data(args.file, args.dataset)
    write_wav(args.output, data, args.fs)

    return 0


if __name__ == '__main__':
    sys.exit(main())
