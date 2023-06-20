all: injectionparameters injections_single_pe injection_multi_pe

injectionparameters: injections/detectable_lensed_event_parameters_resampled_TLU.txt
injection_multi_pe: injections/outdir/pm_injection_1_multiimage/summary.txt
injections_single_pe: injections/outdir/pm_injection_1_image_0/summary.txt injections/outdir/pm_injection_1_image_1/summary.txt injections/outdir/pm_injection_1_image_2/summary.txt injections/outdir/pm_injection_1_image_3/summary.txt 

# Create injection parameters as well as intrinsic parameters for the population
injections/detectable_lensed_event_parameters_resampled_TLU.txt: injections/create_lensed_injections.py
	cd injections && python3 create_lensed_injections.py && touch *.txt
	cd ..

# Create single pe images
injections/outdir/pm_injection_1_image_0/summary.txt: injections/inject_data.sh injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data.sh 1 0
	cd ..
injections/outdir/pm_injection_1_image_1/summary.txt: injections/inject_data.sh injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data.sh 1 1
	cd ..
injections/outdir/pm_injection_1_image_2/summary.txt: injections/inject_data.sh injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data.sh 1 2
	cd ..
injections/outdir/pm_injection_1_image_3/summary.txt: injections/inject_data.sh injections/detectable_lensed_event_parameters_resampled_TLU.txt
	cd injections && ./inject_data.sh 1 3
	cd ..

# Now run the multi-image analysis. It should take as input the injection number, and run the golum analysis on all 4 images
injections/outdir/pm_injection_1_multiimage/summary.txt: injections/inject_multiimage_data.sh injections/outdir/pm_injection_1_image_0/summary.txt injections/outdir/pm_injection_1_image_1/summary.txt injections/outdir/pm_injection_1_image_2/summary.txt injections/outdir/pm_injection_1_image_3/summary.txt
	cd injections && ./inject_multiimage_data.sh 1
	cd ..

# Clean up
clean:
	rm -f injections/*.txt

# Note: Make sure that LeR and quintet are installed; tested with the 'base' conda environment
