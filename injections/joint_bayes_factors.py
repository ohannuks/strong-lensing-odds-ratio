import numpy as np
import pylab as plt
import corner
import helperfunctions as hf
import importlib
# Reload the helperfunctions module
importlib.reload(hf)

# import load_all_results, build_kdes, build_kde, joint_kde_analysis


# Define the parameters
parameters_15d = np.array(['mass_1', 'mass_2', 'a_1', 'a_2', 'tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'luminosity_distance', 'geocent_time', 'phase', 'theta_jn', 'psi', 'ra', 'dec'], dtype='<U20')
parameters_15d = np.array(['mass_1', 'mass_2', 'a_1', 'a_2', 'tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'luminosity_distance', 'geocent_time', 'phase', 'theta_jn', 'psi', 'ra', 'dec'], dtype='<U20')

parameters_eff = np.array(['luminosity_distance', 'geocent_time'])

# Define the directories and labels
outdir = 'outdir'
labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
# Load all the results
results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = hf.load_all_results(outdir, labels)

# Build the kdes
kdes_15d, kdes_eff = hf.build_kdes(posteriors, parameters_15d, parameters_eff)

# Sample the joint posterior
n_samples = 10000 
joint_kde, samples_all, log_weights_all = hf.joint_kde_analysis(kdes_15d, kdes_eff, priors, parameters_15d, parameters_eff, n_samples=n_samples) 










