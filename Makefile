all: injectiondata

injectiondata: injections/detectable_lensed_event_parameters_resampled.txt

# Create injections
injections/detectable_lensed_event_parameters_resampled.txt: injections/create_lensed_injections.py
	cd injections && python3 create_lensed_injections.py && touch injections/detectable_lensed_event_parameters_resampled.txt
	cd ..



# Note: Make sure that LeR and quintet are installed; tested with the 'base' conda environment
