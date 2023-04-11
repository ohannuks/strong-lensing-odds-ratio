import numpy as np
import sys

# Check if the user has provided the correct number of arguments
if len(sys.argv) != 4:
    print("Usage: python3 read_injection_data.py <injection_file> <line number> <image number (0 to 3)>")
    print("Example: python3 detectable_lensed_event_parameters_resampled_TLU.txt injection_data.txt 1 0")
    print("Returns m1 m2 chi1 chi2 dist tc phic inc pol ra dec")
    print("Note: The coalescence times, luminosity distances, and phic are the effective coalescence times, luminosity distances, and phics, and we assume the IMRPhenomD waveform.")
    sys.exit(1)

# Read in the injection file
injection_file_name = sys.argv[1]
injection_data = np.genfromtxt(injection_file_name, names=True)
# Read in the line number
line_number = int(sys.argv[2])
# Read in the image number
image_number = int(sys.argv[3])

# Read mass_1, mass_2, a_1, a_2, luminosity_distance, geocent_time, phase, inclination, polarization, right_ascension, and declination
mass_1 = injection_data['mass_1'][line_number]
mass_2 = injection_data['mass_2'][line_number]
a_1 = injection_data['a_1'][line_number]
a_2 = injection_data['a_2'][line_number]
luminosity_distance = injection_data['luminosity_distance'][line_number]
geocent_time = injection_data['geocent_time'][line_number]
phase = injection_data['phase'][line_number]
iota = injection_data['iota'][line_number]
psi = injection_data['psi'][line_number]
ra = injection_data['ra'][line_number]
dec = injection_data['dec'][line_number]

# Get the magnifications, time delays, and image types
magnification = injection_data["magnifications_%d" % image_number][line_number]
time_delay = injection_data["time_delays_%d" % image_number][line_number]
image_type = injection_data["image_types_%d" % image_number][line_number]
# Convert image type to morse phase (see https://arxiv.org/abs/astro-ph/0305055, Eq. )
nj = image_type*0.5
morse_phase = -np.pi*nj
# Get the effective coalescence time, luminosity distance, and phase
# Note that the phase gets modified such that phi_c -> phi_c - pi*nj
effective_geocent_time = geocent_time + time_delay
effective_luminosity_distance = luminosity_distance / np.sqrt(np.abs(magnification))
effective_phase = phase + morse_phase

# Print the injection data
# m1 m2 chi1 chi2 dist tc phic inc pol ra dec
print(mass_1, mass_2, a_1, a_2, effective_luminosity_distance, effective_geocent_time, effective_phase, iota, psi, ra, dec)

