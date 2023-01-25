import ler
import numpy as np
# Create lensed events with SNR cut-off greater than 8
lensed_statistics = ler.Lensed()
nsamples = 100000
lensed_events = lensed_statistics.create_lensed_images(size=nsamples)
# Only choose the events with SNR greater than 8
# Get the network snr of each 4 images for each lensed event
snrs = lensed_events['network_snr'] # (4, ndim) shape
# Select the indices where each of the four images has SNR greater than 8
snr_cut = 8
indices = np.where(np.all(snrs > snr_cut, axis=0))[0]
# Select the events with SNR greater than 8
lensed_events = lensed_events[indices]



