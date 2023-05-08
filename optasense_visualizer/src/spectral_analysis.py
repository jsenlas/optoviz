import numpy as np
from math import ceil
from tqdm import tqdm

""" taken from https://gitlab.com/optolab/das/data-viewer/-/blob/main/scripts/data-viewer.py """
def spectral_analysis(data: np.array, pulse_rate, fsize=256, shift=128, fmin=100, fmax=1000):
    """Compute the signal power in dB between fmin and fmax frequencies."""
    window = np.hanning(fsize)  # hammingovo okno
    freq = np.fft.fftfreq(fsize, d=1/pulse_rate)  # frequency   diskretny skok

    # indexy do pola 
    ifmin = np.argmax(freq > fmin)
    ifmax = np.argmin(freq < fmax)

    rows, columns = data.shape
    blocks = (rows-fsize)//shift  # pocer blokov 

    # klzave okno 
    print(blocks, rows, fsize, shift)
    tot_pwr = np.zeros((blocks, columns))  # vysledkova matica do ktorej bude zapisovat
    for k in tqdm(range(blocks)):
        data_tmp = data[k*shift:k*shift+fsize, :]  
        data_tmp = (data_tmp.T * window).T  # transpose aby to urobil po stlpcoch vynasobi oknom a potom vratio naspat
        fft_coefs = np.fft.fft(data_tmp, axis=0)  # dostane spektrum pre kazdy kanal
        fft_coefs = fft_coefs[0:fsize//2+1, :]   # vystup fft je komplexne zdruzene pole 256 hodnot, polovicku hodnot zahodi +1 nulova zlozka 
        
        # power spectral density   vuykonostna spektralna hustota
        psd = 1/(pulse_rate*fsize) * np.abs(fft_coefs)**2 # prevod do realnych cisel
        psd[1:ceil(fsize/2)] = 2*psd[1:ceil(fsize/2)]   # zohladnuje zahodenu cas spektra ktora je rovnaka ako ta prva  
        tot_pwr[k, :] = np.sum(psd[ifmin:ifmax, :], axis=0)  # urobi si vysek ktory ho zaujima 

    return 10*np.log10(abs(tot_pwr))  # zobrazuje v logaritmickej skale

""" end inspired code """



# Nacitat knasobok shiftu 