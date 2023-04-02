import ler
import pylab as plt
import numpy as np
import pickle
import corner
import importlib
from quintet import Quintet
importlib.reload(ler)
import bilby.core.utils as utils
import ler.helperroutines as hr
from corner import corner
import os

utils.logger.disabled = True # Disable bilby logger

np.random.seed(1234) # for reproducibility

# Check if 'quintet_object.pkl' file exists
if os.path.isfile('quintet_object.pkl'):
    with open('quintet_object.pkl', 'rb') as f:
        quintet_object = pickle.load(f)
else:
    quintet_object = Quintet(waveform_approximant="IMRPhenomD")
    with open('quintet_object.pkl', 'wb') as f:
        pickle.dump(quintet_object, f)
# Create galaxy source population
galaxy_source_population = ler.SourceGalaxyPopulationHaris2018SDSS()
# Plot out the galaxy source redshift distribution
galaxy_source_population.plot_source_redshift_distribution()
# Create a bbh source population
cbc_source_population = ler.BBHPopulationO3(galaxy_source_population)
# Create a galaxy lens population
galaxy_lens_population = ler.LensGalaxyPopulationHaris2018SDSS(galaxy_source_population)
# Create the unlensed population
unlensed_bbh_statistics = ler.UnlensedCBCStatistics(cbc_source_population, quintet_object=quintet_object)
# Create the lensed population
lensed_bbh_statistics = ler.LensedCBCStatistics(galaxy_source_population, cbc_source_population, galaxy_lens_population, quintet_object=quintet_object)

print("Rate of lensing is", lensed_bbh_statistics.rate_detectable())
print("Rate of unlensing is", unlensed_bbh_statistics.rate_detectable())


# Sample the detectable, lensed BBH events with 4 images that all have snr above 8
nevents = 1000
n_images = 4
snr_threshold = 8
# Check if 'detectable_lensed_event_parameters.txt' exists
if os.path.isfile('detectable_lensed_event_parameters.txt'):
    # If it does, load the file
    detectable_lensed_event_parameters = hr.load_dictionary_from_numpy_txt_file('detectable_lensed_event_parameters.txt')
else:
    detectable_lensed_event_parameters = lensed_bbh_statistics.sample_detectable_events(nevents, n_images, snr_threshold)
    hr.save_dictionary_to_numpy_txt_file(detectable_lensed_event_parameters, fname= 'detectable_lensed_event_parameters.txt' ) # Save the detectable lensed event parameters dictionary as numpy txt file

# Check if 'lensed_event_parameters.txt' exists
if os.path.isfile('lensed_event_parameters.txt'):
    lensed_event_parameters = hr.load_dictionary_from_numpy_txt_file('lensed_event_parameters.txt')
else:
    # sample lensed bbh events with 4 images that do not have an snr cut
    lensed_event_parameters = lensed_bbh_statistics.sample_events(nevents, n_images=4, npool=20) # returns dictionary with parameter names
    # Save the intrinsic lensed event parameters dictionary as numpy txt file
    hr.save_dictionary_to_numpy_txt_file(lensed_event_parameters, fname= 'lensed_event_parameters.txt' )

# Load the detectable lensed event parameters dictionary
data = np.genfromtxt('detectable_lensed_event_parameters.txt', names=True)
names = data.dtype.names
# Load the intrinsic lensed event parameters dictionary
data_intrinsic = np.genfromtxt('lensed_event_parameters.txt', names=True)
names_intrinsic = data_intrinsic.dtype.names
# Load the weights
weights = data['weights']
weights_intrinsic = data_intrinsic['weights']

# Check if 'detectable_lensed_event_parameters_resampled.txt' exists
if os.path.isfile('detectable_lensed_event_parameters_resampled.txt'):
    detectable_lensed_event_parameters_resampled = hr.load_dictionary_from_numpy_txt_file('detectable_lensed_event_parameters_resampled.txt')
else:
    # Resample the detectable lensed event parameters with equal weights and save parameters dictionary as numpy txt file
    detectable_lensed_event_parameters_resampled = hr.resample_dictionary(detectable_lensed_event_parameters, weights, nevents=50)
    detectable_lensed_event_parameters_resampled['weights']=np.ones(len(detectable_lensed_event_parameters_resampled['weights']))
    hr.save_dictionary_to_numpy_txt_file(detectable_lensed_event_parameters_resampled, fname= 'detectable_lensed_event_parameters_resampled.txt' )

# Check if 'lensed_event_parameters_resampled.txt' exists
if os.path.isfile('lensed_event_parameters_resampled.txt'):
    lensed_event_parameters_resampled = hr.load_dictionary_from_numpy_txt_file('lensed_event_parameters_resampled.txt')
else:
    lensed_event_parameters_resampled = hr.resample_dictionary(lensed_event_parameters, weights_intrinsic, nevents=50)
    lensed_event_parameters_resampled['weights']=np.ones(len(lensed_event_parameters_resampled['weights']))
    hr.save_dictionary_to_numpy_txt_file(lensed_event_parameters_resampled, fname= 'lensed_event_parameters_resampled.txt' )

# Compute the rate of lensing
rate_of_lensing, _ = lensed_bbh_statistics.rate_detectable(zs=False,size=10000,ndraws=20, n_images=4, model_pars_gwcosmo = False, use_pdet = False)
rate_of_not_lensed, _ = unlensed_bbh_statistics.rate_detectable(size=10000)

