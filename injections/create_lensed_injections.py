import ler
import numpy as np

# Create lensed events with SNR cut-off greater than 8
lensed_statistics = ler.Lensed()
nsamples = int(1e5)
lensed_events = lensed_statistics.create_lensed_images(size=nsamples)

# get the network snr for each event and for each image 
snrs = lensed_events['snrs']['opt_snr_net'] # (num_lensed_events, max_num_images) where max_num_images=5 by default

# Choose only the events which have 4 or more images and they are all detectable
snr_cut = 8
n_images = lensed_events['n_images'] # (num_lensed_events,)
idx = np.where((n_images >= 4) & (snrs[:, 0] > snr_cut) & (snrs[:, 1] > snr_cut) & (snrs[:, 2] > snr_cut) & (snrs[:, 3] > snr_cut))[0]

# Save the events
# Get the magnifications and time delays
mu = lensed_events['magnifications'][idx]
mu0, mu1, mu2, mu3 = mu[:, 0], mu[:, 1], mu[:, 2], mu[:, 3]
td = lensed_events['time_delays'][idx]
td0, td1, td2, td3 = td[:, 0], td[:, 1], td[:, 2], td[:, 3]
# Get the binary black hole parameters 
gw_parameters = lensed_events['gw_param']
variable_names = gw_parameters.keys()

# Save the events
np.savez('lensed_events.npz', idx=idx, mu0=mu0, mu1=mu1, mu2=mu2, mu3=mu3, td0=td0, td1=td1, td2=td2, td3=td3, **{key: gw_parameters[key][idx] for key in variable_names})

# Now load the events for testing 
data = np.load('lensed_events.npz')
idx = data['idx']
mu0, mu1, mu2, mu3 = data['mu0'], data['mu1'], data['mu2'], data['mu3']
td0, td1, td2, td3 = data['td0'], data['td1'], data['td2'], data['td3']
gw_parameters = {key: data[key] for key in data.keys() if key not in ['idx', 'mu0', 'mu1', 'mu2', 'mu3', 'td0', 'td1', 'td2', 'td3']}

# Now save the events as a txt file, including all of the binary black hole parameters
labels = ['idx', 'mu0', 'mu1', 'mu2', 'mu3', 'td0', 'td1', 'td2', 'td3'] + list(gw_parameters.keys())
np.savetxt('lensed_events.txt', np.array([idx, mu0, mu1, mu2, mu3, td0, td1, td2, td3] + list(gw_parameters.values())).T, header=' '.join(labels))





