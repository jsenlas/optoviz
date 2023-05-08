import h5py
import logging
import numpy as np
import argparse
import json
from datetime import datetime as dt
from scipy import signal
import matplotlib.pyplot as plt
from math import ceil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DECIMATE = 100
# Let's say ... it is not here
# This global var is not the var you are looking for !!!
mouse_click = False


def stamp2date(time: h5py.Dataset):
    return list(map(dt.fromtimestamp, time[:] / 1e6))


def rolling_sub(data: np.array, stride=100):
    for i in range(int(data.shape[0] / stride)):
        data[i * stride + 1:, :] -= data[i * stride, :]
    return data


def sobel(data: np.array, kernel_size=5) -> np.array:
    """Perform vertical edge detection using the convolution with the Sobel operator."""
    if kernel_size == 3:
        sobel_kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    elif kernel_size == 4:
        sobel_kernel = np.array([[-1, -2, -2, -1], [-2, -5, -5, -2], [2, 5, 5, 2], [1, 2, 2, 1]])
    elif kernel_size == 5:
        sobel_kernel = np.array([[2, 3, 6, 3, 2], [3, 4, 6, 4, 3], [0, 0, 0, 0, 0], [-3, -4, -6, -4, -3], [-2, -3, -6, -3, -2]])
    else:
        logger.error("Invalid kernel size for sobel operator.")
        raise ValueError("Invalid kernel size for sobel operator.")

    return signal.convolve2d(data, sobel_kernel, boundary='symm', mode='same')


def spectral_analysis(data: np.array, pulse_rate, fsize=256, shift=128, fmin=100, fmax=1000):
    """Compute the signal power in dB between fmin and fmax frequencies."""
    window = np.hanning(fsize)
    freq = np.fft.fftfreq(fsize, d=1/pulse_rate)

    ifmin = np.argmax(freq > fmin)
    ifmax = np.argmin(freq < fmax)

    rows, columns = data.shape
    blocks = (rows-fsize)//shift

    tot_pwr = np.zeros((blocks, columns))
    for k in range(blocks):
        data_tmp = data[k*shift:k*shift+fsize, :]
        data_tmp = (data_tmp.T * window).T
        fft_coefs = np.fft.fft(data_tmp, axis=0)
        fft_coefs = fft_coefs[0:fsize//2+1, :]
        psd = 1/(pulse_rate*fsize) * np.abs(fft_coefs)**2
        psd[1:ceil(fsize/2)] = 2*psd[1:ceil(fsize/2)]
        tot_pwr[k, :] = np.sum(psd[ifmin:ifmax, :], axis=0)

    return 10*np.log10(abs(tot_pwr))


def parse_data(path: str) -> np.array:
    with h5py.File(path) as f:
        logger.debug(f'All groups in dataset: {f.keys()}')
        grp = f['Acquisition']
        logger.debug(f'All groups in subgroup: {grp.keys()}')
        logger.info('Reading Acquisition/Raw[0]/RawData+RawDataTimestemp')

        data = grp['Raw[0]']['RawData']
        # time = grp['Raw[0]']['RawDataTime']
        # time = stamp2date(time)
        # print(time)
        pulse_rate = grp.attrs['PulseRate']

        # ipdb.set_trace()
        data = np.array(data, dtype=np.float64)
        # data = data[100000: 350000, 150:350]
        # data = np.abs(data)
        # data = np.power(data, 2) + 0.1
        # data -= data[0, :]
        # data = rolling_sub(data, stride=1000)
        # data = np.diff(data, axis=0)
        # data -= np.median(data, axis=0)
        # data = np.abs(data) + 0.1
        # data = np.log(data)
        # data = sobel(data, 3)
        # data = data[::DECIMATE, :]
        data = spectral_analysis(data, pulse_rate)

        return data


def plot_data(data: np.array):
    x_points = []
    y_points = []
    curves = []

    def on_click(event):
        global mouse_click
        mouse_click = True

    def off_click(event):
        global mouse_click
        mouse_click = False
        x_points.append(x_points[0])
        y_points.append(y_points[0])
        ax.plot(x_points, y_points, color='red')
        curves.append((x_points.copy(), y_points.copy()))
        x_points.clear()
        y_points.clear()
        fig.canvas.draw()
        fig.canvas.flush_events()

    def mouse_move(event):
        global mouse_click
        if mouse_click and event.inaxes:
            x_points.append(event.xdata)
            y_points.append(event.ydata)

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111)

    # line = ax.pcolormesh(data)
    line = ax.pcolormesh(
        data,
        #vmin=np.quantile(data, 0.05),
        #vmax=np.quantile(data, 0.95),
    )
    plt.colorbar(line)

    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('button_release_event', off_click)
    fig.canvas.mpl_connect('motion_notify_event', mouse_move)

    plt.show()

    return curves


def store_labels(path, curves, shape):
    data = {}
    data['shape'] = shape

    for i, (x, y) in enumerate(curves):
        data[f'curve{i}'] = {
            'x': x,
            'y': y,
            'decimate': DECIMATE,
        }
    with open(path, 'w') as f:
        json.dump(data, f)

    # with h5py.File(path+'test.hdf5', 'a'):
    #     pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help='Specify a file path to the dataset.')
    args = parser.parse_args()

    data = parse_data(args.dataset)
    curves = plot_data(data)
    label_path = args.dataset[:args.dataset.rfind('.')]
    store_labels(label_path + '.json', curves, data.shape)


if __name__ == '__main__':
    main()