# Compute TLU for quads for detectable lensed event parameters resampled
tlu = lensed_bbh_statistics.TLU(detectable_lensed_event_parameters_resampled)
# Add the TLU to the dictionary
detectable_lensed_event_parameters_resampled['tlu'] = tlu
# Compute TLU for quads for intrinsic lensed event parameters resampled
tlu = lensed_bbh_statistics.TLU(lensed_event_parameters_resampled)
# Add the TLU to the dictionary
lensed_event_parameters_resampled['tlu'] = tlu
# Compute TLU for quads for detectable lensed event parameters
tlu = lensed_bbh_statistics.TLU(detectable_lensed_event_parameters)
# Add the TLU to the dictionary
detectable_lensed_event_parameters['tlu'] = tlu
# Compute TLU for quads for intrinsic lensed event parameters
tlu = lensed_bbh_statistics.TLU(lensed_event_parameters)
# Add the TLU to the dictionary
lensed_event_parameters['tlu'] = tlu

# Save the updated dictionaries
hr.save_dictionary_to_numpy_txt_file(detectable_lensed_event_parameters, fname= 'detectable_lensed_event_parameters_TLU.txt' )
hr.save_dictionary_to_numpy_txt_file(lensed_event_parameters, fname= 'lensed_event_parameters_TLU.txt' )
hr.save_dictionary_to_numpy_txt_file(detectable_lensed_event_parameters_resampled, fname= 'detectable_lensed_event_parameters_resampled_TLU.txt' )
hr.save_dictionary_to_numpy_txt_file(lensed_event_parameters_resampled, fname= 'lensed_event_parameters_resampled_TLU.txt' )

# Create a directory for the figures
if not os.path.exists('figures'):
    os.makedirs('figures')
# Plot out the zl and zs distributions
plt.figure()
plt.hist(data['zl'], bins=20, histtype='step', label='zl', density=True, weights=weights)
plt.hist(data['zs'], bins=20, histtype='step', label='zs', density=True, weights=weights)
plt.legend()
plt.xlabel('Redshift')
plt.ylabel('Number of events')
plt.savefig('figures/zl_zs_distributions.pdf', bbox_inches='tight')
plt.close()

# Plot out the x0, x1 image positions for each image as a corner plot
for i in range(4):
    labels = [r'$x_0\,[\theta_E]$', r'$x_1\,[\theta_E]$']
    data_cornerplot = np.array([data['x0_image_positions_' + str(i)], data['x1_image_positions_' + str(i)]]).T
    corner(data_cornerplot, labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, weights=weights)
    plt.legend()
    plt.savefig('figures/x0_x1_image_positions_' + str(i) + '_cornerplot.pdf', bbox_inches='tight')
    plt.close()
# Plot out the source positions

# Similarly, plot out the magnifications
labels = [r'$\log_{10} |\mu_0|$', r'$\log_{10} |\mu_1|$', r'$\log_{10} |\mu_2|$', r'$\log_{10} |\mu_3|$']
keys = ['magnifications_0', 'magnifications_1', 'magnifications_2', 'magnifications_3']
data_cornerplot = np.array([data[key] for key in keys]).T
corner(np.log10(np.abs(data_cornerplot)), labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, weights=weights)
plt.savefig('figures/magnifications_cornerplot.pdf', bbox_inches='tight')
plt.close()
# And the signal-to-noise ratios for each image
labels = [r'$\log_{10} \mathrm{SNR}_0$', r'$\log_{10} \mathrm{SNR}_1$', r'$\log_{10} \mathrm{SNR}_2$', r'$\log_{10} \mathrm{SNR}_3$']
keys = ['snr_opt_snr_net_0', 'snr_opt_snr_net_1', 'snr_opt_snr_net_2', 'snr_opt_snr_net_3']
data_cornerplot = np.array([data[key] for key in keys]).T
corner(np.log10(data_cornerplot), labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, weights=weights)
plt.savefig('figures/snr_cornerplot.pdf', bbox_inches='tight')
plt.close()
# And then the time delay differences
labels = [r'$\log_{10} \Delta t_1$ [day]', r'$\log_{10} \Delta t_2$ [day]', r'$\log_{10} \Delta t_3$ [day]']
keys = ['time_delays_1', 'time_delays_2', 'time_delays_3']
seconds_to_months = 1/60/60/24/30
data_cornerplot = np.array([data[key] - data['time_delays_0'] for key in keys]).T * seconds_to_months
corner(np.log10(data_cornerplot), labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, weights=weights)
# 
plt.savefig('figures/time_delay_differences_cornerplot.pdf', bbox_inches='tight')
plt.close()

# Plot all of the lens parameters
keys = ['theta_E', 'e1', 'e2', 'gamma', 'gamma1', 'gamma2', 'q']
labels = [r'$\theta_E$', r'$e_1$', r'$e_2$', r'$\gamma$', r'$\gamma_1$', r'$\gamma_2$', r'$q$']
data_cornerplot = np.array([data[key] for key in keys]).T
corner(data_cornerplot, labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, weights=weights)
plt.savefig('figures/lens_parameters_cornerplot.pdf', bbox_inches='tight')
plt.close()

# Plot all of the detectable lensed event parameters against the intrinsic lensed event parameters
data_corner_intrinsic = np.array([data_intrinsic[key] for key in keys]).T
data_corner_detectable = np.array([data[key] for key in keys]).T
fig = corner(data_corner_intrinsic, labels=labels, show_titles=True, title_kwargs={"fontsize": 12}, color='b', hist_kwargs={'alpha': 0.5}, weights=weights_intrinsic)
corner(data_corner_detectable, fig=fig, color='r', hist_kwargs={'alpha': 0.5}, weights=weights)
plt.savefig('figures/detectable_lensed_event_parameters_cornerplot.pdf', bbox_inches='tight')
plt.close()

