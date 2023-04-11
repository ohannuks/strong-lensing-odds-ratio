all: injectionparameters injections_single_pe

injectionparameters: injections/detectable_lensed_event_parameters_resampled_TLU.txt
injections_single_pe: injections/single_pe_image_1.npz injections/single_pe_image_2.npz injections/single_pe_image_3.npz injections/single_pe_image_4.npz

# Create injection parameters as well as intrinsic parameters for the population
injections/detectable_lensed_event_parameters_resampled_TLU.txt: injections/create_lensed_injections.py
	cd injections && python3 create_lensed_injections.py && touch *.txt
	cd ..

# Create single pe images
injections/single_pe_image_%.npz: injections/create_single_pe_images.py
	cd injections && python3 create_single_pe_images.py
	cd ..

# Clean up
clean:
	rm -f injections/*.txt

# Note: Make sure that LeR and quintet are installed; tested with the 'base' conda environment
