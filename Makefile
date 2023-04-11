all: injectionparameters injections_single_pe

injectionparameters: injections/detectable_lensed_event_parameters_resampled_TLU.txt
injections_single_pe: injections/outdir/pm_injection_1_image_0 injections/outdir/pm_injection_1_image_1 injections/outdir/pm_injection_1_image_2 injections/outdir/pm_injection_1_image_3

# Create injection parameters as well as intrinsic parameters for the population
injections/detectable_lensed_event_parameters_resampled_TLU.txt: injections/create_lensed_injections.py
	cd injections && python3 create_lensed_injections.py && touch *.txt
	cd ..

# Create single pe images
injections/outdir/pm_injection_1_image_0: injections/inject_data injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data 1 0
	cd ..
injections/outdir/pm_injection_1_image_1: injections/inject_data injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data 1 1
	cd ..
injections/outdir/pm_injection_1_image_2: injections/inject_data injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data 1 2
	cd ..
injections/outdir/pm_injection_1_image_3: injections/inject_data injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data 1 3
	cd ..

# Clean up
clean:
	rm -f injections/*.txt

# Note: Make sure that LeR and quintet are installed; tested with the 'base' conda environment
