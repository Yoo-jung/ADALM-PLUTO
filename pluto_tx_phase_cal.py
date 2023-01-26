import numpy as np
import matplotlib.pyplot as plt
import adi
import time

#----------- __init__ -----------#
samp_rate = 1e6 # Hz
center_freq = 2.4e9 # Hz
num_samps = 32768 # number of samples per call to rx()

#set device
sdr = adi.ad9361(uri="ip:192.168.3.1")
sdr.sample_rate = int(samp_rate)
# Config Tx
sdr.tx_enabled_channels = [0, 1]
sdr.tx_rf_bandwidth = 10000
sdr.tx_lo = int(center_freq)
sdr.tx_hardwaregain_chan0 = -60 # Increase to increase tx power, valid range is -90 to 0 dB
sdr.tx_hardwaregain_chan1 = -60
sdr.tx_cyclic_buffer = True  # Enable cyclic buffers

# Config Rx
sdr.rx_enabled_channels = [0, 1]
sdr.rx_lo = int(center_freq)
sdr.rx_rf_bandwidth = int(samp_rate)
sdr.rx_rf_bandwidth = 10000
sdr.rx_buffer_size = num_samps
sdr.gain_control_mode_chan0 = 'fast_attack'
sdr.gain_control_mode_chan1 = 'fast_attack'

def generate_sig (value):
    fs = int(samp_rate)
    f0 = int(1e3)
    N = 10000  # number of samples to transmit at once
    t = np.arange(N) / samp_rate
    sig0 = 2 ** 14 * 0.5 * np.exp(2.0j*np.pi*f0*t)
    sig1 = 2 ** 14 * 0.5 * np.exp(2.0j*np.pi*f0*t + 1.0j*np.float32(value))

    # Start the transmitter
    sdr.tx([sig0, sig1])  # Send Tx data.
    time.sleep(2)


def hanning (N):
    w = [0]*N
    for m in range(N):
        w[m] = 0.5 * (1 - np.cos(2*np.pi * (m / N)))
    return w

def fft (sig):
    fft_sig = np.fft.fft(sig)
    return fft_sig

def phase_measure(sig0, sig1):
    # remove the DC component of the signals
    sig0 = sig0 - np.mean(sig0)
    sig1 = sig1 - np.mean(sig1)
    # signals length calculation
    len_sig0 = len(sig0)
    len_sig1 = len(sig1)
    # windows generation
    win0 = hanning(len_sig0)
    win1 = hanning(len_sig1)
    # fft
    sig0 = fft(sig0 * win0)
    sig1 = fft(sig1 * win1)
    # fundamental frequency detection
    sig0_max = np.max(abs(sig0))
    sig1_max = np.max(abs(sig1))
    sig0_num = np.where(abs(sig0) == sig0_max)
    sig0_num = sig0_num[0][0]
    sig1_num = np.where(abs(sig1) == sig1_max)
    sig1_num = sig1_num[0][0]
    # phase difference estimation
    phase_difference = np.angle(sig0[sig0_num]) - np.angle(sig1[sig1_num])
    return phase_difference


generate_sig(input('value:'))
set = input('y?:')
while (set == 'y'):
    rx = sdr.rx()
    phase_rad = phase_measure(rx[0], rx[1])
    print("phase difference(rad): ", phase_rad)
    phase_deg = np.rad2deg(phase_rad)
    print("phase difference(deg): ", phase_deg)

    # Plot time domain
    plt.figure(0)
    plt.plot(np.real(rx[0]))
    plt.plot(np.real(rx[1]))
    plt.xlabel("Time")
    plt.show()
    set = input('y?:')
print('down')

# Stop transmitting
sdr.tx_destroy_buffer()
time.sleep(1)