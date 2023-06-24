import numpy as np
import pylab as plt
import corner
import bilby
from helperfunctions import load_all_results, build_kdes
import pandas as pd

# Define the parameters
parameters_15d = np.array(['mass_1', 'mass_2', 'a_1', 'a_2', 'tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'luminosity_distance', 'geocent_time', 'phase', 'theta_jn', 'psi', 'ra', 'dec'], dtype='<U20')
parameters_15d = np.array(['mass_1', 'mass_2', 'a_1', 'a_2', 'tilt_1', 'tilt_2', 'phi_12', 'phi_jl', 'luminosity_distance', 'geocent_time', 'phase', 'theta_jn', 'psi', 'ra', 'dec'], dtype='<U20')

parameters_eff = np.array(['luminosity_distance', 'geocent_time'])

# Define the directories and labels
outdir = 'outdir'
labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
# Load all the results
results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)

# Build the kdes
kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)

# Sample the joint posterior
n_samples = 100000
samples = sample_joint_posterior(kdes_15d, kdes_eff, n_samples)


